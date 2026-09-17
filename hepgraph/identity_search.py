"""Resolve a typed name, ORCID or record ID to INSPIRE author records.

Identity resolution is the one place a search still consults INSPIRE *before*
the graph: the compact graph stores author identifiers and no names at all, so
there is nothing local to search.  Looking a person up is a bounded lookup, not
traversal, and it never grows with the size of the route being searched.

The query builder is deliberately conservative and is the same rule the live
engine used: raw INSPIRE query language from the UI is never forwarded.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

from .graph import GraphError
from .pipeline import PipelineError, _hits, sanitize_author, source_url


MAX_RESULTS = 25
_NAME_FIELDS = ("name.value", "name.name_variants", "name.preferred_name")


def author_search_query(value: str) -> str:
    """One conservative upstream query from an identity input.

    Numeric records and conventional ORCIDs use field queries; a name permits
    only literal letter/number tokens, which supports INSPIRE's "Hostert,
    Matheus" against a typed "Matheus Hostert" without admitting punctuation
    that would be read as query syntax.
    """
    query = unicodedata.normalize("NFC", value.strip())
    if re.fullmatch(r"[0-9]+", query):
        if not re.fullmatch(r"[1-9][0-9]{0,11}", query):
            raise GraphError("invalid_input", "An INSPIRE numeric author record ID must be positive.")
        return f"control_number:{query}"
    if re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", query, re.IGNORECASE):
        return f'ids.value:"{query.upper()}"'
    if any(ord(character) < 32 or ord(character) == 127 for character in query):
        raise GraphError("invalid_input", "Search must be a numeric INSPIRE ID, ORCID, or a plain name.")
    tokens = re.findall(r"[^\W_]+", query, re.UNICODE)
    if not tokens:
        raise GraphError("invalid_input", "Search must be a numeric INSPIRE ID, ORCID, or a plain name.")
    return " AND ".join(
        "(" + " OR ".join(f'{field}:"{token}"' for field in _NAME_FIELDS) + ")"
        for token in tokens)


def _person(recid: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {"id": recid, "name": payload.get("name") or f"INSPIRE author {recid}",
            "orcid": payload.get("orcid"),
            "affiliations": payload.get("affiliations") or [],
            "profile_status": payload.get("profile_status") or "profile",
            "source_url": source_url("authors", recid)}


def search(client: Any, query: str, *, provider: Any = None,
           limit: int = MAX_RESULTS) -> dict[str, Any]:
    """Resolve an identity, and say whether the graph actually holds it.

    ``indexed`` reports presence in the pinned graph. A person INSPIRE knows but
    the graph does not is still shown, because refusing to display them would
    imply they do not exist.
    """
    if not isinstance(query, str) or not 2 <= len(query.strip()) <= 120:
        raise GraphError("invalid_input", "Search must contain 2-120 characters.")
    try:
        response = client.fetch("authors", author_search_query(query), 1, limit)
        hits = _hits(response)
    except PipelineError as error:
        return {"status": "upstream_unavailable", "results": [], "source": "inspire",
                "message": str(error)}
    results = []
    for hit in hits[:limit]:
        try:
            recid, payload = sanitize_author(hit)
        except PipelineError:
            continue
        person = _person(str(recid), payload)
        person["indexed"] = (provider.resolve_author(person["id"]) is not None
                             if provider is not None else None)
        person["queryable"] = person["indexed"] is True
        results.append(person)
    status = "ambiguous" if len(results) > 1 else ("ok" if results else "not_found")
    return {"status": status, "results": results, "source": "inspire",
            "message": "" if results else "No INSPIRE author record matched that search."}
