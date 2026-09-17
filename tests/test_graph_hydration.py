"""Hydration must stay bounded and must never invent what it could not fetch."""
from __future__ import annotations

import re
from typing import Any

import pytest

from hepgraph.graph_hydration import (PERSON_KEYS, WORK_KEYS, HydrationBudget, HydrationCache,
                                      Hydrator)
from hepgraph.pipeline import PipelineError
from hepgraph.remote import RemoteError


class Clock:
    def __init__(self) -> None:
        self.now = 0.0
        self.sleeps: list[float] = []

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def work_hit(recid: str, *, deleted: bool = False) -> dict[str, Any]:
    return {"id": recid, "metadata": {
        "control_number": int(recid),
        "titles": [{"title": f"Measurement {recid}"}],
        "document_type": ["article"],
        "authors": [{"full_name": "Doe, Jane", "record": {"$ref": "https://inspirehep.net/api/authors/900"},
                     "inspire_roles": ["author"], "affiliations": [{"value": "CERN"}]}],
        "author_count": 3,
        "earliest_date": "2019-05-02",
        "preprint_date": "2019-05-02",
        "dois": [{"value": f"10.1000/{recid}"}],
        "arxiv_eprints": [{"value": f"1905.0{recid}"}],
        "deleted": deleted,
    }}


def person_hit(recid: str) -> dict[str, Any]:
    return {"id": recid, "metadata": {
        "control_number": int(recid),
        "name": {"value": f"Doe, J{recid}", "preferred_name": f"Jane Doe {recid}"},
        "ids": [{"schema": "ORCID", "value": f"0000-0002-0000-{recid}"}],
        "positions": [{"institution": "CERN", "current": True}],
    }}


class FakeInspire:
    """Answers only exact control_number batches; never touches the network."""

    def __init__(self, records: dict[str, dict[str, Any]] | None = None,
                 error: Exception | None = None) -> None:
        self.records = records or {}
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def fetch(self, collection: str, query: str, page: int, size: int,
              sort: str | None = None) -> dict[str, Any]:
        self.calls.append((collection, query))
        if self.error is not None:
            raise self.error
        ids = re.findall(r"control_number:(\d+)", query)
        hits = [self.records[f"{collection}:{ident}"] for ident in ids
                if f"{collection}:{ident}" in self.records]
        return {"hits": {"total": len(hits), "hits": hits}}


def make(records: dict[str, dict[str, Any]] | None = None, *, error: Exception | None = None,
         budget: HydrationBudget | None = None,
         cache: HydrationCache | None = None) -> tuple[Hydrator, FakeInspire, Clock]:
    clock = Clock()
    client = FakeInspire(records, error)
    hydrator = Hydrator(client, cache=cache if cache is not None else HydrationCache(clock=clock),
                        budget=budget, clock=clock, sleep=clock.sleep)
    return hydrator, client, clock


def works(*ids: str) -> dict[str, dict[str, Any]]:
    return {f"literature:{ident}": work_hit(ident) for ident in ids}


def people(*ids: str) -> dict[str, dict[str, Any]]:
    return {f"authors:{ident}": person_hit(ident) for ident in ids}


def test_repeated_ids_are_deduplicated_into_one_batched_request() -> None:
    hydrator, client, _ = make(works("11", "12"))
    result = hydrator.hydrate_works(("11", "12", "11", "11", "12"))
    assert set(result) == {"11", "12"}
    assert len(client.calls) == 1
    assert client.calls[0][1] == "control_number:11 OR control_number:12"
    assert hydrator.requests_made == 1


def test_second_call_is_served_from_cache_and_ttl_expiry_forces_a_refetch() -> None:
    clock = Clock()
    cache = HydrationCache(ttl_seconds=60.0, clock=clock)
    client = FakeInspire(people("900"))
    first = Hydrator(client, cache=cache, clock=clock, sleep=clock.sleep)
    assert first.hydrate_people(("900",))["900"]["name"] == "Jane Doe 900"
    assert len(client.calls) == 1

    second = Hydrator(client, cache=cache, clock=clock, sleep=clock.sleep)
    assert second.hydrate_people(("900",))["900"]["name"] == "Jane Doe 900"
    assert second.requests_made == 0 and second.cache_hits == 1
    assert len(client.calls) == 1

    clock.now += 61.0
    third = Hydrator(client, cache=cache, clock=clock, sleep=clock.sleep)
    assert third.hydrate_people(("900",))["900"]["name"] == "Jane Doe 900"
    assert third.requests_made == 1 and third.cache_hits == 0
    assert len(client.calls) == 2


