"""The full-source gate is tested with a synthetic upstream, never a pilot."""

import json
import re

import pytest

from hepgraph.full_acquisition import FullAcquisition, open_acquisition
from hepgraph.pipeline import PipelineError


class FakeInspire:
    def __init__(self):
        self.records = {
            "literature": {str(number): {
                "id": str(number), "metadata": {
                    "control_number": number, "titles": [{"title": f"Work {number}"}],
                    "document_type": ["article"], "authors": [], "author_count": 0,
                }} for number in (1, 2, 3, 4, 5, 6, 7)},
            "authors": {str(number): {
                "id": str(number), "metadata": {
                    "control_number": number, "name": {"value": f"Person {number}"},
                }} for number in (1, 3, 5, 7)},
        }
        self.calls = []

    def fetch(self, collection, query, page, size, sort=None):
        self.calls.append((collection, query, page, size))
        if query:
            bounds = re.findall(r"\d+", query)
            low, high = map(int, bounds)
            rows = [row for recid, row in self.records[collection].items()
                    if low <= int(recid) <= high]
        else:
            rows = list(self.records[collection].values())
        rows.sort(key=lambda row: int(row["id"]))
        return {"hits": {"total": len(rows), "hits": rows[(page - 1) * size:page * size]}}


def test_full_acquisition_resume_verify_and_privacy(tmp_path):
    db = open_acquisition(tmp_path / "spool.sqlite")
    client = FakeInspire()
    runner = FullAcquisition(db, client, max_recid=8, shard_size=2)
    runner.plan()
    assert runner.status()["literature"]["partitions"]["READY"] > 0
    runner.fetch(max_partitions=1)
    assert runner.status()["literature"]["partitions"]["DONE"] == 1
    # A fresh process can resume without re-fetching the committed shard.
    runner = FullAcquisition(db, client, max_recid=8, shard_size=2)
    runner.plan()
    runner.fetch()
    report = runner.verify()
    assert report["source_complete"] is True
    assert report["collections"]["literature"]["records"] == 7
    assert report["collections"]["authors"]["records"] == 4
    stored = db.execute("SELECT payload FROM acquisition_record WHERE collection='authors' LIMIT 1").fetchone()[0]
    assert "email_addresses" not in stored
    assert "private_field" not in stored
    assert json.loads(stored)["name"]["value"].startswith("Person")
    assert all(size <= 2 for _, _, _, size in client.calls if size > 1)
    db.close()


def test_fails_closed_on_upstream_count_drift(tmp_path):
    db = open_acquisition(tmp_path / "spool.sqlite")
    client = FakeInspire()
    runner = FullAcquisition(db, client, max_recid=8, shard_size=2)
    runner.plan()
    client.records["literature"]["8"] = {"id": "8", "metadata": {
        "control_number": 8, "document_type": ["article"], "authors": [], "author_count": 0,
    }}
    with pytest.raises(PipelineError, match="changed during acquisition"):
        runner.fetch()
    assert db.execute("SELECT COUNT(*) FROM acquisition_partition WHERE status='READY'").fetchone()[0] > 0
    with pytest.raises(PipelineError, match="incomplete partitions"):
        runner.verify()
    db.close()


def test_detects_missing_horizon_and_corrupted_spool(tmp_path):
    db = open_acquisition(tmp_path / "spool.sqlite")
    client = FakeInspire()
    with pytest.raises(PipelineError, match="omits records"):
        FullAcquisition(db, client, max_recid=6, shard_size=2).plan()
    runner = FullAcquisition(db, client, max_recid=8, shard_size=2)
    runner.plan()
    runner.fetch()
    db.execute("UPDATE acquisition_record SET payload='{}' WHERE collection='literature' AND recid='1'")
    db.commit()
    with pytest.raises(PipelineError, match="checksum/count failed"):
        runner.verify()
    db.close()


def test_refuses_duplicate_or_out_of_shard_ids(tmp_path):
    class BadClient(FakeInspire):
        def fetch(self, collection, query, page, size, sort=None):
            response = super().fetch(collection, query, page, size, sort)
            if collection == "literature" and size > 1 and response["hits"]["hits"]:
                response["hits"]["hits"][0] = {"id": "999", "metadata": {
                    "control_number": 999, "document_type": ["article"], "authors": [],
                    "author_count": 0,
                }}
            return response

    db = open_acquisition(tmp_path / "spool.sqlite")
    runner = FullAcquisition(db, BadClient(), max_recid=8, shard_size=2)
    runner.plan()
    # First ready shard may be one row, so drain until the bad multi-row shard.
    with pytest.raises(PipelineError, match="outside shard"):
        runner.fetch()
    db.close()
