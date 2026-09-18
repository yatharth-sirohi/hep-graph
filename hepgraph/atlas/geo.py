"""Geodesy and GeoJSON geometry for the HEP Atlas local-map layer (A25).

`docs/HEP_ATLAS_GEOMETRY.md` is the contract; this module is the *measuring*
half of it.  Every function here is pure: it takes GeoJSON-shaped data (RFC
7946 ``[lon, lat]`` positions in WGS 84) and returns numbers or a list of
problem strings.  Nothing reads a file, nothing imports outside the standard
library, and nothing here knows what an atlas record looks like — the
validator and the build own that.

Two conventions the rest of the layer depends on:

* **Positions are ``[lon, lat]``** (GeoJSON order), while the distance
  primitive :func:`hepgraph.atlas.schema.great_circle_m` takes
  ``(lat, lon)`` (the order the globe layer already used).  Every function in
  this module speaks GeoJSON order and flips the arguments itself, so a caller
  never has to remember which convention it is in.
* **The Earth is the WGS 84 mean sphere** of radius
  ``schema.EARTH_RADIUS_M`` (6 371 008.8 m), for lengths *and* for areas.  A
  local map spans at most 60 km, where the sphere/ellipsoid difference is a
  few parts in 10 000 — far inside the ``accuracy_m`` any record may honestly
  claim, and two orders of magnitude inside the 3 % default check tolerance.
  Using one radius everywhere keeps a length and an area of the same shape
  mutually consistent, which matters more here than absolute geodetic rigour.

``polygon_area_m2`` lives here rather than in ``schema.py`` (where
``docs/HEP_ATLAS_GEOMETRY.md`` §2 first named it) because it needs the GeoJSON
ring conventions this module defines; ``schema.py`` stays the vocabulary
module and keeps only the scalar ``great_circle_m``.  The doc records that
placement in §2.
"""
from __future__ import annotations

import math
from typing import Any, Iterable, Iterator, Sequence

from . import schema

__all__ = [
    'GEOJSON_TYPES', 'EARTH_RADIUS_M',
    'haversine_m', 'initial_bearing_deg', 'bearing_difference_deg',
    'line_length_m', 'ring_perimeter_m', 'polygon_perimeter_m', 'polygon_area_m2',
    'positions', 'is_position', 'bbox', 'centroid',
    'geometry_length_m', 'geometry_area_m2', 'geometry_span_m', 'geometry_azimuth_deg',
    'geojson_problems', 'simplify', 'round_coordinates', 'COORDINATE_DECIMALS',
]

EARTH_RADIUS_M = schema.EARTH_RADIUS_M

#: RFC 7946 geometry types the atlas may draw (contract §1.2).  `GeometryCollection`
#: is deliberately absent: a feature that needs one is two features.
GEOJSON_TYPES: tuple[str, ...] = (
    'Point', 'LineString', 'MultiLineString', 'Polygon', 'MultiPolygon',
)

#: Types whose measurement is a length, and types whose measurement is an area.
LINE_TYPES: frozenset[str] = frozenset({'LineString', 'MultiLineString'})
POLYGON_TYPES: frozenset[str] = frozenset({'Polygon', 'MultiPolygon'})

#: Decimals used when a bundle writes a coordinate (contract §3).  The seventh
#: decimal of a degree is about 11 mm, well under any accuracy_m the atlas
#: claims, and rounding there is what makes a build byte-deterministic.
COORDINATE_DECIMALS = 7


# ---------------------------------------------------------------------------
# Scalars
# ---------------------------------------------------------------------------

def _number(value: Any) -> float | None:
    """`value` as a finite float, or None (a bool is not a number here)."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def is_position(value: Any) -> bool:
    """True for a well-formed GeoJSON position: `[lon, lat]` (altitude allowed)."""
    if not isinstance(value, (list, tuple)) or not 2 <= len(value) <= 3:
        return False
    lon, lat = _number(value[0]), _number(value[1])
    if lon is None or lat is None:
        return False
    return -180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0


def haversine_m(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Great-circle distance in metres between two **[lon, lat]** points."""
    return schema.great_circle_m(lat1, lon1, lat2, lon2)


def initial_bearing_deg(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Initial great-circle bearing from the first point to the second.

    Degrees clockwise from true north, in ``[0, 360)``.  This is the *forward
    azimuth*: on a sphere it changes along the path, which is exactly why a
    long-baseline direction line is checked at its first vertex (contract
    §2, ``geometry-direction-azimuth``) and not at its midpoint.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)
    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    if x == 0.0 and y == 0.0:
        return 0.0
    return math.degrees(math.atan2(y, x)) % 360.0


