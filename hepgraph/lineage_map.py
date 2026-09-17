"""Lay the whole doctoral forest out once, so a browser can draw it.

Doctoral descent is a forest of directed acyclic graphs: 21,137 people in
4,073 separate trees, the largest holding 3,783 and over two thousand being a
single adviser-and-student pair. Laying that out in the browser would mean
shipping the edge list and doing the work on every load, so it is computed here
and stored as coordinates.

Two deliberate exceptions to how the rest of the graph works:

* **Names are stored.** The compact graph holds no names on purpose, but a map
  you can search needs labels for every point, and fetching 21,000 of them per
  visit is not a thing to do to INSPIRE. They are harvested once into a table
  scoped to the overlay. Author names are CC0 metadata; nothing else is kept.
* **The layout is precomputed.** It depends only on the overlay, so it is
  rebuilt when the overlay is, not per request.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import os
import sys
import time
from typing import Any

from .neon_graph_provider import _at
from .pipeline import InspireClient, PipelineError, _hits, sanitize_author


#: Only doctoral relations form the tree, matching what the app traverses.
from .neon_graph_provider import ADVISER_DEGREES  # noqa: E402

DEGREES = list(ADVISER_DEGREES)
NAME_BATCH = 25

#: Abstract layout units. A browser scales these; they only set proportions,
#: but the proportion is the whole point: the renderer sizes each box to the
#: gap to its neighbour, so a narrow column makes every box too thin to hold a
#: name. A column several times the row height gives boxes a readable shape.
COLUMN = 180
ROW = 110
#: Components are shelf-packed, and the shelf is as wide as the widest tree.
#: One component - 3,783 people across eight generations - is 2,662 columns
#: wide on its own, so it fixes the total width whatever else is done. Making
#: every shelf that wide keeps the rest dense beside it; a narrower shelf would
#: square the picture up only by leaving most of it empty.
SHELF_COLUMNS = 2700
COMPONENT_GAP = 3
SHELF_GAP = 1

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS graph_genealogy_person ("
    " overlay_id TEXT NOT NULL,"
    " person_id BIGINT NOT NULL,"
    " name TEXT,"
    " PRIMARY KEY (overlay_id, person_id));"
    "CREATE TABLE IF NOT EXISTS graph_lineage_layout ("
    " overlay_id TEXT NOT NULL,"
    " person_id BIGINT NOT NULL,"
    " x INTEGER NOT NULL,"
    " y INTEGER NOT NULL,"
    " generation SMALLINT NOT NULL,"
    " component INTEGER NOT NULL,"
    " component_size INTEGER NOT NULL,"
    " PRIMARY KEY (overlay_id, person_id));"
    "CREATE INDEX IF NOT EXISTS graph_lineage_layout_component"
    " ON graph_lineage_layout (overlay_id, component);"
)


def read_edges(connection: Any, overlay_id: str) -> list[tuple[int, int]]:
    return [(int(_at(row, 0)), int(_at(row, 1))) for row in connection.execute(
        "SELECT adviser_id, student_id FROM graph_genealogy_edge "
        "WHERE overlay_id=%s AND COALESCE(degree,'other')=ANY(%s) ORDER BY adviser_id, student_id",
        (overlay_id, DEGREES)).fetchall()]


def _components(edges: list[tuple[int, int]]) -> dict[int, int]:
    """Union-find over the undirected shape; a family tree is one component."""
    parent: dict[int, int] = {}

    def find(node: int) -> int:
        parent.setdefault(node, node)
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for adviser, student in edges:
        left, right = find(adviser), find(student)
        if left != right:
            parent[left] = right
    return {node: find(node) for node in parent}


def _generations(edges: list[tuple[int, int]], people: set[int]) -> dict[int, int]:
    """Longest path from a person with no recorded adviser.

    Longest rather than shortest so a person never appears above someone they
    descend from, which is what makes the rows read as generations.
    """
    advisers = defaultdict(list)
    students = defaultdict(list)
    for adviser, student in edges:
        advisers[student].append(adviser)
        students[adviser].append(student)
    generation = {person: 0 for person in people}
    # Kahn order over the DAG: settle a person only once every adviser has been.
    remaining = {person: len(advisers[person]) for person in people}
    queue = [person for person in sorted(people) if remaining[person] == 0]
    seen = 0
    while queue:
        person = queue.pop()
        seen += 1
        for student in students[person]:
            generation[student] = max(generation[student], generation[person] + 1)
            remaining[student] -= 1
            if remaining[student] == 0:
                queue.append(student)
    if seen != len(people):
        # The overlay validator proves this cannot happen; refuse rather than
        # emit a layout that silently drops people inside a cycle.
        raise PipelineError("doctoral relations contain a cycle; layout refused")
    return generation


def build_layout(edges: list[tuple[int, int]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Coordinates for every person: generation down, family across."""
    people = {person for edge in edges for person in edge}
    component_of = _components(edges)
    generation = _generations(edges, people)
    students = defaultdict(list)
    advisers = defaultdict(list)
    for adviser, student in edges:
        students[adviser].append(student)
        advisers[student].append(adviser)

    grouped: dict[int, list[int]] = defaultdict(list)
    for person in people:
        grouped[component_of[person]].append(person)

    placed: dict[int, int] = {}          # person -> column within its component
    widths: dict[int, int] = {}          # component -> column count
    depths: dict[int, int] = {}
    for root, members in grouped.items():
        cursor = 0
        seen: set[int] = set()

        def place(person: int) -> tuple[int, int]:
            """Depth-first: leaves take the next column, parents centre on theirs."""
            nonlocal cursor
            if person in seen:
                return placed[person], placed[person]
            seen.add(person)
            children = [child for child in sorted(students[person]) if child not in seen]
            if not children:
                placed[person] = cursor
                cursor += 1
                return placed[person], placed[person]
            spans = [place(child) for child in children]
            low, high = min(s[0] for s in spans), max(s[1] for s in spans)
            placed[person] = (low + high) // 2
            return low, high

        # Start from people with no adviser so a line reads downward; anything
        # left over is inside a rejoin and is placed after.
        for person in sorted(members, key=lambda item: (generation[item], item)):
            if not advisers[person] and person not in seen:
                place(person)
        for person in sorted(members):
            if person not in seen:
                place(person)
        widths[root] = max(cursor, 1)
        depths[root] = max(generation[person] for person in members) + 1

    # Shelf-pack the components: tallest first, wrapping at the strip width, so
    # the big tree anchors the view and the thousands of pairs fill in beside it.
    order = sorted(grouped, key=lambda root: (-len(grouped[root]), -widths[root], root))
    offsets: dict[int, tuple[int, int]] = {}
    shelf_x = shelf_y = shelf_height = 0
    for root in order:
        if shelf_x and shelf_x + widths[root] > SHELF_COLUMNS:
            shelf_y += shelf_height + SHELF_GAP
            shelf_x, shelf_height = 0, 0
        offsets[root] = (shelf_x, shelf_y)
        shelf_x += widths[root] + COMPONENT_GAP
        shelf_height = max(shelf_height, depths[root])
    total_rows = shelf_y + shelf_height

    nodes = []
    for person in sorted(people):
        root = component_of[person]
        offset_x, offset_y = offsets[root]
        nodes.append({"id": person,
                      "x": (offset_x + placed[person]) * COLUMN,
                      "y": (offset_y + generation[person]) * ROW,
                      "generation": generation[person],
                      "component": root,
                      "component_size": len(grouped[root])})
    bounds = {"width": (SHELF_COLUMNS + COMPONENT_GAP) * COLUMN,
              "height": (total_rows + 1) * ROW}
    return nodes, bounds


