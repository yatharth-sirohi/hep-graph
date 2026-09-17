"""Telling a person from a form label, and cleaning the label off a person.

INSPIRE builds author records from thesis metadata, and that metadata is
entered by many hands. Three things come through as "authors" that are not
people: the literal heading a form printed (``Advisor(s)``), a placeholder
(``[unknown], [unknown]``), and the awarding institution itself
(``Fizyki, Wydział`` - Faculty of Physics, inverted like a surname).

A fourth case looks the same and is not: a *real* person with a role word stuck
to their name - ``Quadt, Betreuer: Arnulf`` is Arnulf Quadt, ``Hell, Betreuer:
Stefan`` is Stefan Hell. Those relations are true and must survive; only the
name needs cleaning. So the two are separated deliberately, and the rules are
narrow enough to explain: anything they are unsure about is left alone.
"""

from __future__ import annotations

import re

#: Words that name a role rather than a human.
ROLE_WORDS = ("advisor", "advisors", "adviser", "supervisor", "supervisors", "betreuer",
              "promotor", "copromotor", "co-promotor", "chair", "chairperson", "committee",
              "tutor", "referent", "korreferent")

#: Whole words that name an institution, after INSPIRE has inverted the name.
#: Matched as whole words, never as substrings: "Institutoris" is a surname and
#: "Universidad" is not.
INSTITUTION_WORDS = frozenset((
    "institut", "institute", "instituto", "institutet", "institution",
    "university", "universitat", "universitaet", "universitat", "universidad",
    "universidade", "universite", "universiteit", "univ",
    "wydzial", "fakultat", "faculte", "facultat", "facultad", "faculty",
    "departament", "department", "departamento", "dept",
    "school", "escuela", "ecole", "college", "programa", "laboratoire", "laboratory"))

#: The subset no human is surnamed. "College" and "School" are left out: they
#: are ordinary English surnames, and refusing one would delete a real relation.
INSTITUTION_HEADS = frozenset((
    "institut", "institute", "instituto", "institutet", "institution",
    "university", "universitat", "universitaet", "universidad", "universidade",
    "universite", "universiteit", "wydzial", "fakultat", "faculte", "facultat",
    "facultad", "departament", "departamento", "escuela", "ecole", "programa",
    "laboratoire"))

#: A name that is only a role heading, with the punctuation forms seen in the data.
_ROLE_ONLY = re.compile(
    r"^\W*(advisor|adviser|supervisor|chair|chairperson|committee|promotor|copromotor)"
    r"(\(s\)|s)?\b[\s,./]*(advisor|adviser|supervisor|chair|chairperson|committee|"
    r"\(s\)|n\.p\.|s)*[\s,./]*$", re.IGNORECASE)

_PLACEHOLDER = re.compile(r"^\W*(\[unknown\][\s,]*)+\W*$|^\W*(unknown|n/?a|none|no name)\W*$",
                          re.IGNORECASE)

#: Labels glued onto a real name, removed for display only.
_LABELS = (
    re.compile(r"\bBetreuer(in)?\s*:\s*", re.IGNORECASE),
    re.compile(r",?\s*supervisor(a)?\s+de\s+grado\b", re.IGNORECASE),
    re.compile(r",?\s*(Co-?)?[Ss]upervisor\s*:\s*", re.IGNORECASE),
    re.compile(r",?\s*Committee\s+Chairperson\b", re.IGNORECASE),
    re.compile(r"^Chairperson,\s*Graduate\s+Committee\s*:\s*", re.IGNORECASE),
    re.compile(r",?\s*Academic\s+co-?advisor\s*:\s*", re.IGNORECASE),
    re.compile(r",?\s*Internal/Supervisor\)?", re.IGNORECASE),
    re.compile(r",\s*Graduate\s+School\s+Representative\s*$", re.IGNORECASE),
    re.compile(r",\s*(Physics|Astronomy|Mathematics)?\s*Department\s*$", re.IGNORECASE),
    # "Lutz Schweikhard, Universitat Greifswald" is a person with their
    # university appended. The institution's own name must be followed by
    # something, so "de Cantabria, Universidad" - an inverted institution - is
    # left for non_person_reason to judge.
    re.compile(r",\s*(Universit\w+|University|Universidad|Universit[aà])\s+[A-Z][\w-]+\s*$"),
)


def _words(name: str) -> list[str]:
    return [word for word in re.split(r"[\s]+", name.strip()) if word]