def bearing_difference_deg(first: float, second: float) -> float:
    """The smaller angle between two bearings, in ``[0, 180]``."""
    return abs((first - second + 180.0) % 360.0 - 180.0)


# ---------------------------------------------------------------------------
# Walking a geometry
# ---------------------------------------------------------------------------

def positions(geometry: Any) -> list[list[float]]:
    """Every position of a geometry, in document order, as `[lon, lat]` pairs.

    Malformed entries are skipped: this is a measuring helper, not a
    validator, and :func:`geojson_problems` is what reports them.
    """
    return [[float(p[0]), float(p[1])] for p in _iter_raw_positions(geometry) if is_position(p)]


def _iter_raw_positions(node: Any) -> Iterator[Any]:
    """Yield every innermost list-of-numbers of a geometry's `coordinates`."""
    coordinates = node.get('coordinates') if isinstance(node, dict) else node
    yield from _walk_positions(coordinates)


def _walk_positions(node: Any) -> Iterator[Any]:
    if not isinstance(node, (list, tuple)):
        return
    if node and all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in node):
        yield node
        return
    for item in node:
        yield from _walk_positions(item)


def _lines(geometry: Any) -> list[list[list[float]]]:
    """Every line of a geometry as a list of clean positions."""
    if not isinstance(geometry, dict):
        return []
    kind, coordinates = geometry.get('type'), geometry.get('coordinates')
    if kind == 'LineString':
        return [_clean(coordinates)]
    if kind == 'MultiLineString':
        return [_clean(line) for line in coordinates or []]
    return []


def _polygons(geometry: Any) -> list[list[list[list[float]]]]:
    """Every polygon of a geometry as a list of rings (outer ring first)."""
    if not isinstance(geometry, dict):
        return []
    kind, coordinates = geometry.get('type'), geometry.get('coordinates')
    if kind == 'Polygon':
        return [[_clean(ring) for ring in coordinates or []]]
    if kind == 'MultiPolygon':
        return [[_clean(ring) for ring in polygon or []] for polygon in coordinates or []]
    return []


def _clean(node: Any) -> list[list[float]]:
    if not isinstance(node, (list, tuple)):
        return []
    return [[float(p[0]), float(p[1])] for p in node if is_position(p)]


# ---------------------------------------------------------------------------
# Measurements
# ---------------------------------------------------------------------------

