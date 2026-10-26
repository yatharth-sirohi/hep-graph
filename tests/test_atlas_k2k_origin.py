"""The K2K baseline starts where K2K's beam was made, not at the Belle II hall.

The baseline's origin was `site:kek-tsukuba-belle-ii`, the SuperKEKB interaction
region, which is a different place on the KEK campus from the 12 GeV proton
synchrotron whose beam K2K used. The origin is now a campus-grade site for the
synchrotron and the K2K beamline, marked approximate; this pins that, and the
A21 distance rule that has to keep holding with it.
"""

from __future__ import annotations

import pytest

from hepgraph.atlas import geo
from hepgraph.atlas.load import DATA_DIR, load_atlas

ORIGIN = "site:kek-ps-k2k-beamline"
FAR = "site:kamioka-mozumi-mine-super-kamiokande"


@pytest.fixture(scope="module")
def atlas():
    return load_atlas(DATA_DIR)


def test_k2k_baseline_starts_at_the_synchrotron_site(atlas) -> None:
    beamline = atlas.get("beamline:kek-neutrino")
    (baseline,) = beamline["baselines"]
    assert baseline["from_site_id"] == ORIGIN
    assert baseline["to_site_id"] == FAR
    assert atlas.get("accelerator:kek-ps")["site_id"] == ORIGIN


def test_the_origin_is_an_honest_campus_point(atlas) -> None:
    site = atlas.get(ORIGIN)
    assert site["facility_id"] == "facility:kek"
    coordinates = site["coordinates"]
    # A campus-grade stand-in: said to be approximate, with its precision, and never
    # relabelled as a detector or underground-laboratory position (A17, A23).
    assert coordinates["kind"] == "campus"
    assert coordinates["confidence"] == "approximate"
    assert coordinates["precision_m"] >= 500
    assert coordinates["sources"], "the coordinate needs a source"
    assert "KEK-PS" in coordinates["quote"], "and a quote that the beam came from the KEK-PS"
    assert ORIGIN != "site:kek-tsukuba-belle-ii"


def test_the_great_circle_distance_stays_within_two_percent_of_250_km(atlas) -> None:
    origin = atlas.get(ORIGIN)["coordinates"]
    far = atlas.get(FAR)["coordinates"]
    metres = geo.haversine_m(origin["lon"], origin["lat"], far["lon"], far["lat"])
    assert abs(metres / 1000 - 250) / 250 <= 0.02, f"{metres / 1000:.1f} km"
