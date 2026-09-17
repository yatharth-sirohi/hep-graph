"""Database-first identity lookup uses the bounded RemoteClient API."""

from hepgraph.identity_search import search
from hepgraph.remote import RemoteError


class Client:
    def __init__(self, error=None):
        self.error = error
        self.calls = []

    def search(self, collection, query, *, size, page):
        self.calls.append((collection, query, size, page))
        if self.error:
            raise self.error
        return {"hits": {"hits": [{"id": "42", "metadata": {
            "control_number": 42,
            "name": {"value": "Doe, Jane", "preferred_name": "Jane Doe"},
            "ids": [{"schema": "ORCID", "value": "0000-0001-0002-0003"}],
            "positions": [{"institution": "Iowa", "current": True}],
        }}]}}


class Provider:
    def resolve_author(self, author_id):
        return {"id": author_id} if author_id == "42" else None


def test_lookup_uses_remote_search_and_returns_display_ready_graph_identity():
    client = Client()
    result = search(client, "Jane Doe", provider=Provider())
    assert result["status"] == "ok"
    assert client.calls == [("authors", client.calls[0][1], 25, 1)]
    assert "Jane" in client.calls[0][1]
    assert result["results"] == [{
        "id": "42", "name": "Jane Doe", "orcid": "0000-0001-0002-0003",
        "affiliations": ["Iowa"], "profile_status": "profile",
        "source_url": "https://inspirehep.net/authors/42", "indexed": True,
        "queryable": True,
    }]


def test_lookup_reports_upstream_failure_without_server_error():
    result = search(Client(RemoteError("upstream_unavailable", "try later")),
                    "Jane Doe", provider=Provider())
    assert result["status"] == "upstream_unavailable"
    assert result["message"] == "try later"
