"""Bounded, deterministic algorithms for an HEP people graph.

The graph deliberately stores work-to-person incidence instead of materialising a
clique for every paper.  A coauthor pair is evaluated only when a query needs it.
"""

from __future__ import annotations

from collections import OrderedDict, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
import random
import re
from typing import Any


class GraphError(ValueError):
    """A client-visible graph error.

    ``resource_limit`` is intentionally distinct from a missing path: callers can
    retry a smaller request without accidentally presenting a false conclusion.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise GraphError("invalid_filter", f"{field} must be an integer")
    return value


@dataclass(frozen=True)
class Filters:
    max_authors: int | None = 10
    min_shared: int = 1
    year_start: int | None = None
    year_end: int | None = None
    genealogy: bool = True
    # Appended to preserve positional callers that construct the original five
    # fields directly.  The public large-team mode uses 11..unbounded.
    min_authors: int = 1

    def __post_init__(self) -> None:
        if isinstance(self.min_authors, bool) or not isinstance(self.min_authors, int) or not 1 <= self.min_authors <= 100_000:
            raise GraphError("invalid_filter", "min_authors must be between 1 and 100000")
        if self.max_authors is not None:
            if isinstance(self.max_authors, bool) or not isinstance(self.max_authors, int) or not 1 <= self.max_authors <= 100_000:
                raise GraphError("invalid_filter", "max_authors must be between 1 and 100000, or all")
            if self.max_authors < self.min_authors:
                raise GraphError("invalid_filter", "max_authors must not be below min_authors")

    @classmethod
    def from_dict(cls, values: dict[str, Any]) -> "Filters":
        if not isinstance(values, dict):
            raise GraphError("invalid_filter", "filters must be an object")
        allowed = {"max_authors", "min_shared", "year_start", "year_end", "genealogy", "min_authors"}
        unknown = set(values) - allowed
        if unknown:
            raise GraphError("invalid_filter", f"unknown filter: {sorted(unknown)[0]}")

        max_authors = values.get("max_authors", 10)
        if max_authors == "all":
            max_authors = None
        elif max_authors is not None:
            max_authors = _integer(max_authors, "max_authors")
            if not 1 <= max_authors <= 100_000:
                raise GraphError("invalid_filter", "max_authors must be between 1 and 100000, or all")

        min_authors = _integer(values.get("min_authors", 1), "min_authors")
        if not 1 <= min_authors <= 100_000:
            raise GraphError("invalid_filter", "min_authors must be between 1 and 100000")
        if max_authors is not None and max_authors < min_authors:
            raise GraphError("invalid_filter", "max_authors must not be below min_authors")

        min_shared = _integer(values.get("min_shared", 1), "min_shared")
        if not 1 <= min_shared <= 1_000:
            raise GraphError("invalid_filter", "min_shared must be between 1 and 1000")

        year_start = values.get("year_start")
        year_end = values.get("year_end")
        for field, value in (("year_start", year_start), ("year_end", year_end)):
            if value is not None:
                value = _integer(value, field)
                if not 1000 <= value <= 2100:
                    raise GraphError("invalid_filter", f"{field} must be between 1000 and 2100")
                if field == "year_start":
                    year_start = value
                else:
                    year_end = value
        if year_start is not None and year_end is not None and year_start > year_end:
            raise GraphError("invalid_filter", "year_start must not be after year_end")

        genealogy = values.get("genealogy", True)
        if isinstance(genealogy, str):
            if genealogy.lower() == "true":
                genealogy = True
            elif genealogy.lower() == "false":
                genealogy = False
        if not isinstance(genealogy, bool):
            raise GraphError("invalid_filter", "genealogy must be true or false")
        return cls(max_authors, min_shared, year_start, year_end, genealogy, min_authors)

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_authors": self.max_authors,
            "min_shared": self.min_shared,
            "year_start": self.year_start,
            "year_end": self.year_end,
            "genealogy": self.genealogy,
            "min_authors": self.min_authors,
        }


class Graph:
    """A filtered view of an immutable graph snapshot.

    Class limits are attributes so a host can tune them, and tests can exercise
    limit handling without allocating an impractically large fixture.
    """

    MAX_INDEXED_PEOPLE = 50_000
    MAX_INDEXED_WORKS = 100_000
    MAX_AUTHOR_OCCURRENCES = 1_000_000
    MAX_QUERY_OPERATIONS = 250_000
    MAX_PATH_NODES = 25_000
    # Exact distance metrics operate on the non-isolated active graph.  The
    # population can be much larger (a realistic snapshot has many people whose
    # papers exceed the author cap); harmonic normalization still uses all people.
    MAX_CENTRALITY_NODES = 6_000
    MAX_EXACT_BETWEENNESS_NODES = 500
    BETWENNESS_SAMPLE_SOURCES = 64
    BETWENNESS_SAMPLE_SEED = 42
    MAX_CENTRALITY_WORK = 20_000_000
    MAX_NEIGHBORHOOD_LIMIT = 1_000
    MAX_PAIR_CACHE = 20_000
    MAX_NEIGHBOR_CACHE = 5_000

    _ALLOWED_TYPES = {"article", "conference paper"}
    _EXCLUDED_TYPES = {"thesis", "book", "book chapter", "proceedings"}
    # Corrections are separately indexed records and can repeat the original
    # paper's author list.  Match only a leading correction label with a real
    # punctuation/whitespace boundary: a research title that merely discusses
    # an erratum remains an eligible scholarly work.
    _STANDALONE_CORRECTION_TITLE = re.compile(
        r"^\s*(?:erratum|errata|corrigendum)(?=$|\W)", re.IGNORECASE
    )

    def __init__(self, snapshot: dict[str, Any], filters: Filters | None = None) -> None:
        if not isinstance(snapshot, dict):
            raise GraphError("invalid_snapshot", "snapshot must be an object")
        self.snapshot = snapshot
        self.version = str(snapshot.get("version", "unknown"))
        self.filters = filters or Filters()
        if not isinstance(self.filters, Filters):
            raise GraphError("invalid_filter", "filters must be a Filters instance")

        raw_people = snapshot.get("people", [])
        if not isinstance(raw_people, list):
            raise GraphError("invalid_snapshot", "people must be a list")
        self.people: dict[str, dict[str, Any]] = {}
        for person in raw_people:
            if isinstance(person, dict) and person.get("id") is not None:
                self.people.setdefault(str(person["id"]), person)
        if len(self.people) > self.MAX_INDEXED_PEOPLE:
            raise GraphError("resource_limit", "snapshot has too many indexed people")

        raw_works = snapshot.get("works", [])
        if not isinstance(raw_works, list):
            raise GraphError("invalid_snapshot", "works must be a list")
        if len(raw_works) > self.MAX_INDEXED_WORKS:
            raise GraphError("resource_limit", "snapshot has too many works")
        self.works: dict[str, dict[str, Any]] = {}
        self._person_works: dict[str, set[str]] = defaultdict(set)
        self._all_person_works: dict[str, set[str]] = defaultdict(set)
        occurrences = 0
        seen_work_ids: set[str] = set()
        for work in raw_works:
            if not isinstance(work, dict) or work.get("id") is None:
                continue
            work_id = str(work["id"])
            # Snapshot records are stable-ID deduplicated.  Defensively retain the
            # first occurrence so repeats cannot inflate publications or evidence.
            if work_id in seen_work_ids:
                continue
            seen_work_ids.add(work_id)
            authors = self._resolved_authors(work)
            for author in authors:
                self._all_person_works[author].add(work_id)
            if not self._eligible_work(work):
                continue
            occurrences += len(authors)
            if occurrences > self.MAX_AUTHOR_OCCURRENCES:
                raise GraphError("resource_limit", "eligible authorship incidence is too large")
            self.works[work_id] = work
            for author in authors:
                self._person_works[author].add(work_id)

        self._phd_by_person: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._phd_by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        self.phd: list[dict[str, Any]] = []
        # Keep documented doctoral evidence inspectable in profiles and ancestry
        # even when the selected graph excludes genealogy from ordinary paths.
        self._index_phd(snapshot.get("phd", []))
        self._pair_cache: OrderedDict[tuple[str, str], tuple[str, ...]] = OrderedDict()
        self._neighbor_cache: OrderedDict[tuple[str, bool], tuple[str, ...]] = OrderedDict()

    def _eligible_work(self, work: dict[str, Any]) -> bool:
        title = work.get("title")
        if isinstance(title, str) and self._STANDALONE_CORRECTION_TITLE.match(title):
            return False
        types = work.get("document_types", [])
        if not isinstance(types, list):
            return False
        normalized = {str(item).strip().lower() for item in types}
        if not normalized.intersection(self._ALLOWED_TYPES) or normalized.intersection(self._EXCLUDED_TYPES):
            return False
        count = work.get("author_count")
        if isinstance(count, bool) or not isinstance(count, int):
            # An omitted total is recoverable only when the author list is present;
            # this remains a full listed count, never a count of indexed people.
            authors = work.get("authors", [])
            unresolved = work.get("unresolved_count", 0)
            if not isinstance(authors, list) or isinstance(unresolved, bool) or not isinstance(unresolved, int):
                return False
            count = len(authors) + max(0, unresolved)
        if (count < self.filters.min_authors
                or (self.filters.max_authors is not None and count > self.filters.max_authors)):
            return False
        year = work.get("year")
        if isinstance(year, bool) or not isinstance(year, int):
            year = None
        if self.filters.year_start is not None or self.filters.year_end is not None:
            # The exporter has already chosen earliest documented date/year.  An
            # unknown date is intentionally excluded whenever a bound is active.
            if year is None:
                return False
            if self.filters.year_start is not None and year < self.filters.year_start:
                return False
            if self.filters.year_end is not None and year > self.filters.year_end:
                return False
        return True

    def _resolved_authors(self, work: dict[str, Any]) -> tuple[str, ...]:
        authors = work.get("authors", [])
        if not isinstance(authors, list):
            return ()
        # A repeated resolved ID on one record is one author in this person graph.
        return tuple(sorted({str(author) for author in authors if str(author) in self.people}))

    def _index_phd(self, records: Any) -> None:
        if not isinstance(records, list):
            return
        seen: set[tuple[str, str, str]] = set()
        for record in records:
            if not isinstance(record, dict):
                continue
            adviser, student = record.get("adviser"), record.get("student")
            if adviser is None or student is None:
                continue
            adviser, student = str(adviser), str(student)
            if adviser not in self.people or student not in self.people or adviser == student:
                continue
            key = (adviser, student, str(record.get("source_record", "")))
            if key in seen:
                continue
            seen.add(key)
            self.phd.append(record)
            self._phd_by_person[adviser].append(record)
            self._phd_by_person[student].append(record)
            self._phd_by_pair[tuple(sorted((adviser, student)))].append(record)
        self.phd.sort(key=self._phd_sort_key)
        for records_for_person in self._phd_by_person.values():
            records_for_person.sort(key=self._phd_sort_key)
        for records_for_pair in self._phd_by_pair.values():
            records_for_pair.sort(key=self._phd_sort_key)

    @staticmethod
    def _phd_sort_key(record: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            str(record.get("adviser", "")), str(record.get("student", "")),
            str(record.get("year", "")), str(record.get("source_record", "")),
        )

    @staticmethod
    def _pair(a: str, b: str) -> tuple[str, str]:
        return (a, b) if a < b else (b, a)

    def _pair_works(self, a: str, b: str) -> tuple[str, ...]:
        key = self._pair(a, b)
        cached = self._cache_get(self._pair_cache, key)
        if cached is not None:
            return cached
        shared = tuple(sorted(self._person_works.get(a, set()).intersection(self._person_works.get(b, set()))))
        self._cache_put(self._pair_cache, key, shared, self.MAX_PAIR_CACHE)
        return shared

    @staticmethod
    def _cache_get(cache: OrderedDict[Any, Any], key: Any) -> Any:
        try:
            value = cache.pop(key)
        except KeyError:
            return None
        cache[key] = value
        return value

    @staticmethod
    def _cache_put(cache: OrderedDict[Any, Any], key: Any, value: Any, limit: int) -> None:
        cache.pop(key, None)
        cache[key] = value
        while len(cache) > limit:
            cache.popitem(last=False)

    def _coauthor_neighbors(self, person_id: str, operations: list[int] | None = None) -> tuple[str, ...]:
        key = (person_id, False)
        if operations is None:
            cached = self._cache_get(self._neighbor_cache, key)
            if cached is not None:
                return cached
        candidates: set[str] = set()
        for work_id in self._person_works.get(person_id, set()):
            for other in self._resolved_authors(self.works[work_id]):
                if other != person_id:
                    candidates.add(other)
                    if operations is not None:
                        self._tick(operations)
        neighbors = tuple(sorted(other for other in candidates if len(self._pair_works(person_id, other)) >= self.filters.min_shared))
        if operations is None:
            self._cache_put(self._neighbor_cache, key, neighbors, self.MAX_NEIGHBOR_CACHE)
        return neighbors

    def _neighbors(self, person_id: str, include_phd: bool = True, operations: list[int] | None = None) -> tuple[str, ...]:
        key = (person_id, include_phd)
        if operations is None:
            cached = self._cache_get(self._neighbor_cache, key)
            if cached is not None:
                return cached
        neighbors = set(self._coauthor_neighbors(person_id, operations))
        if include_phd and self.filters.genealogy:
            for record in self._phd_by_person.get(person_id, []):
                other = str(record["student"] if str(record["adviser"]) == person_id else record["adviser"])
                neighbors.add(other)
        result = tuple(sorted(neighbors))
        if operations is None:
            self._cache_put(self._neighbor_cache, key, result, self.MAX_NEIGHBOR_CACHE)
        return result

    def _tick(self, operations: list[int]) -> None:
        operations[0] += 1
        if operations[0] > self.MAX_QUERY_OPERATIONS:
            raise GraphError("resource_limit", "query exceeded the graph expansion limit")

    def _edge(self, a: str, b: str) -> dict[str, Any] | None:
        work_ids = self._pair_works(a, b)
        works = [self.works[work_id] for work_id in work_ids] if len(work_ids) >= self.filters.min_shared else []
        # A documented doctoral relation remains useful context for an already
        # eligible coauthor edge even when genealogy is off. It must never
        # become a traversable edge or a ``phd`` type in that mode.
        phd_context = self._phd_by_pair.get(self._pair(a, b), [])
        traversable_phd = phd_context if self.filters.genealogy else []
        if not works and not traversable_phd:
            return None
        types: list[str] = []
        if works:
            types.append("coauthor")
        if traversable_phd:
            types.append("phd")
        return {"source": a, "target": b, "types": types, "shared_works": len(works), "works": works,
                "phd": phd_context if works else traversable_phd}

    def _base(self) -> dict[str, Any]:
        return {"version": self.version, "filters": self.filters.to_dict(), "coverage": self.snapshot.get("coverage", {})}

    def find_paths(self, source: str, target: str, alternatives: int = 3) -> dict[str, Any]:
        source, target = str(source), str(target)
        base = self._base()
        if source not in self.people or target not in self.people:
            return {"status": "not_indexed", "paths": [], "exact": True, "alternatives_truncated": False, "message": "One or both people are not indexed.", **base}
        if isinstance(alternatives, bool) or not isinstance(alternatives, int) or not 1 <= alternatives <= 3:
            raise GraphError("invalid_request", "alternatives must be between 1 and 3")
        if source == target:
            return {"status": "ok", "paths": [{"people": [self.people[source]], "hops": 0, "edges": []}], "exact": True, "alternatives_truncated": False, **base}

        operations = [0]
        # Testing one pair is O(their incident works), while expanding a giant
        # paper's entire author list is O(the paper size).  A direct relation is
        # already a provably shortest path.
        direct_edge = self._edge(source, target)
        if direct_edge is not None:
            return {"status": "ok", "paths": [{"people": [self.people[source], self.people[target]], "hops": 1, "edges": [direct_edge]}], "exact": True, "alternatives_truncated": False, **base}
        queue: deque[str] = deque([source])
        distance = {source: 0}
        parents: dict[str, list[str]] = defaultdict(list)
        target_distance: int | None = None
        alternatives_truncated = False
        parent_cap = max(12, alternatives * 4)
        try:
            while queue:
                current = queue.popleft()
                current_distance = distance[current]
                if target_distance is not None and current_distance >= target_distance:
                    continue
                for neighbor in self._neighbors(current, operations=operations):
                    self._tick(operations)
                    if neighbor not in distance:
                        distance[neighbor] = current_distance + 1
                        queue.append(neighbor)
                    if distance[neighbor] == current_distance + 1:
                        if len(parents[neighbor]) < parent_cap:
                            parents[neighbor].append(current)
                        else:
                            alternatives_truncated = True
                    if neighbor == target:
                        target_distance = current_distance + 1
                if len(distance) > self.MAX_PATH_NODES:
                    raise GraphError("resource_limit", "path search reached the indexed-node limit")
        except GraphError as error:
            if error.code == "resource_limit":
                return {"status": "resource_limit", "paths": [], "exact": False, "alternatives_truncated": False, "message": error.message, **base}
            raise
        if target not in distance:
            return {"status": "no_path", "paths": [], "exact": True, "alternatives_truncated": False, "message": "No path was found in this indexed snapshot under the selected filters. Broader INSPIRE coverage may contain a connection.", **base}

        sequences: list[list[str]] = []
        stack: list[tuple[str, list[str]]] = [(target, [target])]
        while stack and len(sequences) < alternatives:
            node, reversed_path = stack.pop()
            if node == source:
                sequences.append(list(reversed(reversed_path)))
                continue
            # Stack is LIFO: reverse push order preserves lexical predecessor
            # order while avoiding recursion limits on long collaboration chains.
            for parent in reversed(sorted(parents[node])):
                stack.append((parent, reversed_path + [parent]))
        paths = []
        for sequence in sequences:
            edges = [self._edge(left, right) for left, right in zip(sequence, sequence[1:])]
            paths.append({"people": [self.people[person_id] for person_id in sequence], "hops": len(sequence) - 1, "edges": [edge for edge in edges if edge is not None]})
        return {"status": "ok", "paths": paths, "exact": True, "alternatives_truncated": alternatives_truncated, **base}

    def profile(self, person_id: str) -> dict[str, Any]:
        person_id = str(person_id)
        if person_id not in self.people:
            raise GraphError("not_indexed", "person is not indexed")
        coauthors = self._coauthor_neighbors(person_id)
        combined = self._neighbors(person_id)
        collaborators = [
            {"person": self.people[other], "shared_works": len(self._pair_works(person_id, other))}
            for other in coauthors
        ]
        collaborators.sort(key=lambda item: (-item["shared_works"], str(item["person"].get("name", "")), str(item["person"].get("id", ""))))
        advisers = [record for record in self._phd_by_person.get(person_id, []) if str(record["student"]) == person_id]
        students = [record for record in self._phd_by_person.get(person_id, []) if str(record["adviser"]) == person_id]
        reachability: dict[str, Any] = {
            "status": "ok", "coauthor_component_size": None, "combined_component_size": None,
        }
        for field, include_phd in (("coauthor_component_size", False), ("combined_component_size", True)):
            try:
                reachability[field] = self._component_size(person_id, include_phd=include_phd)
            except GraphError as error:
                if error.code != "resource_limit":
                    raise
                reachability["status"] = "resource_limit"
                reachability["message"] = error.message
        return {
            "person": self.people[person_id],
            "indexed_publications": len(self._all_person_works.get(person_id, set())),
            "eligible_publications": len(self._person_works.get(person_id, set())),
            "collaborators": collaborators,
            "coauthor_count": len(coauthors),
            "combined_degree": len(combined),
            "advisers": advisers,
            "students": students,
            "reachability": reachability,
            **self._base(),
        }

    def _component_size(self, person_id: str, include_phd: bool) -> int:
        seen = {person_id}
        queue: deque[str] = deque([person_id])
        operations = [0]
        while queue:
            for neighbor in self._neighbors(queue.popleft(), include_phd, operations):
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
                    if len(seen) > self.MAX_PATH_NODES:
                        raise GraphError("resource_limit", "component traversal reached the indexed-node limit")
        return len(seen)

    def neighborhood(self, person_id: str, limit: int = 40) -> dict[str, Any]:
        person_id = str(person_id)
        if person_id not in self.people:
            raise GraphError("not_indexed", "person is not indexed")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= self.MAX_NEIGHBORHOOD_LIMIT:
            raise GraphError("invalid_request", f"limit must be between 1 and {self.MAX_NEIGHBORHOOD_LIMIT}")
        neighbors = self._neighbors(person_id)
        selected = [person_id, *neighbors[: max(0, limit - 1)]]
        # An ego neighborhood is deliberately a bounded star.  Computing every
        # edge between selected neighbours would turn a large collaboration into a
        # clique calculation despite the node limit.
        edges: list[dict[str, Any]] = []
        for other in selected[1:]:
            edge = self._edge(person_id, other)
            if edge is not None:
                edges.append(edge)
        edges.sort(key=lambda edge: (edge["source"], edge["target"]))
        return {"people": [self.people[item] for item in selected], "edges": edges, "truncated": len(neighbors) > len(selected) - 1, **self._base()}

    def _active_adjacency(self, include_phd: bool = True) -> dict[str, tuple[str, ...]]:
        """Return only non-isolates, while retaining the full population elsewhere.

        This lets a production snapshot retain thousands of isolated historical
        authors without making a centrality response falsely unavailable.  It does
        not change any score: isolates have degree, harmonic, and betweenness zero.
        """
        operations = [0]
        active: dict[str, tuple[str, ...]] = {}
        for person_id in sorted(self.people):
            neighbors = self._neighbors(person_id, include_phd, operations)
            if neighbors:
                active[person_id] = neighbors
                if len(active) > self.MAX_CENTRALITY_NODES:
                    raise GraphError("resource_limit", f"centrality is limited to {self.MAX_CENTRALITY_NODES} non-isolated indexed people")
        return active

    @staticmethod
    def _components(adjacency: dict[str, tuple[str, ...]]) -> list[list[str]]:
        remaining = set(adjacency)
        components: list[list[str]] = []
        while remaining:
            start = min(remaining)
            remaining.remove(start)
            component = [start]
            queue: deque[str] = deque([start])
            while queue:
                for neighbor in adjacency[queue.popleft()]:
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        component.append(neighbor)
                        queue.append(neighbor)
            components.append(sorted(component))
        return components

    @staticmethod
    def _component_work(component: list[str], adjacency: dict[str, tuple[str, ...]]) -> int:
        """Conservative BFS/Brandes work estimate for one connected component.

        Every source traversal visits its component's nodes and scans its full
        adjacency.  ``sum_degrees`` intentionally counts each undirected edge
        twice because breadth-first search observes both directed incidences.
        """
        nodes = len(component)
        return nodes * (nodes + sum(len(adjacency[person_id]) for person_id in component))

    def _require_centrality_work(self, work: int, operation: str) -> None:
        if work > self.MAX_CENTRALITY_WORK:
            raise GraphError(
                "resource_limit",
                f"{operation} estimated {work:,} graph operations, above the {self.MAX_CENTRALITY_WORK:,} limit",
            )

    @staticmethod
    def _bfs_distances(adjacency: dict[str, tuple[str, ...]], source: str) -> dict[str, int]:
        distance = {source: 0}
        queue: deque[str] = deque([source])
        while queue:
            current = queue.popleft()
            for neighbor in adjacency[current]:
                if neighbor not in distance:
                    distance[neighbor] = distance[current] + 1
                    queue.append(neighbor)
        return distance

    def _centrality_rows(self, values: dict[str, float], descending: bool = True) -> list[dict[str, Any]]:
        ordered = sorted(values, key=lambda person_id: ((-values[person_id]) if descending else values[person_id], str(self.people[person_id].get("name", "")), person_id))
        rows: list[dict[str, Any]] = []
        rank = 0
        prior: float | None = None
        for position, person_id in enumerate(ordered, 1):
            value = values[person_id]
            if prior is None or value != prior:
                rank = position
                prior = value
            rows.append({"person": self.people[person_id], "value": value, "rank": rank})
        return rows

    def centrality(self, metric: str = "degree", limit: int = 25) -> dict[str, Any]:
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 500:
            raise GraphError("invalid_request", "limit must be between 1 and 500")
        metric = str(metric).lower()
        if metric not in {"degree", "combined_degree", "harmonic", "betweenness", "eccentricity"}:
            raise GraphError("invalid_request", "unknown centrality metric")
        base = self._base()
        definitions = {
            "degree": "Unique eligible coauthors for each indexed person.",
            "combined_degree": "Unique neighbours joined by eligible coauthorship or a doctoral record.",
            "harmonic": "Sum of reciprocal shortest-path distances in the filtered undirected person graph, divided by N-1.",
            "betweenness": "Freeman-normalized betweenness in the filtered simple undirected person graph.",
            "eccentricity": "Maximum shortest-path distance within the largest non-isolated filtered component.",
        }
        try:
            if metric == "degree":
                # Degree needs no global adjacency.  Bound each person's local
                # incidence expansion without inheriting the active-graph limit
                # used by distance metrics. One counter still bounds the complete
                # request: a giant eligible paper cannot be expanded once per
                # author and silently form a full clique calculation.
                values: dict[str, float] = {}
                operations = [0]
                for person_id in self.people:
                    values[person_id] = float(len(self._coauthor_neighbors(person_id, operations=operations)))
                rows = self._centrality_rows(values)
                return {"status": "ok", "metric": metric, "definition": definitions[metric], "population": len(self.people), "scope": "all indexed people; eligible coauthorship only", "exact": True, "method": "lazy incidence pair counts", "computed_at": self._computed_at(), "rows": rows[:limit], **base}

            adjacency = self._active_adjacency(include_phd=True)
            active_n = len(adjacency)
            n = len(self.people)
            components = self._components(adjacency)
            source_work: dict[str, int] = {}
            total_component_work = 0
            for component in components:
                work_estimate = self._component_work(component, adjacency)
                total_component_work += work_estimate
                source_work.update({person_id: work_estimate // len(component) for person_id in component})
            if metric == "combined_degree":
                values = {person_id: float(len(adjacency.get(person_id, ()))) for person_id in self.people}
                rows = self._centrality_rows(values)
                return {"status": "ok", "metric": metric, "definition": definitions[metric], "population": n, "scope": "all indexed people; filtered undirected person graph", "exact": True, "method": "incidence-derived adjacency", "computed_at": self._computed_at(), "rows": rows[:limit], **base}

            if metric == "harmonic":
                self._require_centrality_work(total_component_work, "exact harmonic centrality")
                denominator = max(1, n - 1)
                values = {person_id: 0.0 for person_id in self.people}
                for person_id in adjacency:
                    values[person_id] = sum(1.0 / distance for distance in self._bfs_distances(adjacency, person_id).values() if distance) / denominator
                rows = self._centrality_rows(values)
                return {"status": "ok", "metric": metric, "definition": definitions[metric], "population": n, "scope": "all indexed people, including disconnected people as zero contribution", "exact": True, "method": "all-source breadth-first search", "computed_at": self._computed_at(), "rows": rows[:limit], **base}

            if metric == "betweenness":
                values = {person_id: 0.0 for person_id in self.people}
                if active_n <= self.MAX_EXACT_BETWEENNESS_NODES:
                    self._require_centrality_work(total_component_work, "exact betweenness")
                    # Normalization follows the complete indexed population, even
                    # though Brandes need not visit isolated vertices.
                    values.update(self._brandes_betweenness(adjacency, population=n))
                    exact = True
                    method = "Brandes exact unweighted algorithm"
                    approximation: dict[str, Any] | None = None
                else:
                    sample_size = min(self.BETWENNESS_SAMPLE_SOURCES, active_n)
                    sources = random.Random(self.BETWENNESS_SAMPLE_SEED).sample(sorted(adjacency), sample_size)
                    self._require_centrality_work(sum(source_work[source] for source in sources), "sampled betweenness")
                    values.update(self._brandes_betweenness(adjacency, population=n, sources=sources, estimate_population=active_n))
                    exact = False
                    method = "deterministic sampled Brandes estimator"
                    approximation = {
                        "source_count": sample_size,
                        "active_population": active_n,
                        "seed": self.BETWENNESS_SAMPLE_SEED,
                        "estimator": "source dependency totals scaled by active_population/source_count",
                        "uncertainty": "No confidence interval is calculated; close candidate rankings may change under another sample.",
                    }
                rows = self._centrality_rows(values)
                result = {"status": "ok", "metric": metric, "definition": definitions[metric], "population": n, "scope": "all indexed people; disconnected pairs contribute zero", "exact": exact, "method": method, "computed_at": self._computed_at(), "rows": rows[:limit], **base}
                if approximation is not None:
                    result["approximation"] = approximation
                    result["ranking_note"] = "Ranks are deterministic estimates; interpret close values as candidate ties."
                return result

            non_isolated_components = [component for component in components if len(component) > 1]
            if not non_isolated_components:
                return {"status": "ok", "metric": metric, "definition": definitions[metric], "population": len(self.people), "scope": "no non-isolated component exists", "exact": True, "method": "all-source breadth-first search", "computed_at": self._computed_at(), "rows": [], "radius": None, "centers": [], **base}
            largest = min((component for component in non_isolated_components if len(component) == max(map(len, non_isolated_components))), key=lambda component: component)
            self._require_centrality_work(self._component_work(largest, adjacency), "eccentricity")
            values = {person_id: float(max(self._bfs_distances(adjacency, person_id).values())) for person_id in largest}
            radius = min(values.values())
            centers = [self.people[person_id] for person_id in sorted(values) if values[person_id] == radius]
            rows = self._centrality_rows(values, descending=False)
            return {"status": "ok", "metric": metric, "definition": definitions[metric], "population": len(self.people), "scope": f"largest non-isolated component of {len(largest)} people; isolates and smaller components excluded", "exact": True, "method": "all-source breadth-first search", "computed_at": self._computed_at(), "rows": rows[:limit], "radius": radius, "centers": centers, **base}
        except GraphError as error:
            if error.code != "resource_limit":
                raise
            return {"status": "resource_limit", "metric": metric, "definition": definitions[metric], "population": len(self.people), "scope": "bounded graph calculation was not run to completion", "exact": False, "method": "unavailable within configured resource limits", "computed_at": self._computed_at(), "rows": [], "message": error.message, **base}

    @staticmethod
    def _brandes_betweenness(
        adjacency: dict[str, tuple[str, ...]],
        population: int | None = None,
        sources: list[str] | None = None,
        estimate_population: int | None = None,
    ) -> dict[str, float]:
        scores = dict.fromkeys(adjacency, 0.0)
        selected_sources = sorted(adjacency) if sources is None else sorted(sources)
        for source in selected_sources:
            stack: list[str] = []
            predecessors: dict[str, list[str]] = defaultdict(list)
            paths: dict[str, float] = {source: 1.0}
            distance: dict[str, int] = {source: 0}
            queue: deque[str] = deque([source])
            while queue:
                vertex = queue.popleft()
                stack.append(vertex)
                for neighbor in adjacency[vertex]:
                    if neighbor not in distance:
                        queue.append(neighbor)
                        distance[neighbor] = distance[vertex] + 1
                    if distance[neighbor] == distance[vertex] + 1:
                        paths[neighbor] = paths.get(neighbor, 0.0) + paths[vertex]
                        predecessors[neighbor].append(vertex)
            dependency = dict.fromkeys(stack, 0.0)
            while stack:
                vertex = stack.pop()
                for predecessor in predecessors[vertex]:
                    dependency[predecessor] += (paths[predecessor] / paths[vertex]) * (1.0 + dependency[vertex])
                if vertex != source:
                    scores[vertex] += dependency[vertex]
        n = population if population is not None else len(adjacency)
        if n <= 2:
            return {person_id: 0.0 for person_id in scores}
        # Undirected Brandes counts each pair twice; normalized NetworkX convention.
        scale = 1.0 / ((n - 1) * (n - 2))
        estimate_scale = 1.0
        if estimate_population is not None and selected_sources:
            estimate_scale = estimate_population / len(selected_sources)
        return {person_id: score * scale * estimate_scale for person_id, score in scores.items()}

    def ancestry(self, person_id: str, direction: str = "ancestors", limit: int = 100) -> dict[str, Any]:
        person_id = str(person_id)
        if person_id not in self.people:
            raise GraphError("not_indexed", "person is not indexed")
        if direction not in {"ancestors", "descendants"}:
            raise GraphError("invalid_request", "direction must be ancestors or descendants")
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= self.MAX_NEIGHBORHOOD_LIMIT:
            raise GraphError("invalid_request", f"limit must be between 1 and {self.MAX_NEIGHBORHOOD_LIMIT}")
        selected = {person_id}
        edge_records: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        queue: deque[str] = deque([person_id])
        truncated = False
        while queue:
            current = queue.popleft()
            records = self._phd_by_person.get(current, [])
            if direction == "ancestors":
                records = [record for record in records if str(record["student"]) == current]
                next_id = lambda record: str(record["adviser"])
            else:
                records = [record for record in records if str(record["adviser"]) == current]
                next_id = lambda record: str(record["student"])
            for record in records:
                other = next_id(record)
                if other not in selected and len(selected) >= limit:
                    truncated = True
                    continue
                edge_records[(str(record["adviser"]), str(record["student"]))].append(record)
                if other not in selected:
                    selected.add(other)
                    queue.append(other)
        edges = [
            {"source": adviser, "target": student, "types": ["phd"], "shared_works": 0, "works": [], "phd": sorted(records, key=self._phd_sort_key)}
            for (adviser, student), records in edge_records.items()
        ]
        edges.sort(key=lambda edge: (edge["source"], edge["target"]))
        return {"status": "ok", "person": self.people[person_id], "direction": direction, "people": [self.people[item] for item in sorted(selected)], "edges": edges, "truncated": truncated, **self._base()}

    def _computed_at(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
