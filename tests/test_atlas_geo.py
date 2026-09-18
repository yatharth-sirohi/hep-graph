"""Tests for hepgraph/atlas/geo.py — the geodesy of the local-map layer (A25).

These are checked against figures that are true independently of this code:
one degree of latitude is 111.2 km on the WGS 84 mean sphere; a circle of
1 km radius has a 6 283 m circumference and a 3.14 km² area; a due-north
segment bears 000°.  Nothing here loads a fixture — `geo.py` is pure.
"""

from __future__ import annotations

import math

import pytest

from hepgraph.atlas import geo


def circle(lon: float, lat: float, radius_m: float, vertices: int = 360) -> dict:
    """A closed GeoJSON Polygon approximating a circle of `radius_m`."""
    metres_per_degree = math.pi * geo.EARTH_RADIUS_M / 180.0
    d_lat = radius_m / metres_per_degree
    d_lon = d_lat / math.cos(math.radians(lat))
    ring = [[lon + d_lon * math.sin(2 * math.pi * i / vertices),
             lat + d_lat * math.cos(2 * math.pi * i / vertices)]
            for i in range(vertices)]
    ring.append(list(ring[0]))
    return {"type": "Polygon", "coordinates": [ring]}


# ---------------------------------------------------------------------------
# Distances and bearings
# ---------------------------------------------------------------------------

def test_one_degree_of_latitude_is_about_111_2_km() -> None:
    metres = geo.haversine_m(0.0, 0.0, 0.0, 1.0)
    assert metres == pytest.approx(111_195, rel=1e-4)


def test_one_degree_of_longitude_shrinks_with_the_cosine_of_latitude() -> None:
    at_equator = geo.haversine_m(0.0, 0.0, 1.0, 0.0)
    at_sixty = geo.haversine_m(0.0, 60.0, 1.0, 60.0)
    assert at_sixty / at_equator == pytest.approx(0.5, rel=1e-3)


def test_haversine_takes_lon_lat_while_schema_takes_lat_lon() -> None:
    from hepgraph.atlas import schema

    assert geo.haversine_m(6.05, 46.23, 6.06, 46.24) == pytest.approx(
        schema.great_circle_m(46.23, 6.05, 46.24, 6.06))


def test_initial_bearing_of_the_four_cardinal_directions() -> None:
    assert geo.initial_bearing_deg(0.0, 0.0, 0.0, 1.0) == pytest.approx(0.0, abs=1e-6)
    assert geo.initial_bearing_deg(0.0, 0.0, 1.0, 0.0) == pytest.approx(90.0, abs=1e-6)
    assert geo.initial_bearing_deg(0.0, 1.0, 0.0, 0.0) == pytest.approx(180.0, abs=1e-6)
    assert geo.initial_bearing_deg(1.0, 0.0, 0.0, 0.0) == pytest.approx(270.0, abs=1e-6)


def test_bearing_difference_wraps_across_north() -> None:
    assert geo.bearing_difference_deg(359.0, 1.0) == pytest.approx(2.0)
    assert geo.bearing_difference_deg(10.0, 350.0) == pytest.approx(20.0)
    assert geo.bearing_difference_deg(0.0, 180.0) == pytest.approx(180.0)


# ---------------------------------------------------------------------------
# Lengths, perimeters and areas
# ---------------------------------------------------------------------------

def test_line_length_sums_its_segments() -> None:
    line = {"type": "LineString", "coordinates": [[0.0, 0.0], [0.0, 1.0], [0.0, 2.0]]}
    assert geo.geometry_length_m(line) == pytest.approx(2 * 111_195, rel=1e-4)


def test_multilinestring_length_is_the_sum_of_its_parts() -> None:
    geometry = {"type": "MultiLineString",
                "coordinates": [[[0.0, 0.0], [0.0, 1.0]], [[10.0, 0.0], [10.0, 1.0]]]}
    assert geo.geometry_length_m(geometry) == pytest.approx(2 * 111_195, rel=1e-4)


def test_a_one_kilometre_circle_has_a_6283_metre_perimeter() -> None:
    assert geo.polygon_perimeter_m(circle(6.06, 46.26, 1000.0)) == pytest.approx(6283.0, rel=2e-3)


def test_a_one_kilometre_circle_has_an_area_of_pi_square_kilometres() -> None:
    area = geo.polygon_area_m2(circle(6.06, 46.26, 1000.0))
    assert area == pytest.approx(math.pi * 1e6, rel=2e-3)