def test_entry_ceiling_beyond_the_requested_count_yields_budget_placeholders() -> None:
    hydrator, client, _ = make(works("11", "12", "13"),
                               budget=HydrationBudget(max_requests=4, max_works=2, max_people=2))
    result = hydrator.hydrate_works(("11", "12", "13"))
    assert set(result) == {"11", "12", "13"}
    assert result["13"] == {"id": "13", "details_unavailable": True, "reason": "budget_exhausted",
                            "source_url": "https://inspirehep.net/literature/13"}
    assert not result["11"].get("details_unavailable")
    assert hydrator.failures == 1


def test_request_ceiling_stops_cleanly_without_dropping_entries() -> None:
    hydrator, client, _ = make(works("11", "12"),
                               budget=HydrationBudget(max_requests=1, min_interval_seconds=0.0))
    assert not hydrator.hydrate_works(("11",))["11"].get("details_unavailable")
    second = hydrator.hydrate_works(("12",))
    assert second["12"]["details_unavailable"] is True
    assert second["12"]["reason"] == "budget_exhausted"
    assert len(client.calls) == 1


def test_upstream_error_returns_a_placeholder_that_keeps_the_id() -> None:
    for error in (RemoteError("upstream_unavailable", "INSPIRE is down"),
                  RemoteError("resource_limit", "deadline", deadline=True),
                  PipelineError("INSPIRE HTTP 502"),
                  TimeoutError("read timed out")):
        hydrator, _, _ = make(works("11"), error=error)
        entry = hydrator.hydrate_works(("11",))["11"]
        assert entry["id"] == "11"
        assert entry["details_unavailable"] is True
        assert entry["reason"] in {"upstream_unavailable", "upstream_timeout"}
        assert entry["source_url"] == "https://inspirehep.net/literature/11"
        assert "title" not in entry and "date" not in entry


def test_unknown_and_deleted_records_are_reported_not_invented() -> None:
    hydrator, _, _ = make({**works("11"), "literature:12": work_hit("12", deleted=True)})
    result = hydrator.hydrate_works(("11", "12", "13"))
    assert result["12"]["reason"] == "record_deleted"
    assert result["13"]["reason"] == "not_found"
    assert result["13"]["id"] == "13"
    assert result["11"]["title"] == "Measurement 11"
    missing_person = hydrator.hydrate_people(("900",))["900"]
    assert missing_person["reason"] == "not_found"
    assert missing_person["source_url"] == "https://inspirehep.net/authors/900"
    assert "name" not in missing_person


def test_a_substituted_upstream_record_never_stands_in_for_the_cited_one() -> None:
    hydrator, client, _ = make({"literature:11": work_hit("99")})
    result = hydrator.hydrate_works(("11",))
    assert result["11"]["reason"] == "not_found"
    assert "99" not in result


def test_hydrated_entries_carry_exactly_the_frontend_keys() -> None:
    hydrator, _, _ = make({**works("11"), **people("900")})
    work = hydrator.hydrate_works(("11",))["11"]
    person = hydrator.hydrate_people(("900",))["900"]
    assert set(work) == set(WORK_KEYS)
    assert set(person) == set(PERSON_KEYS)
    assert work["year"] == 2019 and work["date"] == "2019-05-02"
    assert work["date_source"] in {"earliest_date", "preprint_date"}
    assert work["author_count"] == 3
    assert work["doi"] == ["10.1000/11"] and work["arxiv"] == ["1905.011"]
    assert work["source_url"] == "https://inspirehep.net/literature/11"
    assert work["retrieved_at"].endswith("Z")
    assert person["orcid"] == "0000-0002-0000-900"
    assert person["affiliations"] == ["CERN"]
    assert person["profile_status"] == "profile"
    assert person["source_url"] == "https://inspirehep.net/authors/900"


