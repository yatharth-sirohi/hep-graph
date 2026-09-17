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

A BAI is also not always right. Wikidata gives Niels Bohr ``N.Bohr.1`` and Lev
Landau ``L.D.Landau.1``; INSPIRE has neither, so both were dropped and the
chains above them stopped dead. INSPIRE's own records carry a ``WIKIPEDIA``
identifier - Landau's says ``Lev_Landau`` - and a Wikipedia article belongs to
exactly one Wikidata item. That is a second bridge between the two databases,
made of identifiers on both sides, and it reaches precisely the historical
physicists a BAI tends to miss.

Everything harvested here lands in ``graph_genealogy_research`` as a pending
lead with its Wikidata item as the citation. Wikidata is a good source, not
this project's source of truth, so nothing here becomes an INSPIRE relation.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Iterable

from .genealogy_research import Lead, record

ENDPOINT = "https://query.wikidata.org/sparql"
AGENT = "hep-graph-genealogy/1.0 (https://hep-graph.vercel.app)"

#: Doctoral advisor, with whatever INSPIRE identifier each end carries. The
#: relation is recorded from either end - P184 on the student, P185 on the
#: adviser - and often only from one of them, so both are asked for. An end
#: with no BAI is kept here and resolved later through the Wikipedia bridge.
#: Asked as four narrow patterns rather than one broad one: the combined query
#: - either direction, either end carrying an identifier - times out at the
#: public endpoint, while each of these returns in seconds.
_PATTERNS = (
    "?person wdt:P184 ?adviser . ?person wdt:P2930 ?personInspire .",
    "?person wdt:P184 ?adviser . ?adviser wdt:P2930 ?adviserInspire .",
    "?adviser wdt:P185 ?person . ?person wdt:P2930 ?personInspire .",
    "?adviser wdt:P185 ?person . ?adviser wdt:P2930 ?adviserInspire .",
)