def test_polygon_length_measurement_is_its_perimeter() -> None:
    shape = circle(6.06, 46.26, 1000.0)
    assert geo.geometry_length_m(shape) == pytest.approx(geo.polygon_perimeter_m(shape))


def test_a_hole_is_subtracted_from_the_area_but_not_from_the_perimeter() -> None:
    outer = circle(6.06, 46.26, 1000.0)["coordinates"][0]
    inner = circle(6.06, 46.26, 500.0)["coordinates"][0]
    with_hole = {"type": "Polygon", "coordinates": [outer, inner]}
    assert geo.polygon_area_m2(with_hole) == pytest.approx(math.pi * (1e6 - 0.25e6), rel=3e-3)
    assert geo.polygon_perimeter_m(with_hole) == pytest.approx(6283.0, rel=2e-3)


def test_area_of_a_line_and_length_of_a_point_are_unmeasurable() -> None:
    line = {"type": "LineString", "coordinates": [[0.0, 0.0], [0.0, 1.0]]}
    point = {"type": "Point", "coordinates": [0.0, 0.0]}
    assert geo.geometry_area_m2(line) is None
    assert geo.geometry_length_m(point) is None
    assert geo.geometry_area_m2(point) is None


def test_ring_winding_does_not_change_the_area() -> None:
    ring = circle(6.06, 46.26, 1000.0)["coordinates"][0]
    reversed_ring = list(reversed(ring))
    assert geo.polygon_area_m2({"type": "Polygon", "coordinates": [reversed_ring]}) == \
        pytest.approx(geo.polygon_area_m2({"type": "Polygon", "coordinates": [ring]}))


def test_span_is_the_greatest_distance_between_two_vertices() -> None:
    shape = circle(6.06, 46.26, 1000.0, vertices=60)
    assert geo.geometry_span_m(shape) == pytest.approx(2000.0, rel=5e-3)


def test_azimuth_is_the_bearing_from_the_first_vertex_to_the_last() -> None:
    line = {"type": "LineString", "coordinates": [[0.0, 0.0], [0.5, 0.5], [0.0, 1.0]]}
    assert geo.geometry_azimuth_deg(line) == pytest.approx(0.0, abs=1e-6)
    assert geo.geometry_azimuth_deg({"type": "Point", "coordinates": [0.0, 0.0]}) is None


def test_a_closed_ring_has_no_azimuth() -> None:
    ring = circle(6.06, 46.26, 1000.0, vertices=8)["coordinates"][0]
    assert geo.geometry_azimuth_deg({"type": "LineString", "coordinates": ring}) is None


# ---------------------------------------------------------------------------
# bbox and centroid
# ---------------------------------------------------------------------------

def test_bbox_is_min_lon_min_lat_max_lon_max_lat() -> None:
    line = {"type": "LineString", "coordinates": [[2.0, -1.0], [-3.0, 4.0]]}
    assert geo.bbox(line) == [-3.0, -1.0, 2.0, 4.0]
    assert geo.bbox({"type": "LineString", "coordinates": []}) is None


def test_merge_bbox_contains_every_input() -> None:
    assert geo.merge_bbox([[0, 0, 1, 1], [-1, 2, 0, 3]]) == [-1, 0, 1, 3]
    assert geo.merge_bbox([]) is None


def test_centroid_of_a_circle_is_its_centre() -> None:
    lon, lat = 6.06, 46.26
    centre = geo.centroid(circle(lon, lat, 1000.0))
    assert centre[0] == pytest.approx(lon, abs=1e-6)
    assert centre[1] == pytest.approx(lat, abs=1e-6)


def test_centroid_of_a_straight_line_is_its_midpoint() -> None:
    line = {"type": "LineString", "coordinates": [[0.0, 0.0], [0.0, 2.0]]}
    assert geo.centroid(line) == pytest.approx([0.0, 1.0], abs=1e-9)


def test_centroid_of_a_point_is_the_point() -> None:
    assert geo.centroid({"type": "Point", "coordinates": [6.5, 46.5]}) == [6.5, 46.5]


def test_a_degenerate_polygon_still_has_a_centroid() -> None:
    folded = {"type": "Polygon", "coordinates": [[[0.0, 0.0], [0.0, 1.0], [0.0, 0.0], [0.0, 0.0]]]}
    assert geo.centroid(folded) is not None


# ---------------------------------------------------------------------------
# GeoJSON validation
# ---------------------------------------------------------------------------