def harvest_names(connection: Any, overlay_id: str, client: Any, *,
                  rate: float = 2.0, limit: int | None = None) -> dict[str, int]:
    """Fetch a display name per person, once, in batches.

    Resumable: only people without a row are asked for, so an interrupted run
    continues rather than restarting.
    """
    missing = [int(_at(row, 0)) for row in connection.execute(
        "SELECT DISTINCT person FROM ("
        "  SELECT adviser_id AS person FROM graph_genealogy_edge"
        "   WHERE overlay_id=%s AND COALESCE(degree,'other')=ANY(%s)"
        "  UNION SELECT student_id FROM graph_genealogy_edge"
        "   WHERE overlay_id=%s AND COALESCE(degree,'other')=ANY(%s)) AS everyone "
        "WHERE NOT EXISTS (SELECT 1 FROM graph_genealogy_person p "
        "                   WHERE p.overlay_id=%s AND p.person_id = everyone.person) "
        "ORDER BY person", (overlay_id, DEGREES, overlay_id, DEGREES, overlay_id)).fetchall()]
    if limit is not None:
        missing = missing[:limit]
    stored = failed = 0
    interval = 1.0 / rate if rate > 0 else 0.0
    for start in range(0, len(missing), NAME_BATCH):
        batch = missing[start:start + NAME_BATCH]
        query = " OR ".join(f"control_number:{person}" for person in batch)
        began = time.monotonic()
        rows: list[tuple[Any, ...]] = []
        try:
            for hit in _hits(client.fetch("authors", query, 1, len(batch))):
                try:
                    recid, payload = sanitize_author(hit)
                except PipelineError:
                    continue
                name = payload.get("name")
                if isinstance(name, dict):
                    name = name.get("preferred_name") or name.get("value")
                rows.append((overlay_id, int(recid), name if isinstance(name, str) else None))
        except Exception as error:  # a blip must not lose the run's progress
            failed += len(batch)
            print(f"batch at {start} failed: {error}", file=sys.stderr, flush=True)
        found = {row[1] for row in rows}
        # A person INSPIRE did not return still gets a row, so a resumed run does
        # not ask for them forever; the null name is read as "no name available".
        rows.extend((overlay_id, person, None) for person in batch if person not in found)
        with connection.cursor() as cursor:
            cursor.executemany(
                "INSERT INTO graph_genealogy_person(overlay_id,person_id,name) "
                "VALUES (%s,%s,%s) ON CONFLICT (overlay_id,person_id) DO NOTHING", rows)
        stored += len(rows)
        if stored % 2000 < NAME_BATCH:
            print(f"{stored:,} / {len(missing):,} names", flush=True)
        wait = interval - (time.monotonic() - began)
        if wait > 0:
            time.sleep(wait)
    return {"requested": len(missing), "stored": stored, "failed": failed}