QUERY = """
SELECT DISTINCT ?person ?personInspire ?personLabel ?adviser ?adviserInspire ?adviserLabel WHERE {
  %(pattern)s
  OPTIONAL { ?person wdt:P2930 ?personInspire }
  OPTIONAL { ?adviser wdt:P2930 ?adviserInspire }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

#: The same relation among the people INSPIRE has tied to a Wikipedia article,
#: for chains that run entirely above the BAI frontier - Bohr and his own
#: adviser both sit here, and neither has a BAI that resolves.
BRIDGED_QUERY = """
SELECT DISTINCT ?person ?personInspire ?personLabel ?adviser ?adviserInspire ?adviserLabel WHERE {
  VALUES ?anchor { %(values)s }
  { ?anchor wdt:P184 ?other } UNION { ?other wdt:P185 ?anchor }
  BIND(IF(EXISTS { ?anchor wdt:P184 ?other }, ?anchor, ?other) AS ?person)
  BIND(IF(EXISTS { ?anchor wdt:P184 ?other }, ?other, ?anchor) AS ?adviser)
  OPTIONAL { ?person wdt:P2930 ?personInspire }
  OPTIONAL { ?adviser wdt:P2930 ?adviserInspire }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

#: Authors INSPIRE has tied to a Wikipedia article. About 900 - small, but it is
#: the set that sits at the top of the long chains.
WIKIPEDIA_QUERY = "ids.schema:WIKIPEDIA"

#: INSPIRE allows 15 requests per 5 seconds per address, shared with every
#: other crawl this project runs, so resolution asks for many ids at once.
BATCH = 25

#: Wikidata's entity API takes fifty titles per call.
TITLE_BATCH = 50


def _sparql(query: str, *, url: str = ENDPOINT, opener: Any = None) -> list[dict[str, Any]]:
    request = urllib.request.Request(
        f"{url}?format=json&query={urllib.parse.quote(query)}",
        headers={"User-Agent": AGENT, "Accept": "application/sparql-results+json"})
    with (opener or urllib.request.urlopen)(request, timeout=300) as response:
        return json.load(response)["results"]["bindings"]


def _row(binding: dict[str, Any]) -> dict[str, str]:
    return {
        "item": binding["person"]["value"],
        "student_qid": binding["person"]["value"].rsplit("/", 1)[-1],
        "student_bai": binding.get("personInspire", {}).get("value", ""),
        "student_label": binding.get("personLabel", {}).get("value", ""),
        "adviser_qid": binding["adviser"]["value"].rsplit("/", 1)[-1],
        "adviser_bai": binding.get("adviserInspire", {}).get("value", ""),
        "adviser_label": binding.get("adviserLabel", {}).get("value", "")}


def wikipedia_titles(client: Any) -> dict[str, int]:
    """Every INSPIRE author record that names a Wikipedia article, title -> recid."""
    found: dict[str, int] = {}
    page = 1
    while True:
        response = client.search("authors", WIKIPEDIA_QUERY, size=250, page=page,
                                 fields="control_number,ids")
        hits = response.get("hits", {}).get("hits", [])
        if not hits:
            return found
        for hit in hits:
            metadata = hit.get("metadata", {})
            recid = metadata.get("control_number")
            for identifier in metadata.get("ids", []) or ():
                if identifier.get("schema") == "WIKIPEDIA" and recid is not None:
                    title = str(identifier.get("value", "")).replace("_", " ").strip()
                    if title:
                        found.setdefault(title, int(recid))
        page += 1


def _site_and_title(stored: str) -> tuple[str, str]:
    """INSPIRE writes a foreign-language article as "de:Fritz Coester"."""
    match = re.match(r"^([a-z]{2,3}):(.+)$", stored)
    if match:
        return f"{match.group(1)}wiki", match.group(2).strip()
    return "enwiki", stored


def titles_to_items(titles: dict[str, int], *, opener: Any = None) -> dict[str, int]:
    """Map each Wikipedia article to its Wikidata item: QID -> INSPIRE recid.

    An article belongs to exactly one Wikidata item, so this is a join on
    identifiers rather than a name match. The response comes back keyed by item,
    so it is traced back through the item's own sitelink; anything that cannot
    be traced back is dropped rather than attached to a guess.
    """
    bridge: dict[str, int] = {}
    by_site: dict[str, dict[str, int]] = {}
    for stored, recid in titles.items():
        site, title = _site_and_title(stored)
        by_site.setdefault(site, {})[title] = recid
    for site, wanted in by_site.items():
        names = sorted(wanted)
        for start in range(0, len(names), TITLE_BATCH):
            chunk = names[start:start + TITLE_BATCH]
            query = urllib.parse.urlencode({
                "action": "wbgetentities", "format": "json", "sites": site,
                "props": "sitelinks", "sitefilter": site, "titles": "|".join(chunk)})
            request = urllib.request.Request(f"https://www.wikidata.org/w/api.php?{query}",
                                             headers={"User-Agent": AGENT})
            try:
                with (opener or urllib.request.urlopen)(request, timeout=120) as response:
                    payload = json.load(response)
            except Exception:
                continue
            for qid, entity in (payload.get("entities", {}) or {}).items():
                if not qid.startswith("Q") or "missing" in entity:
                    continue
                linked = (entity.get("sitelinks") or {}).get(site, {}).get("title")
                if linked in wanted:
                    bridge[qid] = wanted[linked]
            time.sleep(0.2)
    return bridge


def build_bridge(client: Any, *, opener: Any = None) -> dict[str, int]:
    """Wikidata item -> INSPIRE record, via INSPIRE's own Wikipedia identifiers."""
    return titles_to_items(wikipedia_titles(client), opener=opener)


def fetch_pairs(*, url: str = ENDPOINT, opener: Any = None,
                bridged: dict[str, int] | None = None) -> list[dict[str, str]]:
    """Every adviser relation with an INSPIRE identifier at either end."""
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for pattern in _PATTERNS:
        for binding in _sparql(QUERY % {"pattern": pattern}, url=url, opener=opener):
            row = _row(binding)
            key = (row["student_qid"], row["adviser_qid"])
            if key not in seen:
                seen.add(key)
                rows.append(row)
        time.sleep(0.5)
    anchors = sorted(bridged or ())
    for start in range(0, len(anchors), 200):
        values = " ".join(f"wd:{qid}" for qid in anchors[start:start + 200])
        for binding in _sparql(BRIDGED_QUERY % {"values": values}, url=url, opener=opener):
            row = _row(binding)
            if (row["student_qid"], row["adviser_qid"]) not in seen:
                seen.add((row["student_qid"], row["adviser_qid"]))
                rows.append(row)
        time.sleep(0.5)
    return rows


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


def leads(pairs: list[dict[str, str]], resolved: dict[str, int],
          bridged: dict[str, int] | None = None) -> list[Lead]:
    """Turn resolved pairs into leads, dropping any end we could not identify.

    An end is identified by its BAI when that resolves, and otherwise by the
    Wikipedia article INSPIRE itself put on the record. Never by its name.
    """
    bridged = bridged or {}
    made: list[Lead] = []
    for pair in pairs:
        how = []

        def side(which: str) -> int | None:
            recid = resolved.get(pair.get(f"{which}_bai", ""))
            if recid:
                how.append(f"{which} by INSPIRE identifier {pair[f'{which}_bai']}")
                return recid
            recid = bridged.get(pair.get(f"{which}_qid", ""))
            if recid:
                how.append(f"{which} by the Wikipedia article on INSPIRE record {recid}")
                return recid
            return None

        student, adviser = side("student"), side("adviser")
        if not student or not adviser or student == adviser:
            continue
        item = pair["item"]
        quote = (f"Wikidata item {item.rsplit('/', 1)[-1]} records "
                 f"{pair['adviser_label'] or pair['adviser_qid']} as the doctoral advisor of "
                 f"{pair['student_label'] or pair['student_qid']}.")
        made.append(Lead(
            student_id=student, adviser_id=adviser,
            evidence_url=item.replace("http://www.wikidata.org/entity/",
                                      "https://www.wikidata.org/wiki/"),
            evidence_quote=quote,
            corroboration=("Both ends resolved to exactly one INSPIRE record - "
                           + "; ".join(how) + ". No name matching was used."),
            confidence="high", degree="phd"))
    return made


def collect(client: Any, *, pause: float = 0.4) -> tuple[list[Lead], dict[str, Any]]:
    """Do all of the network work and return the leads it produced.

    Kept separate from storing them because this takes minutes, and a database
    connection opened before it is liable to be closed underneath us.
    """
    bridged = build_bridge(client)
    time.sleep(pause)
    pairs = fetch_pairs(bridged=bridged)
    time.sleep(pause)
    resolved = resolve_bais(
        [value for pair in pairs for value in (pair["student_bai"], pair["adviser_bai"])], client)
    return leads(pairs, resolved, bridged), {
        "pairs": len(pairs), "identifiers": len(resolved), "wikipedia_bridge": len(bridged)}


def store(connection: Any, found: list[Lead], *, overlay_id: str = "inspire-genealogy",
          researcher: str = "wikidata-p184") -> dict[str, Any]:
    stored = refused = 0
    reasons: dict[str, int] = {}
    reasons: dict[str, int] = {}
    for lead in found:
        result = record(connection, lead, researcher=researcher, overlay_id=overlay_id)
        if result["stored"]:
            stored += 1
            continue
        refused += 1
        for problem in result["problems"]:
            reasons[problem] = reasons.get(problem, 0) + 1
    return {"stored": stored, "refused": refused, "reasons": reasons}


def run(connection: Any, client: Any, *, overlay_id: str = "inspire-genealogy",
        researcher: str = "wikidata-p184", pause: float = 0.4) -> dict[str, Any]:
    found, stats = collect(client, pause=pause)
    return stats | store(connection, found, overlay_id=overlay_id, researcher=researcher)


class _IdentifierClient:
    """INSPIRE's author search, asked only for identifiers.

    ``InspireClient`` projects a fixed field list per collection; resolving BAIs
    needs just the record number and the ids, so the projection is narrowed for
    the duration of this crawl and put back afterwards.
    """

    def __init__(self) -> None:
        from .pipeline import InspireClient

        self.client = InspireClient()

    def search(self, collection: str, query: str, *, size: int = 25, page: int = 1,
               fields: str = "") -> Any:
        from . import pipeline

        previous = pipeline.AUTHOR_FIELDS
        pipeline.AUTHOR_FIELDS = fields or "control_number,ids"
        try:
            return self.client.fetch(collection, query, page, size)
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

    # Harvest first, connect second: the crawl takes minutes and a connection
    # held open across it gets closed by the server.
    found, stats = collect(_IdentifierClient())
    print(json.dumps(stats, indent=1), flush=True)
    with psycopg.connect(args.database_url, autocommit=True,
                         row_factory=psycopg.rows.dict_row) as connection:
        connection.execute(SCHEMA)
        stats |= store(connection, found, overlay_id=args.overlay_id)
    print(json.dumps(stats, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
