"""Wikidata adviser links: identifier to identifier, or not at all.

The value of this source is that neither end is a name, so the tests are about
refusing anything that would reintroduce name matching.
"""

from __future__ import annotations

from hepgraph.wikidata_genealogy import leads, resolve_bais


class Client:
    """Stands in for INSPIRE's author search over a small id table."""

    def __init__(self, table, duplicates=()):
        self.table = table
        self.duplicates = dict(duplicates)
        self.queries = []

    def search(self, collection, query, **kwargs):
        self.queries.append(query)
        hits = []
        for bai, recid in self.table.items():
            if f'"{bai}"' in query:
                hits.append({"metadata": {"control_number": recid,
                                          "ids": [{"value": bai}]}})
                if bai in self.duplicates:
                    hits.append({"metadata": {"control_number": self.duplicates[bai],
                                              "ids": [{"value": bai}]}})
        return {"hits": {"hits": hits, "total": len(hits)}}


def pair(student="S.One.1", adviser="A.Two.1", item="http://www.wikidata.org/entity/Q42"):
    return {"item": item, "student_bai": student, "student_label": "Student One",
            "adviser_bai": adviser, "adviser_label": "Adviser Two"}


def test_a_bai_resolves_to_the_one_record_that_carries_it():
    client = Client({"S.One.1": 111, "A.Two.1": 222})
    assert resolve_bais(["S.One.1", "A.Two.1"], client) == {"S.One.1": 111, "A.Two.1": 222}


def test_a_bai_matching_two_records_is_refused_rather_than_picked():
    client = Client({"S.One.1": 111}, duplicates={"S.One.1": 999})
    assert resolve_bais(["S.One.1"], client) == {}


def test_identifiers_are_asked_for_in_batches_not_one_request_each():
    client = Client({f"P.{i}.1": i for i in range(1, 60)})
    resolve_bais([f"P.{i}.1" for i in range(1, 60)], client, batch=25)
    assert len(client.queries) == 3


def test_a_pair_with_an_unresolved_end_produces_no_lead():
    assert leads([pair()], {"S.One.1": 111}) == []
    assert leads([pair()], {"A.Two.1": 222}) == []


def test_a_resolved_pair_carries_its_wikidata_item_as_evidence():
    made = leads([pair()], {"S.One.1": 111, "A.Two.1": 222})
    assert len(made) == 1
    lead = made[0]
    assert (lead.student_id, lead.adviser_id) == (111, 222)
    assert lead.evidence_url == "https://www.wikidata.org/wiki/Q42"
    assert "Q42" in lead.evidence_quote and "Adviser Two" in lead.evidence_quote
    assert "S.One.1" in lead.corroboration and "No name matching" in lead.corroboration
    assert lead.problems() == []


def test_a_self_loop_in_the_source_is_dropped():
    same = pair(student="X.1", adviser="X.1")
    assert leads([same], {"X.1": 111}) == []


# ------------------------------------------------- the Wikipedia-article bridge

class PagedClient(Client):
    """Adds paging and a WIKIPEDIA id on some records."""

    def __init__(self, table, wikipedia):
        super().__init__(table)
        self.wikipedia = wikipedia   # recid -> article title

    def search(self, collection, query, *, size=25, page=1, fields=""):
        if "WIKIPEDIA" in query:
            items = sorted(self.wikipedia.items())
            chunk = items[(page - 1) * size:page * size]
            return {"hits": {"hits": [
                {"metadata": {"control_number": recid,
                              "ids": [{"schema": "WIKIPEDIA", "value": title},
                                      {"schema": "INSPIRE BAI", "value": f"B.{recid}.1"}]}}
                for recid, title in chunk], "total": len(items)}}
        return super().search(collection, query, size=size)


def test_the_bridge_reads_inspires_own_wikipedia_identifiers():
    from hepgraph.wikidata_genealogy import wikipedia_titles

    client = PagedClient({}, {1019139: "Lev_Landau", 1033333: "Niels_Bohr"})
    assert wikipedia_titles(client) == {"Lev Landau": 1019139, "Niels Bohr": 1033333}


def test_a_stale_wikidata_identifier_is_rescued_by_the_article_not_the_name():
    """Wikidata says Bohr is 'N.Bohr.1'; INSPIRE has no such record."""
    from hepgraph.wikidata_genealogy import leads

    pair = {"item": "http://www.wikidata.org/entity/Q7085",
            "student_qid": "Q7085", "student_bai": "N.Bohr.1", "student_label": "Niels Bohr",
            "adviser_qid": "Q47285", "adviser_bai": "Joseph.John.Thomson.1",
            "adviser_label": "J. J. Thomson"}
    resolved = {"Joseph.John.Thomson.1": 1076576}          # the BAI that does resolve
    assert leads([pair], resolved) == []                   # nothing to identify Bohr with

    made = leads([pair], resolved, {"Q7085": 1033333})     # the article bridges him
    assert len(made) == 1 and made[0].student_id == 1033333
    assert "Wikipedia article" in made[0].corroboration
    assert made[0].problems() == []


def test_the_bridge_never_rescues_an_end_it_cannot_identify():
    from hepgraph.wikidata_genealogy import leads

    pair = {"item": "http://www.wikidata.org/entity/Q1", "student_qid": "Q1",
            "student_bai": "", "student_label": "Someone",
            "adviser_qid": "Q2", "adviser_bai": "", "adviser_label": "Another"}
    assert leads([pair], {}, {"Q1": 5}) == []      # the adviser is still unidentified
