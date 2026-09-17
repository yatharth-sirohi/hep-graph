"""Web-researched doctoral relations, kept separate from what INSPIRE says.

INSPIRE is the project's authority: an edge in ``graph_genealogy_edge`` is
something INSPIRE publishes, and the overlay's completeness certificate is a
claim about exactly that. Research done off the open web is a different kind of
thing - it is a lead with a citation, sometimes wrong - so it lands in its own
table with its evidence attached, and only becomes a served relation once it has
been checked.

Two rules make the leads worth keeping:

* An adviser must arrive as an **INSPIRE record id**, not a name. Matching by
  name is the identity guess this project refuses to make anywhere else, and a
  research agent is the last place to start making it.
* Every lead carries the URL it came from and the sentence that supports it, so
  a reviewer can reject it without repeating the search.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .neon_graph_provider import _at

SCHEMA = (
    "CREATE TABLE IF NOT EXISTS graph_genealogy_research ("
    " overlay_id TEXT NOT NULL,"
    " student_id BIGINT NOT NULL,"
    " adviser_id BIGINT NOT NULL,"
    " degree TEXT,"
    " evidence_url TEXT NOT NULL,"
    " evidence_quote TEXT NOT NULL,"
    " corroboration TEXT NOT NULL,"
    " confidence TEXT NOT NULL,"
    " researcher TEXT NOT NULL,"
    " status TEXT NOT NULL DEFAULT 'pending',"
    " reviewed_note TEXT,"
    " created_at TIMESTAMPTZ NOT NULL DEFAULT now(),"
    " PRIMARY KEY (overlay_id, student_id, adviser_id, evidence_url),"
    " CHECK (adviser_id <> student_id),"
    " CHECK (status IN ('pending','accepted','rejected')));"
    "CREATE TABLE IF NOT EXISTS graph_genealogy_research_miss ("
    " overlay_id TEXT NOT NULL,"
    " student_id BIGINT NOT NULL,"
    " researcher TEXT NOT NULL,"
    " note TEXT NOT NULL,"
    " created_at TIMESTAMPTZ NOT NULL DEFAULT now(),"
    " PRIMARY KEY (overlay_id, student_id));"
)

#: Enough of a person for a search to be about the right human, and no more.
TARGET_COLUMNS = ("student_id", "display_name", "descendants", "component_size")


@dataclass(frozen=True)
class Lead:
    student_id: int
    adviser_id: int
    evidence_url: str
    evidence_quote: str
    corroboration: str
    confidence: str
    degree: str | None = "phd"

    def problems(self) -> list[str]:
        """Reasons this lead may not be stored at all. Checked before the database."""
        found: list[str] = []
        if self.student_id == self.adviser_id:
            found.append("a person cannot be their own adviser")
        if not str(self.evidence_url).startswith(("http://", "https://")):
            found.append("evidence_url must be a URL that a reviewer can open")
        if len(str(self.evidence_quote).strip()) < 20:
            found.append("evidence_quote must quote the source, not summarise it")
        if len(str(self.corroboration).strip()) < 20:
            found.append("corroboration must say why this is the right INSPIRE person")
        if str(self.confidence) not in {"high", "medium", "low"}:
            found.append("confidence must be high, medium or low")
        return found


def targets(connection: Any, overlay_id: str = "inspire-genealogy", *,
            limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """People the overlay places in a tree but gives no doctoral adviser.

    Ordered by how much of the forest hangs off them: finding the adviser of
    someone with many descendants joins two families at once, which is the
    whole point of looking outside INSPIRE. Layout is only used for ordering,
    so targets can be handed out before a rebuilt map exists.
    """
    rows = connection.execute(
        """WITH placed AS (
               SELECT adviser_id AS person_id FROM graph_genealogy_edge
                WHERE overlay_id=%s AND degree='phd'
               UNION
               SELECT student_id FROM graph_genealogy_edge
                WHERE overlay_id=%s AND degree='phd'),
             advised AS (
               SELECT DISTINCT student_id FROM graph_genealogy_edge
                WHERE overlay_id=%s AND degree='phd'),
             descendants AS (
               SELECT adviser_id, count(*) AS n FROM graph_genealogy_edge
                WHERE overlay_id=%s AND degree='phd' GROUP BY 1)
           SELECT p.person_id AS student_id, COALESCE(n.name,'') AS display_name,
                  COALESCE(d.n,0) AS descendants, COALESCE(l.component_size,0) AS component_size
             FROM placed p
             LEFT JOIN graph_genealogy_person n
                    ON n.person_id = p.person_id AND n.overlay_id=%s
             LEFT JOIN graph_lineage_layout l
                    ON l.person_id = p.person_id AND l.overlay_id=%s
             LEFT JOIN descendants d ON d.adviser_id = p.person_id
            WHERE p.person_id NOT IN (SELECT student_id FROM advised)
              AND p.person_id NOT IN (SELECT student_id FROM graph_genealogy_research
                                       WHERE overlay_id=%s)
              AND p.person_id NOT IN (SELECT student_id FROM graph_genealogy_research_miss
                                       WHERE overlay_id=%s)
            ORDER BY COALESCE(d.n,0) DESC, COALESCE(l.component_size,0) DESC, p.person_id
            LIMIT %s OFFSET %s""",
        (overlay_id,) * 8 + (limit, offset)).fetchall()
    return [dict(zip(TARGET_COLUMNS, (int(_at(row, 0)), str(_at(row, 1)),
                                      int(_at(row, 2)), int(_at(row, 3))))) for row in rows]


def record(connection: Any, lead: Lead, *, researcher: str,
           overlay_id: str = "inspire-genealogy") -> dict[str, Any]:
    """Store one lead, or say why it was refused. Never writes the served overlay."""
    problems = lead.problems()
    if problems:
        return {"stored": False, "problems": problems}
    known = connection.execute(
        "SELECT 1 FROM graph_genealogy_edge WHERE overlay_id=%s AND student_id=%s "
        "AND adviser_id=%s", (overlay_id, lead.student_id, lead.adviser_id)).fetchone()
    if known is not None:
        return {"stored": False, "problems": ["INSPIRE already records this relation"]}
    connection.execute(
        "INSERT INTO graph_genealogy_research(overlay_id,student_id,adviser_id,degree,"
        "evidence_url,evidence_quote,corroboration,confidence,researcher) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING",
        (overlay_id, lead.student_id, lead.adviser_id, lead.degree, lead.evidence_url,
         lead.evidence_quote.strip(), lead.corroboration.strip(), lead.confidence, researcher))
    return {"stored": True, "problems": []}


def record_miss(connection: Any, student_id: int, *, researcher: str, note: str,
                overlay_id: str = "inspire-genealogy") -> None:
    """Remember that a person was searched for and nothing was found.

    Without this the next batch would hand the same hopeless names to the next
    agent forever.
    """
    connection.execute(
        "INSERT INTO graph_genealogy_research_miss(overlay_id,student_id,researcher,note) "
        "VALUES (%s,%s,%s,%s) ON CONFLICT (overlay_id,student_id) DO NOTHING",
        (overlay_id, int(student_id), researcher, note[:500]))


def ingest(connection: Any, lines: list[str], *, researcher: str,
           overlay_id: str = "inspire-genealogy") -> dict[str, Any]:
    """Load one research agent's JSONL output. Malformed lines are reported, not raised.

    Agents are expected to get some of this wrong, so every refusal is counted
    and returned: a silent drop would make a bad batch look like a thin one.
    """
    import json

    summary: dict[str, Any] = {"stored": 0, "missed": 0, "refused": []}
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except ValueError:
            summary["refused"].append({"line": line[:120], "problems": ["not JSON"]})
            continue
        try:
            student = int(item["student_id"])
        except (KeyError, TypeError, ValueError):
            summary["refused"].append({"line": line[:120], "problems": ["no usable student_id"]})
            continue
        if item.get("not_found"):
            record_miss(connection, student, researcher=researcher,
                        note=str(item.get("note", "")), overlay_id=overlay_id)
            summary["missed"] += 1
            continue
        try:
            lead = Lead(student_id=student, adviser_id=int(item["adviser_id"]),
                        evidence_url=str(item.get("evidence_url", "")),
                        evidence_quote=str(item.get("evidence_quote", "")),
                        corroboration=str(item.get("corroboration", "")),
                        confidence=str(item.get("confidence", "")),
                        degree=str(item.get("degree", "phd") or "phd").lower())
        except (KeyError, TypeError, ValueError):
            summary["refused"].append({"line": line[:120], "problems": ["no usable adviser_id"]})
            continue
        result = record(connection, lead, researcher=researcher, overlay_id=overlay_id)
        if result["stored"]:
            summary["stored"] += 1
        else:
            summary["refused"].append({"student_id": student, "problems": result["problems"]})
    return summary


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json
    import os
    import pathlib
    import sys

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.environ.get("DATABASE_URL_UNPOOLED"))
    parser.add_argument("--overlay-id", default="inspire-genealogy")
    parser.add_argument("--targets", type=int, default=0,
                        help="print this many people to research, as JSON, and exit")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--researcher", default="subagent",
                        help="which model produced the leads being ingested")
    parser.add_argument("leads", nargs="*", help="JSONL files written by research agents")
    args = parser.parse_args(argv)
    if not args.database_url:
        parser.error("a direct database URL is required")

    import psycopg

    with psycopg.connect(args.database_url, autocommit=True,
                         row_factory=psycopg.rows.dict_row) as connection:
        connection.execute(SCHEMA)
        if args.targets:
            print(json.dumps(targets(connection, args.overlay_id, limit=args.targets,
                                     offset=args.offset), indent=1))
            return 0
        if not args.leads:
            parser.error("give at least one leads file, or --targets N")
        total = {"stored": 0, "missed": 0, "refused": []}
        for path in args.leads:
            summary = ingest(connection, pathlib.Path(path).read_text().splitlines(),
                             researcher=args.researcher, overlay_id=args.overlay_id)
            total["stored"] += summary["stored"]
            total["missed"] += summary["missed"]
            total["refused"].extend(summary["refused"])
        print(json.dumps(total, indent=1), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
