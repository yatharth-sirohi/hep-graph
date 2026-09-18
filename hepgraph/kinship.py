"""Naming the relationship between two people in the adviser forest.

A shortest path already tells you two researchers are connected. A family tree
can say something better: *how* they are related. The vocabulary is the one on
a probate relationship chart - siblings, cousins, removals - and it falls out
of one number each: how far each person stands below the nearest ancestor they
share.

Two conventions are deliberate:

* The terms stay neutral. "Cousin" and "sibling" are; "aunt" and "nephew" are
  not, and these are real people. The chart's own word, *removed*, covers that
  case exactly: sharing an adviser with someone's adviser is being their
  academic sibling once removed.
* Supervision is a DAG, not a tree, so two people can share several ancestors.
  The nearest one is chosen, and ties are broken by the shorter climb, so the
  answer is the tightest true statement rather than the first one found.

Kinship is not the whole story, and the data says so: of 200 random pairs drawn
from the largest family, **one** shared an ancestor. INSPIRE records an adviser
for only a small share of physicists, so the recorded lines are short, and what
holds a family together is people with *two* advisers - each one joining two
lines the way a marriage joins two families. A pair with no common ancestor is
therefore usually still connected, just not by descent, and saying so is more
honest and more interesting than "not related".
"""

from __future__ import annotations

ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth", "seventh",
            "eighth", "ninth", "tenth")
REMOVALS = ("", "once removed", "twice removed", "three times removed",
            "four times removed", "five times removed", "six times removed")


def _ordinal(number: int) -> str:
    return ORDINALS[number - 1] if 1 <= number <= len(ORDINALS) else f"{number}th"


def _removed(steps: int) -> str:
    return REMOVALS[steps] if steps < len(REMOVALS) else f"{steps} times removed"


def _ancestor_word(steps: int, *, upward: bool) -> str:
    """adviser, grandadviser, great-grandadviser, ... and the mirror downwards."""
    stem = "adviser" if upward else "student"
    if steps == 1:
        return stem
    return "great-" * (steps - 2) + "grand" + stem


def describe(up: int, down: int) -> dict[str, str]:
    """Name the relationship, given each person's distance to a shared ancestor.

    ``up`` is how far the first person stands below that ancestor and ``down``
    how far the second does. Zero means the ancestor *is* that person.
    """
    up, down = int(up), int(down)
    if up < 0 or down < 0:
        raise ValueError("distances cannot be negative")
    if up == 0 and down == 0:
        return {"label": "the same person",
                "explanation": "These are the same person."}
    if up == 0:
        word = _ancestor_word(down, upward=True)
        return {"label": f"academic {word}",
                "explanation": f"The first is the academic {word} of the second: "
                               f"{'a direct line of ' + str(down) + ' supervisions' if down > 1 else 'their adviser'}."}
    if down == 0:
        word = _ancestor_word(up, upward=False)
        return {"label": f"academic {word}",
                "explanation": f"The first is the academic {word} of the second: "
                               f"{'a direct line of ' + str(up) + ' supervisions' if up > 1 else 'their student'}."}
    if up == 1 and down == 1:
        return {"label": "academic siblings",
                "explanation": "They share an adviser."}
    if min(up, down) == 1:
        steps = abs(up - down)
        return {"label": f"academic siblings, {_removed(steps)}",
                "explanation": "One shares an adviser with the other's "
                               f"{_ancestor_word(steps, upward=True)}."}
    degree = min(up, down) - 1
    steps = abs(up - down)
    label = f"academic {_ordinal(degree)} cousins"
    if steps:
        label += f", {_removed(steps)}"
    return {"label": label,
            "explanation": "Their academic lines meet at a shared ancestor "
                           f"{up} and {down} supervisions above them."}


def best_meeting_point(up_distances: dict[int, int],
                       down_distances: dict[int, int]) -> tuple[int, int, int] | None:
    """Pick the nearest ancestor two people share: (person, up, down).

    A person counts as their own ancestor at distance zero, so a direct line of
    descent is found by the same rule as a cousinhood. Ties prefer the shorter
    total climb, then the shorter single climb, then the smaller id, so the
    answer never depends on row order.
    """
    shared = set(up_distances) & set(down_distances)
    if not shared:
        return None
    best = min(shared, key=lambda person: (max(up_distances[person], down_distances[person]),
                                           up_distances[person] + down_distances[person],
                                           person))
    return best, up_distances[best], down_distances[best]


def describe_link(steps: list[str]) -> dict[str, str]:
    """Name a connection that is not a line of descent.

    ``steps`` reads along the path, "up" towards an adviser and "down" towards
    a student. A path that only rises and then falls has a common ancestor and
    belongs to :func:`describe`; anything else turns back on itself at someone
    who studied under both sides, and that person is what joins the families.
    """
    joins = sum(1 for before, after in zip(steps, steps[1:])
                if before == "down" and after == "up")
    links = len(steps)
    return {"label": f"connected through {links} supervision link{'' if links == 1 else 's'}",
            "explanation": (
                "Not a line of descent: neither is an academic ancestor of the other, and "
                "they share no recorded ancestor. Their lines are joined "
                + (f"at {joins} point{'' if joins == 1 else 's'} where someone studied under "
                   "both sides" if joins else "by the chain below")
                + ", the way a marriage joins two families.")}