def line_length_m(coordinates: Sequence[Any]) -> float:
    """Geodesic length of one `[lon, lat]` vertex list, in metres."""
    points = _clean(coordinates)
    return sum(haversine_m(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
               for i in range(len(points) - 1))


def ring_perimeter_m(ring: Sequence[Any]) -> float:
    """Perimeter of one ring, closing it implicitly when it is not closed."""
    points = _clean(ring)
    if len(points) < 2:
        return 0.0
    if points[0] != points[-1]:
        points = points + [points[0]]
    return line_length_m(points)


def polygon_perimeter_m(geometry: Any) -> float:
    """Perimeter of a Polygon / MultiPolygon: the outer ring(s) only.

    Holes are not fence: a hall's footprint with a courtyard in it has the
    perimeter a plan would print, so an `area` check and a `length` check on
    the same record stay comparable with the same published figure.
    """
    return sum(ring_perimeter_m(rings[0]) for rings in _polygons(geometry) if rings)


def _ring_area_m2(ring: Sequence[Any]) -> float:
    """Signed spherical-excess area of one ring, in square metres.

    The standard spherical polygon formula

        E = Σ (λ_{i+1} − λ_i) · (2 + sin φ_i + sin φ_{i+1})

    with each longitude difference wrapped into ``[-π, π]`` so a shape that
    crosses the antimeridian is measured the short way round.
    """
    points = _clean(ring)
    if len(points) < 3:
        return 0.0
    if points[0] != points[-1]:
        points = points + [points[0]]
    total = 0.0
    for index in range(len(points) - 1):
        lon1, lat1 = points[index]
        lon2, lat2 = points[index + 1]
        d_lambda = math.radians(lon2 - lon1)
        # Wrap into [-pi, pi]: a 359-degree step is a one-degree step back.
        d_lambda = (d_lambda + math.pi) % (2 * math.pi) - math.pi
        total += d_lambda * (2 + math.sin(math.radians(lat1)) + math.sin(math.radians(lat2)))
    return total * EARTH_RADIUS_M * EARTH_RADIUS_M / 2.0


def polygon_area_m2(geometry: Any) -> float:
    """Area of a Polygon / MultiPolygon in m², outer rings minus their holes.

    Ring winding is ignored (RFC 7946 asks for right-hand winding but plenty
    of real data does not comply): the outer ring contributes its absolute
    area and every later ring of the same polygon is subtracted.
    """
    total = 0.0
    for rings in _polygons(geometry):
        if not rings:
            continue
        total += abs(_ring_area_m2(rings[0]))
        for hole in rings[1:]:
            total -= abs(_ring_area_m2(hole))
    return max(total, 0.0)


def geometry_length_m(geometry: Any) -> float | None:
    """The length a `length` check measures: line length, or polygon perimeter.

    `None` for a Point, which has no length to compare with anything.
    """
    kind = (geometry or {}).get('type') if isinstance(geometry, dict) else None
    if kind in LINE_TYPES:
        return sum(line_length_m(line) for line in _lines(geometry))
    if kind in POLYGON_TYPES:
        return polygon_perimeter_m(geometry)
    return None


def geometry_area_m2(geometry: Any) -> float | None:
    """The area an `area` check measures; `None` for anything but a polygon."""
    kind = (geometry or {}).get('type') if isinstance(geometry, dict) else None
    if kind in POLYGON_TYPES:
        return polygon_area_m2(geometry)
    return None


def geometry_span_m(geometry: Any) -> float | None:
    """Largest extent: the greatest great-circle distance between two vertices.

    `None` when there are fewer than two positions.  Quadratic in the vertex
    count, which is why the validator simplifies before measuring a span on a
    shape with thousands of nodes.
    """
    points = positions(geometry)
    if len(points) < 2:
        return None
    best = 0.0
    for index, (lon1, lat1) in enumerate(points):
        for lon2, lat2 in points[index + 1:]:
            distance = haversine_m(lon1, lat1, lon2, lat2)
            if distance > best:
                best = distance
    return best


def geometry_azimuth_deg(geometry: Any) -> float | None:
    """A line's own bearing: first vertex to last vertex.

    `None` unless the geometry is a line with at least two distinct positions.
    """
    lines = _lines(geometry)
    points = lines[0] if lines else []
    if len(points) < 2 or points[0] == points[-1]:
        return None
    return initial_bearing_deg(points[0][0], points[0][1], points[-1][0], points[-1][1])


def bbox(geometry: Any) -> list[float] | None:
    """`[minLon, minLat, maxLon, maxLat]`, or None when there is no position."""
    points = positions(geometry)
    if not points:
        return None
    lons = [point[0] for point in points]
    lats = [point[1] for point in points]
    return [min(lons), min(lats), max(lons), max(lats)]


def merge_bbox(boxes: Iterable[Any]) -> list[float] | None:
    """The bounding box that contains every given `[minLon, minLat, …]` box."""
    rows = [box for box in boxes if isinstance(box, (list, tuple)) and len(box) == 4]
    if not rows:
        return None
    return [min(box[0] for box in rows), min(box[1] for box in rows),
            max(box[2] for box in rows), max(box[3] for box in rows)]


def centroid(geometry: Any) -> list[float] | None:
    """A representative `[lon, lat]` for a feature, or None when empty.

    Polygons use the area-weighted centroid of their outer ring(s) in a local
    equirectangular projection; lines use the length-weighted midpoint of
    their segments; points use themselves.  A degenerate polygon (zero area —
    a ring folded onto a line) falls back to the mean of its vertices, so a
    `distance` check never silently measures from nowhere.
    """
    if not isinstance(geometry, dict):
        return None
    points = positions(geometry)
    if not points:
        return None
    kind = geometry.get('type')
    origin_lat = sum(point[1] for point in points) / len(points)
    scale = math.cos(math.radians(origin_lat)) or 1e-12

    if kind in POLYGON_TYPES:
        total_area = 0.0
        acc_x = acc_y = 0.0
        for rings in _polygons(geometry):
            if not rings:
                continue
            ring = rings[0]
            area, x, y = _ring_centroid(ring, scale)
            total_area += area
            acc_x += x
            acc_y += y
        if total_area:
            return [acc_x / total_area / scale, acc_y / total_area]
    elif kind in LINE_TYPES:
        total_length = 0.0
        acc_lon = acc_lat = 0.0
        for line in _lines(geometry):
            for index in range(len(line) - 1):
                lon1, lat1 = line[index]
                lon2, lat2 = line[index + 1]
                weight = haversine_m(lon1, lat1, lon2, lat2)
                total_length += weight
                acc_lon += weight * (lon1 + lon2) / 2.0
                acc_lat += weight * (lat1 + lat2) / 2.0
        if total_length:
            return [acc_lon / total_length, acc_lat / total_length]

    return [sum(point[0] for point in points) / len(points), origin_lat]


def _ring_centroid(ring: Sequence[Any], scale: float) -> tuple[float, float, float]:
    """`(signed area, area*x, area*y)` of one ring in a local flat projection."""
    points = _clean(ring)
    if len(points) < 3:
        return 0.0, 0.0, 0.0
    if points[0] != points[-1]:
        points = points + [points[0]]
    area = cx = cy = 0.0
    for index in range(len(points) - 1):
        x1, y1 = points[index][0] * scale, points[index][1]
        x2, y2 = points[index + 1][0] * scale, points[index + 1][1]
        cross = x1 * y2 - x2 * y1
        area += cross
        cx += (x1 + x2) * cross
        cy += (y1 + y2) * cross
    area /= 2.0
    if area == 0.0:
        return 0.0, 0.0, 0.0
    return area, cx / 6.0, cy / 6.0


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def geojson_problems(value: Any) -> list[str]:
    """Everything wrong with one GeoJSON *geometry object* (contract §1.2).

    Returns a list of human-readable problems, empty when the value is a
    well-formed geometry of an allowed type: positions in range and finite,
    lines of at least two positions, polygon rings closed and at least four
    positions long.  The list is ordered and stable so a validator message
    reads the same on every run.
    """
    problems: list[str] = []
    if not isinstance(value, dict):
        return [f'geometry must be a GeoJSON geometry object, got {type(value).__name__}']
    kind = value.get('type')
    if kind not in GEOJSON_TYPES:
        return [f'geometry type {kind!r} is not one of {list(GEOJSON_TYPES)}']
    if 'coordinates' not in value:
        return [f'{kind} has no "coordinates"']
    coordinates = value.get('coordinates')

    def check_position(position: Any, where: str) -> None:
        if not isinstance(position, (list, tuple)):
            problems.append(f'{where} is not a [lon, lat] position')
            return
        if not 2 <= len(position) <= 3:
            problems.append(f'{where} has {len(position)} ordinates; a position is [lon, lat]')
            return
        for name, item, limit in (('longitude', position[0], 180.0), ('latitude', position[1], 90.0)):
            number = _number(item)
            if number is None:
                problems.append(f'{where}: {name} {item!r} is not a finite number')
            elif not -limit <= number <= limit:
                problems.append(f'{where}: {name} {number} is outside [-{limit:g}, {limit:g}]')

    def check_line(line: Any, where: str) -> None:
        if not isinstance(line, (list, tuple)):
            problems.append(f'{where} is not a list of positions')
            return
        if len(line) < 2:
            problems.append(f'{where} has {len(line)} position(s); a line needs at least 2')
        for index, position in enumerate(line):
            check_position(position, f'{where}[{index}]')

    def check_ring(ring: Any, where: str) -> None:
        if not isinstance(ring, (list, tuple)):
            problems.append(f'{where} is not a list of positions')
            return
        if len(ring) < 4:
            problems.append(f'{where} has {len(ring)} position(s); a closed ring needs at least 4')
        for index, position in enumerate(ring):
            check_position(position, f'{where}[{index}]')
        if len(ring) >= 2 and is_position(ring[0]) and is_position(ring[-1]):
            if list(ring[0])[:2] != list(ring[-1])[:2]:
                problems.append(f'{where} is not closed: the last position must repeat the first')

    def check_polygon(polygon: Any, where: str) -> None:
        if not isinstance(polygon, (list, tuple)) or not polygon:
            problems.append(f'{where} is not a non-empty list of rings')
            return
        for index, ring in enumerate(polygon):
            check_ring(ring, f'{where}[{index}]')

    if kind == 'Point':
        check_position(coordinates, 'coordinates')
    elif kind == 'LineString':
        check_line(coordinates, 'coordinates')
    elif kind == 'MultiLineString':
        if not isinstance(coordinates, (list, tuple)) or not coordinates:
            problems.append('coordinates is not a non-empty list of lines')
        else:
            for index, line in enumerate(coordinates):
                check_line(line, f'coordinates[{index}]')
    elif kind == 'Polygon':
        check_polygon(coordinates, 'coordinates')
    elif kind == 'MultiPolygon':
        if not isinstance(coordinates, (list, tuple)) or not coordinates:
            problems.append('coordinates is not a non-empty list of polygons')
        else:
            for index, polygon in enumerate(coordinates):
                check_polygon(polygon, f'coordinates[{index}]')
    return problems


# ---------------------------------------------------------------------------
# Simplification
# ---------------------------------------------------------------------------

def simplify(coordinates: Sequence[Any], tolerance_m: float) -> list[list[float]]:
    """Douglas–Peucker on a `[lon, lat]` vertex list with a **metre** tolerance.

    Distances are measured in a local equirectangular projection anchored at
    the line's mean latitude: over a ≤ 60 km map that is accurate to better
    than 0.1 %, and it keeps the routine dependency-free and fast.  The first
    and last vertices are always kept, and a closed ring stays closed (the
    ring is split at its farthest vertex from the start so that the endpoint
    is never the only survivor).

    This exists for the *maintainer* side of the layer — Overpass hands back
    ring geometry with thousands of nodes and a 2 MB bundle budget has to be
    met — never for the validator: a shape is measured as it was authored.
    """
    points = _clean(coordinates)
    if tolerance_m <= 0 or len(points) < 3:
        return [list(point) for point in points]

    closed = points[0] == points[-1]
    origin_lat = sum(point[1] for point in points) / len(points)
    metres_per_degree_lat = math.pi * EARTH_RADIUS_M / 180.0
    metres_per_degree_lon = metres_per_degree_lat * math.cos(math.radians(origin_lat))

    def project(point: Sequence[float]) -> tuple[float, float]:
        return point[0] * metres_per_degree_lon, point[1] * metres_per_degree_lat

    if closed and len(points) > 3:
        body = points[:-1]
        start = project(body[0])
        farthest = max(range(1, len(body)), key=lambda i: _distance2(project(body[i]), start))
        first = _douglas_peucker(body[:farthest + 1], tolerance_m, project)
        second = _douglas_peucker(body[farthest:] + [body[0]], tolerance_m, project)
        kept = first[:-1] + second
        if len(kept) < 4:        # never simplify a ring out of existence
            return [list(point) for point in points]
        return [list(point) for point in kept]

    return [list(point) for point in _douglas_peucker(points, tolerance_m, project)]


def _distance2(a: tuple[float, float], b: tuple[float, float]) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _douglas_peucker(points: list[list[float]], tolerance_m: float, project) -> list[list[float]]:
    if len(points) < 3:
        return list(points)
    start, end = project(points[0]), project(points[-1])
    worst_index, worst = 0, -1.0
    for index in range(1, len(points) - 1):
        distance = _point_segment_distance(project(points[index]), start, end)
        if distance > worst:
            worst_index, worst = index, distance
    if worst <= tolerance_m:
        return [points[0], points[-1]]
    left = _douglas_peucker(points[:worst_index + 1], tolerance_m, project)
    right = _douglas_peucker(points[worst_index:], tolerance_m, project)
    return left[:-1] + right


def _point_segment_distance(point: tuple[float, float], start: tuple[float, float],
                            end: tuple[float, float]) -> float:
    """Perpendicular distance from `point` to the segment `start`-`end`."""
    dx, dy = end[0] - start[0], end[1] - start[1]
    if dx == 0.0 and dy == 0.0:
        return math.hypot(point[0] - start[0], point[1] - start[1])
    t = ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(point[0] - (start[0] + t * dx), point[1] - (start[1] + t * dy))


# ---------------------------------------------------------------------------
# Emitting
# ---------------------------------------------------------------------------

def round_coordinates(node: Any, decimals: int = COORDINATE_DECIMALS) -> Any:
    """Round every number inside a `coordinates` tree to `decimals` places.

    Returns ints unchanged only when they are already whole; `-0.0` is
    normalised to `0.0` so two builds of the same data cannot differ by a
    sign that JSON renders but arithmetic does not.
    """
    if isinstance(node, (list, tuple)):
        return [round_coordinates(item, decimals) for item in node]
    number = _number(node)
    if number is None:
        return node
    rounded = round(number, decimals)
    return 0.0 if rounded == 0 else rounded


def round_geometry(geometry: Any, decimals: int = COORDINATE_DECIMALS) -> Any:
    """A copy of a GeoJSON geometry with its coordinates rounded (contract §3)."""
    if not isinstance(geometry, dict):
        return geometry
    out = {key: value for key, value in geometry.items() if key != 'coordinates'}
    out['coordinates'] = round_coordinates(geometry.get('coordinates'), decimals)
    return out
