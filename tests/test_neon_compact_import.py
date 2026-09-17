from hepgraph.neon_compact_import import _work_from_hit


def literature(recid, *, title="A paper", document_type=None, author_count=2, authors=None, **extra):
    metadata = {
        "control_number": recid,
        "titles": [{"title": title}],
        "document_type": document_type or ["article"],
        "author_count": author_count,
        "authors": authors if authors is not None else [
            {"record": {"$ref": "https://inspirehep.net/api/authors/12"}},
            {"record": {"$ref": "https://inspirehep.net/api/authors/14"}},
        ],
    }
    metadata.update(extra)
    return {"id": str(recid), "updated": "2026-09-16T00:00:00Z", "metadata": metadata}


def test_compact_row_keeps_only_path_necessary_values():
    row = _work_from_hit(literature(11, earliest_date="2021-03-17"))
    assert row == (11, 2021, 2, (12, 14), "2026-09-16T00:00:00Z")


def test_compact_row_treats_team_size_as_source_truth_and_deduplicates_ids():
    row = _work_from_hit(literature(12, author_count=52, authors=[
        {"record": {"$ref": "https://inspirehep.net/api/authors/12"}},
        {"record": {"$ref": "https://inspirehep.net/api/authors/12"}},
        {"record": {"$ref": "https://inspirehep.net/api/authors/14"}},
        {"record": None},
    ]))
    assert row is not None
    assert row[2:4] == (52, (12, 14))


def test_compact_row_excludes_non_graph_semantics_without_persisting_titles():
    assert _work_from_hit(literature(1, title="Erratum: A paper")) is None
    assert _work_from_hit(literature(2, document_type=["thesis"])) is None
    assert _work_from_hit(literature(3, document_type=["book", "article"])) is None
    assert _work_from_hit(literature(4, author_count=1)) is None
    assert _work_from_hit(literature(5, deleted=True)) is None


def test_compact_row_excludes_explicit_non_author_roles_but_keeps_missing_roles():
    row = _work_from_hit(literature(6, authors=[
        {"record": {"$ref": "https://inspirehep.net/api/authors/12"}, "inspire_roles": ["editor"]},
        {"record": {"$ref": "https://inspirehep.net/api/authors/14"}},
        {"record": {"$ref": "https://inspirehep.net/api/authors/15"}, "inspire_roles": ["author"]},
    ]))
    assert row is not None
    assert row[3] == (14, 15)