def _tokens(text: str) -> list[str]:
    """Words, split on hyphens too and stripped to bare letters.

    "Humboldt-Universitat" has to yield "universitat"; "Institutoris" must yield
    only itself, which is why this compares whole tokens and never substrings.
    """
    import unicodedata

    flat = unicodedata.normalize("NFD", text)
    flat = "".join(ch for ch in flat if not unicodedata.combining(ch))
    # A stroked letter is not a combining mark, so NFD leaves it: Wydzial.
    for source, plain in (("ł", "l"), ("Ł", "L"), ("ø", "o"), ("Ø", "O"),
                          ("đ", "d"), ("Đ", "D"), ("ß", "ss")):
        flat = flat.replace(source, plain)
    return [token for token in re.split(r"[^A-Za-z]+", flat) if token]


def _is_institution(text: str) -> bool:
    return any(token.lower() in INSTITUTION_WORDS for token in _tokens(text)[:2])


def _looks_like_a_person(text: str) -> bool:
    """Two or more capitalised words reads as a human name, not a place.

    "Lutz Schweikhard" and "Valeri P.Frolov" pass; "de Cantabria", "Fizyki" and
    "Berlin" do not. It is deliberately easy to pass: the cost of calling an
    institution a person is one odd box on a map, and the cost of calling a
    person an institution is deleting a true relation.
    """
    capitals = [token for token in re.split(r"[^\w]+", text)
                if token[:1].isupper() and token.lower() not in INSTITUTION_WORDS
                and token.lower() not in ROLE_WORDS]
    return len(capitals) >= 2


def non_person_reason(name: str | None) -> str | None:
    """Why this name cannot be a person, or None to leave it alone.

    Call it on a name that has already been through :func:`clean_name`: a label
    like "Chairperson, Graduate Committee: Neil J.Cornish" reads as a role until
    the label comes off, and Neil Cornish is a real adviser.
    """
    if name is None:
        return None
    text = str(name).strip()
    if not text:
        return None
    if _ROLE_ONLY.match(text):
        return "a form heading, not a name"
    if _PLACEHOLDER.match(text):
        return "a placeholder, not a name"
    if len(_words(text)) >= 8 and re.search(r"dissertation|thesis|comments welcome", text, re.I):
        return "a sentence about a document, not a name"

    # INSPIRE inverts a name around its last comma, so an institution arrives as
    # "de Cantabria, Universidad": the given-name slot holds the institution
    # word. A person who merely lists their university - "Shu Li, Shanghai Jiao
    # Tong University" - has a real given name in that slot and is kept.
    surname, comma, given = text.rpartition(",")
    if comma:
        # INSPIRE inverts a name around its last comma, which moves an
        # institution's head noun to the front of the given-name slot:
        # "Universidad de Cantabria" -> "de Cantabria, Universidad". A person
        # who merely appended their university - "Povinec, Pavel Comenius
        # University" - has their own given name there instead. Both halves
        # have to agree before anything is refused.
        tokens = _tokens(given)
        inverted = bool(tokens) and tokens[0].lower() in INSTITUTION_HEADS
        if inverted and not _looks_like_a_person(surname):
            return "an institution, not a person"
        # Nobody's surname *is* the bare word "Institut" or "Universidad",
        # though "Institutoris" is a surname - hence whole tokens, not prefixes.
        head = _tokens(surname)[:1]
        if head and head[0].lower() in INSTITUTION_HEADS:
            return "an institution, not a person"
        first = _words(surname)[:1]
        if (first and first[0].strip(".,").lower() in ROLE_WORDS
                and not _looks_like_a_person(given)
                and all(word.strip(".,()/").lower() in ROLE_WORDS or not word.strip(".,()/")
                        for word in re.split(r"[\s/]+", given) if word)):
            # "Chair, Advisor/Supervisor/Committee" is a heading;
            # "Chair, Noureddine" is a person whose surname happens to be Chair.
            return "a role word where the surname should be"
    elif _is_institution(text):
        return "an institution, not a person"
    return None


def clean_name(name: str | None) -> str | None:
    """Strip a role label off a real person's name; leave everything else alone."""
    if name is None:
        return None
    text = str(name)
    for pattern in _LABELS:
        text = pattern.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip(" ,;:")
    # "Quadt,  Arnulf" -> "Quadt, Arnulf"
    text = re.sub(r"\s*,\s*", ", ", text).strip()
    return text or str(name).strip()