def test_a_well_formed_geometry_of_each_allowed_type_has_no_problems() -> None:
    good = [
        {"type": "Point", "coordinates": [6.0, 46.0]},
        {"type": "LineString", "coordinates": [[6.0, 46.0], [6.1, 46.1]]},
        {"type": "MultiLineString", "coordinates": [[[6.0, 46.0], [6.1, 46.1]]]},
        circle(6.0, 46.0, 500.0, vertices=8),
        {"type": "MultiPolygon", "coordinates": [circle(6.0, 46.0, 500.0, vertices=8)["coordinates"]]},
    ]
    for geometry in good:
        assert geo.geojson_problems(geometry) == [], geometry["type"]


@pytest.mark.parametrize("geometry", [
    {"type": "GeometryCollection", "geometries": []},
    {"type": "Polygon"},
    "LineString",
    None,
])
def test_a_disallowed_or_shapeless_geometry_is_reported(geometry) -> None:
    assert geo.geojson_problems(geometry)


def test_a_line_needs_two_positions() -> None:
    problems = geo.geojson_problems({"type": "LineString", "coordinates": [[6.0, 46.0]]})
    assert any("at least 2" in problem for problem in problems)


def test_a_ring_must_be_closed_and_four_positions_long() -> None:
    open_ring = {"type": "Polygon",
                 "coordinates": [[[0.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, 0.0]]]}
    assert any("not closed" in problem for problem in geo.geojson_problems(open_ring))
    short = {"type": "Polygon", "coordinates": [[[0.0, 0.0], [0.0, 1.0], [0.0, 0.0]]]}
    assert any("at least 4" in problem for problem in geo.geojson_problems(short))


def test_out_of_range_and_non_finite_coordinates_are_reported() -> None:
    out_of_range = {"type": "Point", "coordinates": [181.0, 46.0]}
    assert any("outside" in problem for problem in geo.geojson_problems(out_of_range))
    nan = {"type": "Point", "coordinates": [float("nan"), 46.0]}
    assert any("finite" in problem for problem in geo.geojson_problems(nan))
    assert any("finite" in problem for problem in
               geo.geojson_problems({"type": "Point", "coordinates": ["6.0", 46.0]}))


def test_positions_skips_what_it_cannot_measure() -> None:
    assert geo.positions({"type": "LineString", "coordinates": [[6.0, 46.0], ["x", "y"]]}) == \
        [[6.0, 46.0]]


# ---------------------------------------------------------------------------
# Simplification
# ---------------------------------------------------------------------------

def test_simplify_drops_vertices_that_lie_on_the_line() -> None:
    line = [[0.0, 0.0], [0.0, 0.5], [0.0, 1.0]]
    assert geo.simplify(line, 1.0) == [[0.0, 0.0], [0.0, 1.0]]


def test_simplify_keeps_a_vertex_further_off_than_the_tolerance() -> None:
    # 0.001 degree of longitude at the equator is about 111 m.
    line = [[0.0, 0.0], [0.001, 0.5], [0.0, 1.0]]
    assert len(geo.simplify(line, 10.0)) == 3
    assert len(geo.simplify(line, 200.0)) == 2


def test_simplify_keeps_a_ring_closed() -> None:
    ring = circle(6.0, 46.0, 1000.0, vertices=200)["coordinates"][0]
    simplified = geo.simplify(ring, 20.0)
    assert simplified[0] == simplified[-1]
    assert 4 <= len(simplified) < len(ring)
    perimeter = geo.ring_perimeter_m(simplified)
    assert perimeter == pytest.approx(6283.0, rel=0.05)


def test_simplify_is_a_no_op_below_three_points_or_without_a_tolerance() -> None:
    assert geo.simplify([[0.0, 0.0], [0.0, 1.0]], 100.0) == [[0.0, 0.0], [0.0, 1.0]]
    line = [[0.0, 0.0], [0.0, 0.5], [0.0, 1.0]]
    assert geo.simplify(line, 0.0) == line


# ---------------------------------------------------------------------------
# Emitting
# ---------------------------------------------------------------------------

def test_coordinates_round_to_seven_decimals_without_a_negative_zero() -> None:
    rounded = geo.round_geometry({"type": "LineString",
                                  "coordinates": [[6.055465712345, 46.23568001], [-1e-12, 0.0]]})
    assert rounded["coordinates"] == [[6.0554657, 46.23568], [0.0, 0.0]]
    assert str(rounded["coordinates"][1][0]) == "0.0"
