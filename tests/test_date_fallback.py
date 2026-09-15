"""Regression coverage for INSPIRE's database-created earliest-date fallback."""

from hepgraph.pipeline import _documented_date


def _payload(**overrides):
    payload = {
        "earliest_date": None,
        "preprint_date": None,
        "imprints": [],
        "publication_years": [],
        "thesis_info": {"date": None},
    }
    payload.update(overrides)
    return payload


def test_earliest_date_alone_is_not_published_as_a_scholarly_date():
    # INSPIRE's LiteratureRecord.earliest_date uses the database record's
    # created timestamp if it cannot derive a date from scholarly metadata.
    # ``created`` is deliberately not one of our requested/persisted fields;
    # an otherwise unsupported response must remain unknown.
    created_fallback = _payload(
        earliest_date="2024-05-06",
        created="2024-05-06T13:14:15+00:00",
    )
    assert _documented_date([created_fallback]) == (None, "unknown")


def test_supported_earliest_date_preserves_its_reported_precision():
    # A full imprint corroborates every part of this reported month.  The
    # output should retain the official earliest month rather than inventing
    # the imprint's later day.
    corroborated_month = _payload(
        earliest_date="2012-07",
        imprints=["2012-07-31"],
    )
    assert _documented_date([corroborated_month]) == ("2012-07", "earliest_date")


def test_bare_publication_year_cannot_corrobate_an_earliest_day():
    # A publication year is real evidence, but it cannot prove a day which may
    # have originated solely from the INSPIRE database creation timestamp.
    # Its own documented precision remains a usable fallback.
    precision_mismatch = _payload(
        earliest_date="2024-05-06",
        publication_years=["2024"],
    )
    assert _documented_date([precision_mismatch]) == ("2024", "publication_info.year")
