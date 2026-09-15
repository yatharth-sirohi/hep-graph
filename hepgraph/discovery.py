"""Compact coauthor navigation. Nothing in this module is relationship evidence.

INSPIRE's author facet is a top-100 aggregation, not a complete bibliography.
It can cheaply suggest where to look; every suggested route must separately
pass the normal paper, doctoral-source and current-identity validation.
"""
from collections import deque


class Navigator:
    def __init__(self, source, target, *, base_neighbors=None,
                 max_nodes=20_000, max_links=100_000):
        self.source, self.target = str(source), str(target)
        self.base_neighbors = base_neighbors or (lambda _: ())
        self.max_nodes, self.max_links = max_nodes, max_links
        self.adjacency = {}
        self.queues = [deque([self.source]), deque([self.target])]
        self.seen = [{self.source}, {self.target}]
        self.known = {self.source, self.target}
        self.queried = set()
        self.truncated = set()
        self.blocked_edges = set()
        self.blocked_people = set()
        self.attempted_routes = set()
        self.pending = None
        self.links = 0
        self.capped = False
        self.last_side = 1
        self.side_streak = 0

    @staticmethod
    def pair(a, b):
        return tuple(sorted((str(a), str(b))))

    def _enqueue(self, side, person):
        if person in self.seen[side] or person in self.blocked_people:
            return
        if person not in self.known and len(self.known) >= self.max_nodes:
            self.capped = True
            return
        self.seen[side].add(person)
        self.known.add(person)
        self.queues[side].append(person)

    def next_person(self):
        """Retain the same pending cursor until a response is accepted."""
        if self.pending is not None:
            return self.pending[1]
        for side in (0, 1):
            while self.queues[side] and (self.queues[side][0] in self.queried
                                        or self.queues[side][0] in self.blocked_people):
                person = self.queues[side].popleft()
                for neighbor in self.adjacency.get(person, ()):
                    self._enqueue(side, neighbor)
        available = [side for side in (0, 1) if self.queues[side]]
        if not available:
            return None
        if len(available) == 1:
            side = available[0]
        elif self.side_streak >= 3:
            side = 1 - self.last_side
        else:
            side = min(available, key=lambda n: (len(self.queues[n]), n == self.last_side))
        self.side_streak = self.side_streak + 1 if side == self.last_side else 1
        self.last_side = side
        self.pending = (side, self.queues[side].popleft())
        return self.pending[1]

    def accept(self, person, authors, *, truncated=False):
        person = str(person)
        if self.pending is None or self.pending[1] != person:
            raise ValueError('A facet response must match its pending person.')
        side = self.pending[0]
        self.pending = None
        self.queried.add(person)
        if truncated:
            self.truncated.add(person)
        # Larger counts are a discovery priority only, never an edge weight or
        # proof of the minimum eligible shared-work threshold.
        for row in sorted(authors, key=lambda item: (-item['count'], item['id'])):
            other = row['id']
            if other == person or other in self.blocked_people:
                continue
            self.add_link(person, other)
            self._enqueue(side, other)

    def add_link(self, a, b):
        a, b = str(a), str(b)
        if a == b or self.pair(a, b) in self.blocked_edges:
            return
        if a in self.blocked_people or b in self.blocked_people:
            return
        if b in self.adjacency.get(a, ()):
            return
        missing = int(a not in self.adjacency) + int(b not in self.adjacency)
        if self.links >= self.max_links or len(self.adjacency) + missing > self.max_nodes:
            self.capped = True
            return
        self.adjacency.setdefault(a, set()).add(b)
        self.adjacency.setdefault(b, set()).add(a)
        self.links += 1
        for side in (0, 1):
            if a in self.seen[side]:
                self._enqueue(side, b)
            if b in self.seen[side]:
                self._enqueue(side, a)

    def reject_edge(self, a, b):
        self.blocked_edges.add(self.pair(a, b))

    def reject_person(self, person):
        self.blocked_people.add(str(person))

    def _neighbors(self, person):
        if person in self.blocked_people:
            return ()
        found = set(self.adjacency.get(person, ()))
        found.update(self.base_neighbors(person))
        return sorted(other for other in found if other not in self.blocked_people
                      and self.pair(person, other) not in self.blocked_edges)

    def route(self):
        """Bidirectional BFS through hints and the existing navigation graph."""
        if self.source in self.blocked_people or self.target in self.blocked_people:
            return None
        previous = [{self.source: None}, {self.target: None}]
        frontiers = [{self.source}, {self.target}]
        meeting = self.source if self.source == self.target else None
        while frontiers[0] and frontiers[1] and meeting is None:
            side = 0 if len(frontiers[0]) <= len(frontiers[1]) else 1
            following = set()
            for current in sorted(frontiers[side]):
                for neighbor in self._neighbors(current):
                    if neighbor in previous[side]:
                        continue
                    if len(previous[0]) + len(previous[1]) >= self.max_nodes:
                        self.capped = True
                        return None
                    previous[side][neighbor] = current
                    following.add(neighbor)
                    if neighbor in previous[1 - side]:
                        meeting = neighbor
                        break
                if meeting is not None:
                    break
            frontiers[side] = following
        if meeting is None:
            return None
        left, right = [meeting], []
        while previous[0][left[-1]] is not None:
            left.append(previous[0][left[-1]])
        current = previous[1][meeting]
        while current is not None:
            right.append(current)
            current = previous[1][current]
        path = list(reversed(left)) + right
        if tuple(path) in self.attempted_routes:
            return None
        self.attempted_routes.add(tuple(path))
        return path

    def coverage(self):
        return {'queried_profiles': len(self.queried),
                'candidate_people': len(self.adjacency), 'candidate_links': self.links,
                'truncated_profiles': len(self.truncated), 'complete': False,
                'rejected_links': len(self.blocked_edges), 'resource_limit': self.capped,
                'purpose': 'navigation_only; all displayed edges require separate evidence'}
