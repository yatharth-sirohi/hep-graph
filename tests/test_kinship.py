"""Naming a relationship from two distances.

The cases are read off a probate relationship chart, which is the vocabulary
the feature is meant to match.
"""

from __future__ import annotations

import pytest

from hepgraph.kinship import best_meeting_point, describe


def label(up, down):
    return describe(up, down)["label"]


def test_a_direct_line_upward_is_named_by_generation():
    assert label(0, 1) == "academic adviser"
    assert label(0, 2) == "academic grandadviser"
    assert label(0, 3) == "academic great-grandadviser"
    assert label(0, 5) == "academic great-great-great-grandadviser"


def test_a_direct_line_downward_mirrors_it():
    assert label(1, 0) == "academic student"
    assert label(3, 0) == "academic great-grandstudent"


def test_sharing_an_adviser_makes_academic_siblings():
    assert label(1, 1) == "academic siblings"
    assert describe(1, 1)["explanation"] == "They share an adviser."


def test_cousins_count_from_the_shared_ancestor():
    assert label(2, 2) == "academic first cousins"
    assert label(3, 3) == "academic second cousins"
    assert label(4, 4) == "academic third cousins"


def test_an_uneven_climb_is_removed_not_renamed():
    assert label(2, 3) == "academic first cousins, once removed"
    assert label(3, 5) == "academic second cousins, twice removed"


def test_the_sibling_of_someones_adviser_is_a_sibling_removed():
    """The chart's own word for it, and it avoids gendering real people."""
    assert label(1, 2) == "academic siblings, once removed"
    assert label(1, 4) == "academic siblings, three times removed"


def test_the_same_person_is_said_plainly():
    assert label(0, 0) == "the same person"


def test_a_negative_distance_is_refused_rather_than_named():
    with pytest.raises(ValueError):
        describe(-1, 2)


# ------------------------------------------------------- choosing the ancestor

def test_the_nearest_shared_ancestor_wins():
    """A DAG gives several; the tightest true statement is the closest one."""
    found = best_meeting_point({10: 1, 20: 2, 30: 3}, {10: 4, 20: 2, 30: 3})
    assert found == (20, 2, 2)


def test_descent_is_found_by_the_same_rule():
    """A person is their own ancestor at distance zero."""
    found = best_meeting_point({5: 0, 9: 1}, {5: 2, 9: 3})
    assert found == (5, 0, 2)
    assert label(0, 2) == "academic grandadviser"


def test_no_shared_ancestor_is_reported_as_none_not_guessed():
    assert best_meeting_point({1: 1}, {2: 1}) is None


def test_ties_are_broken_deterministically():
    assert best_meeting_point({7: 2, 4: 2}, {7: 2, 4: 2})[0] == 4


# ------------------------------------------- connections that are not descent

def test_a_path_that_turns_back_is_named_by_its_joins():
    from hepgraph.kinship import describe_link

    # up, up, down, up: the third step falls to someone who then has a second
    # adviser - one person studying under both sides joins the two families.
    found = describe_link(["up", "up", "down", "up"])
    assert found["label"] == "connected through 4 supervision links"
    assert "1 point" in found["explanation"]
    assert "not a line of descent" in found["explanation"].lower()


def test_a_single_link_reads_in_the_singular():
    from hepgraph.kinship import describe_link
    assert describe_link(["up"])["label"] == "connected through 1 supervision link"


def test_two_joins_are_counted_separately():
    from hepgraph.kinship import describe_link
    found = describe_link(["up", "down", "up", "down", "up"])
    assert "2 points" in found["explanation"]