def test_hydrate_route_reports_completeness_and_counters() -> None:
    hydrator, _, _ = make({**works("11"), **people("900")},
                          budget=HydrationBudget(max_requests=4, min_interval_seconds=0.0))
    complete = hydrator.hydrate_route(people_ids=("900", "900"), work_ids=("11",))
    assert complete.complete is True and complete.reason is None
    assert complete.requests_made == 2 and complete.failures == 0
    assert set(complete.people) == {"900"} and set(complete.works) == {"11"}

    partial = hydrator.hydrate_route(people_ids=("900",), work_ids=("77",))
    assert partial.complete is False and partial.reason == "not_found"
    assert partial.cache_hits == 1
    assert partial.works["77"]["details_unavailable"] is True


def test_budget_exhaustion_dominates_the_reported_route_reason() -> None:
    hydrator, _, _ = make(works("11", "12"),
                          budget=HydrationBudget(max_requests=1, max_works=1, max_people=1,
                                                 min_interval_seconds=0.0))
    result = hydrator.hydrate_route(people_ids=(), work_ids=("11", "12"))
    assert result.complete is False and result.reason == "budget_exhausted"
    assert set(result.works) == {"11", "12"}


def test_pacing_waits_between_upstream_requests() -> None:
    hydrator, _, clock = make({**works("11"), **people("900")},
                              budget=HydrationBudget(min_interval_seconds=0.5))
    hydrator.hydrate_works(("11",))
    hydrator.hydrate_people(("900",))
    assert clock.sleeps == [0.5]


def test_deadline_exhaustion_produces_placeholders_rather_than_raising() -> None:
    hydrator, client, clock = make(works("11", "12"),
                                   budget=HydrationBudget(deadline_seconds=0.4,
                                                          min_interval_seconds=0.5))
    assert not hydrator.hydrate_works(("11",))["11"].get("details_unavailable")
    assert hydrator.hydrate_works(("12",))["12"]["reason"] == "budget_exhausted"
    assert len(client.calls) == 1


def test_invalid_ids_are_rejected_without_a_request() -> None:
    hydrator, client, _ = make(works("11"))
    entry = hydrator.hydrate_works(("not-an-id",))["not-an-id"]
    assert entry == {"id": "not-an-id", "details_unavailable": True, "reason": "invalid_id",
                     "source_url": None}
    assert client.calls == []


def test_cache_evicts_on_both_the_entry_and_byte_ceilings() -> None:
    clock = Clock()
    entries = HydrationCache(max_entries=2, clock=clock)
    for ident in ("1", "2", "3"):
        entries.put("works", ident, {"id": ident, "title": "x"})
    assert entries.get("works", "1") is None
    assert entries.get("works", "3") is not None
    assert entries.info()["entries"] == 2

    payload = {"id": "1", "title": "y" * 200}
    size = len(str(payload))
    small = HydrationCache(max_bytes=size + 40, clock=clock)
    small.put("works", "1", payload)
    assert small.get("works", "1") is not None
    small.put("works", "2", {**payload, "id": "2"})
    assert small.get("works", "1") is None
    assert small.get("works", "2") is not None
    assert small.info()["bytes"] <= size + 40

    oversize = HydrationCache(max_bytes=8, clock=clock)
    oversize.put("works", "1", payload)
    assert oversize.get("works", "1") is None


def test_cached_entries_are_isolated_copies_and_failures_are_not_cached() -> None:
    clock = Clock()
    cache = HydrationCache(clock=clock)
    client = FakeInspire(works("11"), error=RemoteError("upstream_unavailable", "down"))
    failing = Hydrator(client, cache=cache, clock=clock, sleep=clock.sleep)
    assert failing.hydrate_works(("11",))["11"]["details_unavailable"] is True
    assert cache.info()["entries"] == 0

    client.error = None
    hydrator = Hydrator(client, cache=cache, clock=clock, sleep=clock.sleep)
    entry = hydrator.hydrate_works(("11",))["11"]
    entry["title"] = "mutated"
    assert cache.get("works", "11")["title"] == "Measurement 11"


def test_budget_validation_rejects_unbounded_allowances() -> None:
    with pytest.raises(ValueError):
        Hydrator(FakeInspire(), budget=HydrationBudget(max_requests=0))
    with pytest.raises(ValueError):
        Hydrator(FakeInspire(), budget=HydrationBudget(deadline_seconds=0.0))
    with pytest.raises(ValueError):
        Hydrator(FakeInspire(), budget=HydrationBudget(max_works=10_000))