def store_layout(connection: Any, overlay_id: str, nodes: list[dict[str, Any]]) -> None:
    with connection.transaction():
        connection.execute("DELETE FROM graph_lineage_layout WHERE overlay_id=%s", (overlay_id,))
        with connection.cursor() as cursor:
            with cursor.copy("COPY graph_lineage_layout (overlay_id,person_id,x,y,generation,"
                             "component,component_size) FROM STDIN") as copy:
                for node in nodes:
                    copy.write_row((overlay_id, node["id"], node["x"], node["y"],
                                    node["generation"], node["component"],
                                    node["component_size"]))


def read_map(connection: Any, overlay_id: str, version: str) -> dict[str, Any]:
    """The payload the browser draws. Nodes are arrays; edges are indices."""
    rows = connection.execute(
        "SELECT l.person_id, l.x, l.y, l.generation, l.component_size, p.name, l.component "
        "FROM graph_lineage_layout l "
        "LEFT JOIN graph_genealogy_person p "
        "  ON p.overlay_id = l.overlay_id AND p.person_id = l.person_id "
        "WHERE l.overlay_id=%s ORDER BY l.person_id", (overlay_id,)).fetchall()
    if not rows:
        return {"status": "unavailable",
                "message": "The lineage map has not been built for this release."}
    index = {}
    # Names ride alongside the nodes in the same order rather than in a map
    # keyed by id: at this size the repeated keys alone cost about 600 kB, and
    # the response has a hard ceiling on the platform that serves it.
    index = {}
    nodes, names = [], []
    width = height = 0
    for position, row in enumerate(rows):
        person, x, y = int(_at(row, 0)), int(_at(row, 1)), int(_at(row, 2))
        index[person] = position
        nodes.append([person, x, y, int(_at(row, 3)), int(_at(row, 4))])
        names.append(_at(row, 5) or "")
        width, height = max(width, x), max(height, y)
    edges = [[index[adviser], index[student]]
             for adviser, student in read_edges(connection, overlay_id)
             if adviser in index and student in index]
    components = len({_at(row, 6) for row in rows})
    return {"status": "ok", "version": version, "overlay": overlay_id,
            "counts": {"people": len(nodes), "relations": len(edges),
                       "components": components,
                       "named": sum(1 for name in names if name)},
            "bounds": {"width": width + 200, "height": height + 200},
            "nodes": nodes, "names": names, "edges": edges}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL_UNPOOLED"))
    parser.add_argument("--overlay-id", default="inspire-genealogy")
    parser.add_argument("--names", action="store_true", help="harvest missing display names")
    parser.add_argument("--layout", action="store_true", help="recompute and store the layout")
    parser.add_argument("--rate", type=float, default=2.0)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args(argv)
    if not args.database_url:
        parser.error("a direct database URL is required")
    import psycopg

    with psycopg.connect(args.database_url, autocommit=True) as connection:
        connection.execute("SELECT set_config('statement_timeout','600000',false)")
        connection.execute(SCHEMA)
        if args.names:
            print(harvest_names(connection, args.overlay_id, InspireClient(),
                                rate=args.rate, limit=args.limit), flush=True)
        if args.layout:
            edges = read_edges(connection, args.overlay_id)
            nodes, bounds = build_layout(edges)
            store_layout(connection, args.overlay_id, nodes)
            print({"people": len(nodes), "relations": len(edges), "bounds": bounds}, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
