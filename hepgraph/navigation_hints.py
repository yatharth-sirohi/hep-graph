"""Small, discovery-only historical navigation hints.

These identifiers are not graph evidence.  Deep search must retrieve current
profiles and pair evidence before any suggested hop can enter a result.
"""
from __future__ import annotations


# Undirected navigation only.  The independently checked source works are
# recorded in docs/DEEP_SEARCH.md; they are deliberately not copied here as
# works, authorship occurrences, or graph edges.
HISTORICAL_NAVIGATION_PAIRS: tuple[tuple[str, str], ...] = (
    ("1010907", "1016635"),  # Einstein -- Bergmann
    ("1016635", "995796"),   # Bergmann -- Newman
    ("995796", "993859"),    # Newman -- Penrose
    ("993859", "1006450"),   # Penrose -- Hawking
    ("1006450", "989544"),   # Hawking -- Sciama
    ("989544", "993651"),    # Sciama -- Petcov
    ("993651", "1019647"),   # Petcov -- Pascoli
    ("1019647", "1621061"),  # Pascoli -- Hostert
)
