"""Telling a person from a form label.

Every string here was found on the live map, so the cases are real ones. The
rule that matters most is the one that keeps a person: a real adviser with a
role word stuck to their name must survive, because their relation is true.
"""

from __future__ import annotations

import pytest

from hepgraph.person_names import clean_name, non_person_reason


def judge(raw):
    """What the pipeline does: clean the label off, then judge what is left."""
    cleaned = clean_name(raw)
    return non_person_reason(cleaned), cleaned


@pytest.mark.parametrize("raw", [
    "Advisor(s)", "Supervisor(s)", "Chair, Advisor/Supervisor/Committee", "Copromotor, N.P.",
])
def test_a_form_heading_is_not_a_person(raw):
    assert judge(raw)[0] is not None


@pytest.mark.parametrize("raw", ["[unknown], [unknown]", "unknown", "N/A"])
def test_a_placeholder_is_not_a_person(raw):
    assert judge(raw)[0] is not None


@pytest.mark.parametrize("raw", [
    "Fizyki, Wydział",                                   # Faculty of Physics, inverted
    "de Cantabria, Universidad",
    "de Física, Universitat de Barcelona. Facultat",
    "Science, University of Lethbridge. Faculty of Arts and",
    "1 Institut für Astroteilchenphysik (IAP), Karlsruher Institut für Technologie (KIT)",
])
def test_an_institution_is_not_a_person(raw):
    assert judge(raw)[0] == "an institution, not a person"


@pytest.mark.parametrize("raw,expected", [
    ("Quadt, Betreuer: Arnulf", "Quadt, Arnulf"),
    ("Alen Alexanderian, Graduate School Representative", "Alen Alexanderian"),
    ("Valeri P.Frolov, Physics Department", "Valeri P.Frolov"),
    ("Lutz Schweikhard, Universität Greifswald", "Lutz Schweikhard"),
    ("Hell, Betreuer: Stefan", "Hell, Stefan"),
    ("Salgado Arias, Patricio, supervisor de grado", "Salgado Arias, Patricio"),
    ("Chairperson, Graduate Committee: Neil J.Cornish", "Neil J.Cornish"),
    ("Carl Mummert, Committee Chairperson", "Carl Mummert"),
])
def test_a_real_adviser_keeps_their_relation_and_loses_the_label(raw, expected):
    reason, cleaned = judge(raw)
    assert reason is None, f"{raw} is a real person"
    assert cleaned == expected


@pytest.mark.parametrize("raw", [
    "Einstein, Albert", "Lüst, Dieter", "Müller, Thomas",
    # Every one of these was wrongly refused by an earlier draft of the rules,
    # which is the failure that matters: refusing a person deletes a true
    # relation, while admitting an institution only draws an odd box.
    "Chair, Noureddine",                       # a surname that is also a role word
    "Povinec, Pavel Comenius University",      # a person who appended their university
    "Institutoris, Marek",          # a surname that merely starts like "institute"
    "Schoolcraft, Jane", "College, Mary",
    "Shu Li, Shanghai Jiao Tong University",   # a person who listed their university
    "Povinec, Pavel Comenius University",
    "Lenzi Piergiulio (Università, Firenze (IT))",
])
def test_a_person_is_left_alone(raw):
    reason, cleaned = judge(raw)
    assert reason is None, f"{raw} was wrongly refused as {reason}"
    assert cleaned == raw.strip()


def test_a_sentence_about_the_document_is_not_a_person():
    raw = "Doctoral dissertation, contains also unpublished material. Comments welcome!"
    assert judge(raw)[0] == "a sentence about a document, not a name"


def test_nothing_is_decided_about_an_empty_or_missing_name():
    assert non_person_reason(None) is None and non_person_reason("") is None
    assert clean_name(None) is None


@pytest.mark.parametrize("raw", [
    "Berlin, Humboldt-Universität zu",     # head noun is not first in the given slot
    "de Física Quàntica i Astrofísica, Universitat de Barcelona. Departament",
])
def test_some_institutions_are_admitted_on_purpose(raw):
    """The rules err towards admitting, and this records the price of that.

    Refusing one of these would mean refusing "Povinec, Pavel Comenius
    University" and "Chair, Noureddine" too, which deletes true relations. An
    institution drawn as a box is a blemish; a deleted relation is a false
    claim about a person, so the blemish is the better failure.
    """
    assert non_person_reason(clean_name(raw)) is None
