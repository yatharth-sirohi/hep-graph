"""Adviser relations from Wikidata, where both people carry an INSPIRE id.

The web-research pilot showed why prose sources are hard: a weak model reading
a biography can invent the sentence it needed, and the reviewer has to re-do
the search to catch it. Wikidata is the opposite shape. It states ``doctoral
advisor`` (P184) as a link between two items, and many physics items also carry
``INSPIRE-HEP author ID`` (P2930). When both ends have one, the relation
arrives as *identifier to identifier* - there is no name to match, and nothing
for a model to hallucinate.

What still has to be checked, and is: a BAI like ``J.V.Lepore.2`` is not an
INSPIRE record id, so each one is resolved against INSPIRE itself, and a BAI
that does not resolve to exactly one record is dropped rather than guessed at.

Everything harvested here lands in ``graph_genealogy_research`` as a pending
lead with its Wikidata item as the citation. Wikidata is a good source, not
this project's source of truth, so nothing here becomes an INSPIRE relation.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from typing import Any, Iterable

from .genealogy_research import Lead, record

ENDPOINT = "https://query.wikidata.org/sparql"
AGENT = "hep-graph-genealogy/1.0 (https://hep-graph.vercel.app)"

#: Doctoral advisor, both sides identified in INSPIRE's own namespace. The
#: relation is recorded from either end - P184 on the student, P185 on the
#: adviser - and often only from one of them, so both are asked for.
QUERY = """
SELECT DISTINCT ?person ?personInspire ?personLabel ?adviser ?adviserInspire ?adviserLabel WHERE {
  { ?person wdt:P184 ?adviser . } UNION { ?adviser wdt:P185 ?person . }
  ?person wdt:P2930 ?personInspire .
  ?adviser wdt:P2930 ?adviserInspire .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

#: INSPIRE allows 15 requests per 5 seconds per address, shared with every
#: other crawl this project runs, so resolution asks for many ids at once.
BATCH = 25


def fetch_pairs(*, url: str = ENDPOINT, opener: Any = None) -> list[dict[str, str]]:
    """Ask Wikidata for every P184 relation whose two ends carry a P2930."""
    request = urllib.request.Request(
        f"{url}?format=json&query={urllib.parse.quote(QUERY)}",
        headers={"User-Agent": AGENT, "Accept": "application/sparql-results+json"})
    with (opener or urllib.request.urlopen)(request, timeout=180) as response:
        payload = json.load(response)
    pairs = []
    for row in payload["results"]["bindings"]:
        pairs.append({
            "item": row["person"]["value"],
            "student_bai": row["personInspire"]["value"],
            "student_label": row.get("personLabel", {}).get("value", ""),
            "adviser_bai": row["adviserInspire"]["value"],
            "adviser_label": row.get("adviserLabel", {}).get("value", "")})
    return pairs


def resolve_bais(bais: Iterable[str], client: Any, *, batch: int = BATCH) -> dict[str, int]:
    """Map each BAI to the one INSPIRE record carrying it.

    A BAI that matches no record, or more than one, is left out: this project
    does not resolve a person by anything weaker than their own identifier.
    """
    found: dict[str, int] = {}
    pending = sorted({str(value) for value in bais if value})
    for start in range(0, len(pending), batch):
        chunk = pending[start:start + batch]
        query = " OR ".join(f'ids.value:"{value}"' for value in chunk)
        response = client.search("authors", query, size=len(chunk) * 2,
                                 fields="control_number,ids")
        for hit in response.get("hits", {}).get("hits", []):
            metadata = hit.get("metadata", {})
            recid = metadata.get("control_number")
            for identifier in metadata.get("ids", []) or ():
                value = identifier.get("value")
                if value in chunk and recid is not None:
                    if value in found and found[value] != int(recid):
                        found[value] = 0          # ambiguous: refuse it below
                    else:
                        found.setdefault(value, int(recid))
    return {value: recid for value, recid in found.items() if recid}


def leads(pairs: list[dict[str, str]], resolved: dict[str, int]) -> list[Lead]:
    """Turn resolved pairs into leads, dropping any end we could not identify."""
    made: list[Lead] = []
    for pair in pairs:
        student = resolved.get(pair["student_bai"])
        adviser = resolved.get(pair["adviser_bai"])
        if not student or not adviser or student == adviser:
            continue
        item = pair["item"]
        quote = (f"Wikidata item {item.rsplit('/', 1)[-1]} records "
                 f"{pair['adviser_label'] or pair['adviser_bai']} as the doctoral advisor of "
                 f"{pair['student_label'] or pair['student_bai']}.")
        made.append(Lead(
            student_id=student, adviser_id=adviser,
            evidence_url=item.replace("http://www.wikidata.org/entity/",
                                      "https://www.wikidata.org/wiki/"),
            evidence_quote=quote,
            corroboration=(f"Both ends carry an INSPIRE author identifier on Wikidata "
                           f"({pair['student_bai']}, {pair['adviser_bai']}), each resolved "
                           f"against INSPIRE to exactly one record ({student}, {adviser}). "
                           f"No name matching was used."),
            confidence="high", degree="phd"))
    return made


def run(connection: Any, client: Any, *, overlay_id: str = "inspire-genealogy",
        researcher: str = "wikidata-p184", pause: float = 0.4) -> dict[str, Any]:
    pairs = fetch_pairs()
    time.sleep(pause)
    resolved = resolve_bais(
        [value for pair in pairs for value in (pair["student_bai"], pair["adviser_bai"])], client)
    stored = refused = 0
    reasons: dict[str, int] = {}
    for lead in leads(pairs, resolved):
        result = record(connection, lead, researcher=researcher, overlay_id=overlay_id)
        if result["stored"]:
            stored += 1
            continue
        refused += 1
        for problem in result["problems"]:
            reasons[problem] = reasons.get(problem, 0) + 1
    return {"pairs": len(pairs), "identifiers": len(resolved),
            "stored": stored, "refused": refused, "reasons": reasons}


class _IdentifierClient:
    """INSPIRE's author search, asked only for identifiers.

    ``InspireClient`` projects a fixed field list per collection; resolving BAIs
    needs just the record number and the ids, so the projection is narrowed for
    the duration of this crawl and put back afterwards.
    """

    def __init__(self) -> None:
        from .pipeline import InspireClient

        self.client = InspireClient()

    def search(self, collection: str, query: str, *, size: int = 25, fields: str = "") -> Any:
        from . import pipeline

        previous = pipeline.AUTHOR_FIELDS
        pipeline.AUTHOR_FIELDS = fields or "control_number,ids"
        try:
            return self.client.fetch(collection, query, 1, size)
        finally:
            pipeline.AUTHOR_FIELDS = previous


def main(argv: list[str] | None = None) -> int:
    import argparse
    import os

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL_UNPOOLED"))
    parser.add_argument("--overlay-id", default="inspire-genealogy")
    args = parser.parse_args(argv)
    if not args.database_url:
        parser.error("a direct database URL is required")

    import psycopg

    from .genealogy_research import SCHEMA

    with psycopg.connect(args.database_url, autocommit=True,
                         row_factory=psycopg.rows.dict_row) as connection:
        connection.execute(SCHEMA)
        summary = run(connection, _IdentifierClient(), overlay_id=args.overlay_id)
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
