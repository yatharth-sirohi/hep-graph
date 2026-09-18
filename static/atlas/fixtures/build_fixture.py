#!/usr/bin/env python3
"""Generate the HEP Atlas development fixture bundles in v0.2 shapes.

Run: .venv/bin/python static/atlas/fixtures/build_fixture.py

The Atlas front end is developed against these files (`/atlas?data=fixtures`)
so it does not block on the real pipeline. Facilities, experiments, detectors,
results and documents describe real projects; institution memberships are a
plausible subset and every *person* is invented. `manifest.json` says so and
the UI shows the banner.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD_DATE = "2026-09-16"
COVERAGE_UPDATED = "2026-09-12"
EPOCH_YEAR = 1950
AS_OF = "2026-09"

# --------------------------------------------------------------------------
# dates and A3 timeline semantics


def parse(date: str | None):
    """Return (lo_month, hi_month) in months since 1950-01, or None."""
    if not date:
        return None
    m = re.fullmatch(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", date)
    if not m:
        raise ValueError(f"bad date {date!r}")
    year, month = int(m.group(1)), m.group(2)
    if month is None:
        return (months(year, 1), months(year, 12))
    return (months(year, int(month)), months(year, int(month)))


def months(year: int, month: int) -> int:
    return (year - EPOCH_YEAR) * 12 + (month - 1)


BUILD_M = parse(BUILD_DATE)[0]

RANK = ["decommissioned", "cancelled", "completed", "shutdown", "upgrade", "active",
        "commissioning", "construction", "approved", "proposed", "planned"]
TERMINAL = {"completed", "decommissioned", "cancelled"}
EARLY = {"proposed", "approved", "planned"}


def state_segments(intervals):
    """A3: month-resolution state + certainty, run-length encoded."""
    spans = []
    for iv in intervals:
        lo_s, hi_s = parse(iv.get("start")) or (None, None)
        end = parse(iv.get("end"))
        spans.append({"status": iv["status"], "lo_s": lo_s, "hi_s": hi_s,
                      "lo_e": end[0] if end else None, "hi_e": end[1] if end else None,
                      "open": iv.get("end") is None})
    starts = [s["lo_s"] for s in spans if s["lo_s"] is not None]
    if not starts:
        return [], False
    first = min(starts)
    last = BUILD_M
    for s in spans:
        if s["hi_e"] is not None:
            last = max(last, s["hi_e"])
    open_ended = any(s["open"] and s["status"] not in TERMINAL for s in spans)
    out = []
    for m in range(first, last + 1):
        covering = []
        for s in spans:
            if s["lo_s"] is not None and s["lo_s"] > m:
                continue
            if not s["open"] and s["hi_e"] is not None and s["hi_e"] < m:
                continue
            if s["open"] and m > BUILD_M:
                continue
            certain = (s["hi_s"] is None or s["hi_s"] <= m) and \
                      (s["open"] or (s["lo_e"] is not None and s["lo_e"] >= m))
            covering.append((s, certain))
        if not covering:
            continue
        strong = [c for c in covering if c[0]["status"] not in EARLY]
        pool = strong or covering
        best = max(pool, key=lambda c: (c[0]["lo_s"], -RANK.index(c[0]["status"])))
        certainty = "certain" if best[1] else "possible"
        seg = [m, m, best[0]["status"], certainty]
        if out and out[-1][2] == seg[2] and out[-1][3] == seg[3] and out[-1][1] == m - 1:
            out[-1][1] = m
        else:
            out.append(seg)
    return out, open_ended


def status_at(segments, month):
    for m0, m1, status, _ in segments:
        if m0 <= month <= m1:
            return status
    return None


# --------------------------------------------------------------------------
# helpers


def q(value, unit, display, dimension):
    return {"value": value, "unit": unit, "display": display, "dimension": dimension}


_ARXIV_ID_RE = re.compile(r'^([0-9]{4}\.[0-9]{4,5}|[a-z-]+(?:\.[A-Za-z-]+)?/[0-9]{7})(?:v\d+)?$')
_ARXIV_URL_RE = re.compile(
    r'^(?:https?://)?(?:www\.)?arxiv\.org/(?:abs|pdf)/([^\s?#]+?)(?:\.pdf)?/?$', re.IGNORECASE)
_DOI_URL_RE = re.compile(r'^(?:https?://)?(?:dx\.)?doi\.org/(.+)$', re.IGNORECASE)


def _normalize_arxiv_id(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text_ = value.strip()
    m = _ARXIV_URL_RE.match(text_)
    if m:
        text_ = m.group(1)
    m = _ARXIV_ID_RE.match(text_)
    return m.group(1) if m else None


def _normalize_doi(value):
    if not isinstance(value, str) or not value.strip():
        return None
    text_ = value.strip()
    m = _DOI_URL_RE.match(text_)
    if m:
        text_ = m.group(1)
    text_ = text_.strip('/')
    return text_.lower() or None


def official_url_kind(official_url, publication):
    """Mirrors hepgraph/atlas/build.py's `_official_url_kind` (A4): whether
    `official_url` restates `publication.arxiv`/`.doi` under another name, so
    the panel never shows the same target twice. Kept independent (not
    imported) because this script builds the dev-fixtures tree standalone,
    without the ontology pipeline `hepgraph.atlas.build` runs against."""
    if not official_url:
        return None
    publication = publication if isinstance(publication, dict) else {}
    official_arxiv = _normalize_arxiv_id(official_url)
    if official_arxiv and official_arxiv == _normalize_arxiv_id(publication.get("arxiv")):
        return "arxiv"
    official_doi = _normalize_doi(official_url)
    if official_doi and official_doi == _normalize_doi(publication.get("doi")):
        return "doi"
    return "official"


def great_circle_km(a, b):
    lat1, lon1, lat2, lon2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    d = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(d))


def iv(status, start, end=None, label=None, kind="lifecycle", planned=False):
    return {"status": status, "start": start, "end": end,
            "label": label or status, "kind": kind, "planned": planned}


TEXT: dict[str, dict] = {}
PROV: dict[str, dict] = {}


def text(entity_id, **fields):
    TEXT.setdefault(entity_id, {}).update({k: v for k, v in fields.items() if v})


def prov(entity_id, path, sources, *, quote="", locator="", confidence="verified",
         verified_at=COVERAGE_UPDATED, note=""):
    PROV.setdefault(entity_id, {})[path] = {
        "sources": sources, "verified_at": verified_at, "confidence": confidence,
        "note": note, "quote": quote, "locator": locator,
    }


# --------------------------------------------------------------------------
# sites

SITES = [
    ("site:cern-meyrin", "CERN Meyrin site", "facility:cern", 46.2339, 6.0553, 150, "campus",
     "surface", None, None, 430, "CH", ("Meyrin", "Canton of Geneva", "CH"), []),
    ("site:cern-lhc-point-1", "LHC Point 1 — ATLAS cavern", "facility:cern", 46.2352, 6.0555, 60,
     "detector", "underground", 100, None, 430, "CH", ("Meyrin", "Canton of Geneva", "CH"),
     [iv("active", "2008-09")]),
    ("site:cern-lhc-point-5", "LHC Point 5 — CMS cavern", "facility:cern", 46.3100, 6.0770, 60,
     "detector", "underground", 100, None, 490, "FR", ("Cessy", "Ain", "FR"),
     [iv("active", "2008-09")]),
    ("site:cern-sps-lss5", "SPS Long Straight Section 5 — UA1 cavern", "facility:cern", 46.2467, 6.0500,
     120, "detector", "underground", 25, None, 435, "CH", ("Meyrin", "Canton of Geneva", "CH"),
     [iv("active", "1981-07", "1990-12"), iv("decommissioned", "1990-12", "1993-01")]),
    ("site:fermilab-batavia", "Fermilab Batavia site", "facility:fermilab", 41.8319, -88.2569, 200,
     "campus", "surface", None, None, 226, "US", ("Batavia", "Illinois", "US"), []),
    ("site:fermilab-nd-hall", "LBNF near detector hall", "facility:fermilab", 41.8320, -88.2620, 50,
     "detector", "underground", 60, None, 226, "US", ("Batavia", "Illinois", "US"),
     [iv("construction", "2023-01")]),
    ("site:fermilab-minos-hall", "MINOS near detector hall", "facility:fermilab", 41.8380, -88.2650, 50,
     "detector", "underground", 105, None, 226, "US", ("Batavia", "Illinois", "US"),
     [iv("active", "2005-01")]),
    ("site:fermilab-sbnd-hall", "SBND detector hall", "facility:fermilab", 41.8400, -88.2740, 50,
     "detector", "surface", None, None, 226, "US", ("Batavia", "Illinois", "US"),
     [iv("active", "2024-07")]),
    ("site:fermilab-icarus-hall", "ICARUS detector hall", "facility:fermilab", 41.8450, -88.2790, 50,
     "detector", "surface", None, None, 226, "US", ("Batavia", "Illinois", "US"),
     [iv("active", "2020-08")]),
    ("site:surf-dune-caverns", "SURF 4850 ft level — DUNE caverns", "facility:surf", 44.3510, -103.7580,
     80, "underground_lab", "underground", 1478, 4300, 1600, "US", ("Lead", "South Dakota", "US"),
     [iv("construction", "2021-01")]),
    ("site:surf-davis-campus", "SURF 4850 ft level — Davis Campus", "facility:surf", 44.3520, -103.7510,
     80, "underground_lab", "underground", 1478, 4300, 1600, "US", ("Lead", "South Dakota", "US"),
     [iv("active", "2012-05")]),
    ("site:nova-ash-river", "NOvA Ash River far detector laboratory", "facility:fermilab", 48.3786,
     -92.8314, 100, "detector", "surface", None, None, 400, "US", ("Ash River", "Minnesota", "US"),
     [iv("active", "2014-02")]),
    ("site:jparc-tokai", "J-PARC Tokai campus", "facility:j-parc", 36.4425, 140.6070, 200, "campus",
     "surface", None, None, 30, "JP", ("Tokai", "Ibaraki", "JP"), []),
    ("site:jparc-nd280", "T2K near detector pit (ND280)", "facility:j-parc", 36.4400, 140.6030, 50,
     "detector", "underground", 33, None, 30, "JP", ("Tokai", "Ibaraki", "JP"),
     [iv("active", "2009-11")]),
    ("site:super-k-cavern", "Super-Kamiokande cavern, Mozumi mine", "facility:kamioka-observatory",
     36.4275, 137.3100, 100, "underground_lab", "underground", 1000, 2700, 370, "JP",
     ("Hida", "Gifu", "JP"), [iv("active", "1996-04")]),
    ("site:icecube-array", "IceCube in-ice array, Amundsen–Scott Station", "facility:amundsen-scott",
     -89.9944, -63.4533, 500, "detector", "ice", 2450, None, 2835, "AQ",
     ("Amundsen–Scott South Pole Station", "South Pole", "AQ"), [iv("active", "2010-12")]),
    ("site:kek-tsukuba", "KEK Tsukuba campus — SuperKEKB interaction region", "facility:kek", 36.1500,
     140.0770, 150, "campus", "surface", None, None, 30, "JP", ("Tsukuba", "Ibaraki", "JP"), []),
]

# --------------------------------------------------------------------------
# facilities

FACILITIES = [
    dict(id="facility:cern", name="CERN", aliases=["European Organization for Nuclear Research",
         "Organisation européenne pour la recherche nucléaire"], kind="accelerator_laboratory",
         country=["CH", "FR"], operator="CERN Member States",
         primary_site_id="site:cern-meyrin", institution_id="institution:cern",
         website="https://home.cern/",
         intervals=[iv("active", "1954-09-29", label="founded")],
         specs={"cms_energy": q(13600, "GeV", "13.6 TeV", "energy")},
         topic_ids=["topic:electroweak-symmetry-breaking", "topic:higgs-boson",
                    "topic:qcd-and-heavy-ions", "topic:b-meson-decays"]),
    dict(id="facility:fermilab", name="Fermilab", aliases=["Fermi National Accelerator Laboratory",
         "FNAL"], kind="accelerator_laboratory", country=["US"],
         operator="Fermi Forward Discovery Group for the U.S. Department of Energy",
         primary_site_id="site:fermilab-batavia", institution_id="institution:fermilab",
         website="https://www.fnal.gov/",
         intervals=[iv("active", "1967-11-21", label="founded")],
         specs={"beam_power": q(900, "kW", "900 kW (NuMI, 2024)", "power")},
         topic_ids=["topic:neutrino-oscillations", "topic:leptonic-cp-violation",
                    "topic:sterile-neutrinos"]),
    dict(id="facility:surf", name="Sanford Underground Research Facility",
         aliases=["SURF", "Homestake"], kind="underground_laboratory", country=["US"],
         operator="South Dakota Science and Technology Authority",
         primary_site_id="site:surf-davis-campus", institution_id=None,
         website="https://sanfordlab.org/",
         intervals=[iv("active", "2007-06", label="founded")],
         specs={"overburden": q(4300, "m.w.e.", "4300 m.w.e.", "depth_mwe"),
                "depth": q(1478, "m", "1478 m (4850 ft)", "length")},
         topic_ids=["topic:neutrino-oscillations", "topic:wimp-direct-detection"]),
    dict(id="facility:j-parc", name="J-PARC", aliases=["Japan Proton Accelerator Research Complex"],
         kind="accelerator_laboratory", country=["JP"], operator="JAEA and KEK",
         primary_site_id="site:jparc-tokai", institution_id=None,
         website="https://j-parc.jp/c/en/",
         intervals=[iv("active", "2009-02", label="operating")],
         specs={"beam_power": q(760, "kW", "760 kW (neutrino beam, 2023)", "power")},
         topic_ids=["topic:neutrino-oscillations", "topic:leptonic-cp-violation"]),
    dict(id="facility:kamioka-observatory", name="Kamioka Observatory",
         aliases=["Kamioka", "Institute for Cosmic Ray Research, Kamioka"],
         kind="underground_laboratory", country=["JP"],
         operator="Institute for Cosmic Ray Research, University of Tokyo",
         primary_site_id="site:super-k-cavern", institution_id="institution:university-of-tokyo-icrr",
         website="https://www-sk.icrr.u-tokyo.ac.jp/en/",
         intervals=[iv("active", "1983-07", label="founded")],
         specs={"overburden": q(2700, "m.w.e.", "2700 m.w.e.", "depth_mwe")},
         topic_ids=["topic:neutrino-oscillations", "topic:neutrino-astronomy"]),
    dict(id="facility:amundsen-scott", name="Amundsen–Scott South Pole Station",
         aliases=["South Pole Station"], kind="polar_station", country=["AQ"],
         operator="U.S. Antarctic Program, National Science Foundation",
         primary_site_id="site:icecube-array", institution_id=None,
         website="https://www.nsf.gov/geo/opp/support/southp.jsp",
         intervals=[iv("active", "1956-11", label="founded")],
         specs={"altitude": q(2835, "m", "2835 m", "length")},
         topic_ids=["topic:neutrino-astronomy"]),
    dict(id="facility:kek", name="KEK", aliases=["High Energy Accelerator Research Organization"],
         kind="accelerator_laboratory", country=["JP"], operator="Inter-University Research Institute Corporation",
         primary_site_id="site:kek-tsukuba", institution_id="institution:kek",
         website="https://www.kek.jp/en/",
         intervals=[iv("active", "1971-04", label="founded")],
         specs={"peak_luminosity": q(5.1e34, "cm^-2 s^-1", "5.1 × 10³⁴ cm⁻² s⁻¹", "luminosity")},
         topic_ids=["topic:b-meson-decays", "topic:flavour-physics"]),
]


# --------------------------------------------------------------------------
# accelerators and beamlines

ACCELERATORS = [
    dict(id="accelerator:lhc", name="Large Hadron Collider", aliases=["LHC"], kind="collider",
         facility_id="facility:cern", site_id="site:cern-meyrin", is_collider=True,
         particles=["proton", "lead ion"], feeds_accelerator_ids=[],
         intervals=[iv("construction", "1998-12", "2008-08"), iv("commissioning", "2008-09", "2010-03"),
                    iv("active", "2010-03", "2013-02"), iv("shutdown", "2013-02", "2015-04", label="LS1"),
                    iv("active", "2015-04", "2018-12"), iv("shutdown", "2018-12", "2022-04", label="LS2"),
                    iv("active", "2022-04")],
         specs={"cms_energy": q(13600, "GeV", "13.6 TeV", "energy"),
                "circumference": q(26659, "m", "26.659 km", "length"),
                "peak_luminosity": q(2.1e34, "cm^-2 s^-1", "2.1 × 10³⁴ cm⁻² s⁻¹", "luminosity")}),
    dict(id="accelerator:sps", name="Super Proton Synchrotron", aliases=["SPS", "SppS"],
         kind="synchrotron", facility_id="facility:cern", site_id="site:cern-meyrin",
         is_collider=False, particles=["proton", "antiproton", "lead ion"],
         feeds_accelerator_ids=["accelerator:lhc"],
         intervals=[iv("active", "1976-05")],
         specs={"beam_energy": q(450, "GeV", "450 GeV", "energy"),
                "circumference": q(6912, "m", "6.912 km", "length")}),
    dict(id="accelerator:fermilab-main-injector", name="Main Injector", aliases=["MI"],
         kind="synchrotron", facility_id="facility:fermilab", site_id="site:fermilab-batavia",
         is_collider=False, particles=["proton"], feeds_accelerator_ids=[],
         intervals=[iv("active", "1999-06")],
         specs={"beam_energy": q(120, "GeV", "120 GeV", "energy"),
                "beam_power": q(900, "kW", "900 kW", "power")}),
    dict(id="accelerator:fermilab-booster", name="Booster", aliases=[], kind="booster",
         facility_id="facility:fermilab", site_id="site:fermilab-batavia", is_collider=False,
         particles=["proton"], feeds_accelerator_ids=["accelerator:fermilab-main-injector"],
         intervals=[iv("active", "1970-09")],
         specs={"beam_energy": q(8, "GeV", "8 GeV", "energy")}),
    dict(id="accelerator:jparc-mr", name="J-PARC Main Ring", aliases=["MR"], kind="synchrotron",
         facility_id="facility:j-parc", site_id="site:jparc-tokai", is_collider=False,
         particles=["proton"], feeds_accelerator_ids=[],
         intervals=[iv("commissioning", "2008-05", "2009-04"), iv("active", "2009-04")],
         specs={"beam_energy": q(30, "GeV", "30 GeV", "energy"),
                "beam_power": q(760, "kW", "760 kW", "power")}),
    dict(id="accelerator:superkekb", name="SuperKEKB", aliases=[], kind="collider",
         facility_id="facility:kek", site_id="site:kek-tsukuba", is_collider=True,
         particles=["electron", "positron"], feeds_accelerator_ids=[],
         intervals=[iv("construction", "2011-01", "2016-02"), iv("commissioning", "2016-02", "2018-03"),
                    iv("active", "2018-03", "2022-06"), iv("upgrade", "2022-07", "2024-01"),
                    iv("active", "2024-02")],
         specs={"cms_energy": q(10.58, "GeV", "10.58 GeV", "energy"),
                "peak_luminosity": q(5.1e34, "cm^-2 s^-1", "5.1 × 10³⁴ cm⁻² s⁻¹", "luminosity"),
                "circumference": q(3016, "m", "3.016 km", "length")}),
]

BEAMLINES = [
    dict(id="beamline:lbnf", name="LBNF neutrino beamline", aliases=["LBNF"],
         facility_id="facility:fermilab", accelerator_id="accelerator:fermilab-main-injector",
         primary_beam={"particle": "proton", "energy": q(120, "GeV", "120 GeV", "energy")},
         target="1.5 m graphite target", secondary_beam="muon neutrinos / antineutrinos, on-axis",
         direction="north-west, 5.8° downward towards Lead, South Dakota",
         near_detector_site_ids=["site:fermilab-nd-hall"],
         far_detector_site_ids=["site:surf-dune-caverns"],
         baselines=[("site:fermilab-batavia", "site:surf-dune-caverns", 1285, "1285 km")],
         intervals=[iv("construction", "2017-07")],
         specs={"beam_power": q(1200, "kW", "1.2 MW at start-up", "power"),
                "baseline": q(1285, "km", "1285 km", "length")}),
    dict(id="beamline:numi", name="NuMI neutrino beamline", aliases=["NuMI"],
         facility_id="facility:fermilab", accelerator_id="accelerator:fermilab-main-injector",
         primary_beam={"particle": "proton", "energy": q(120, "GeV", "120 GeV", "energy")},
         target="graphite target", secondary_beam="muon neutrinos / antineutrinos, 14.6 mrad off-axis for NOvA",
         direction="north, 3.3° downward towards Ash River, Minnesota",
         near_detector_site_ids=["site:fermilab-minos-hall"],
         far_detector_site_ids=["site:nova-ash-river"],
         baselines=[("site:fermilab-batavia", "site:nova-ash-river", 810, "810 km")],
         intervals=[iv("active", "2005-01")],
         specs={"beam_power": q(900, "kW", "900 kW", "power"),
                "off_axis_angle": q(14.6, "mrad", "14.6 mrad", "angle"),
                "baseline": q(810, "km", "810 km", "length")}),
    dict(id="beamline:bnb", name="Booster Neutrino Beam", aliases=["BNB"],
         facility_id="facility:fermilab", accelerator_id="accelerator:fermilab-booster",
         primary_beam={"particle": "proton", "energy": q(8, "GeV", "8 GeV", "energy")},
         target="beryllium target", secondary_beam="muon neutrinos, on-axis",
         direction="north-east along the Booster neutrino line",
         near_detector_site_ids=["site:fermilab-sbnd-hall"],
         far_detector_site_ids=["site:fermilab-icarus-hall"],
         baselines=[("site:fermilab-sbnd-hall", "site:fermilab-icarus-hall", 0.49, "0.49 km")],
         intervals=[iv("active", "2002-08")],
         specs={"peak_neutrino_energy": q(800, "MeV", "800 MeV", "energy")}),
    dict(id="beamline:jparc-neutrino", name="J-PARC neutrino beamline", aliases=["T2K beamline"],
         facility_id="facility:j-parc", accelerator_id="accelerator:jparc-mr",
         primary_beam={"particle": "proton", "energy": q(30, "GeV", "30 GeV", "energy")},
         target="graphite target", secondary_beam="muon neutrinos / antineutrinos, 2.5° off-axis",
         direction="west-south-west towards the Kamioka mine",
         near_detector_site_ids=["site:jparc-nd280"],
         far_detector_site_ids=["site:super-k-cavern"],
         baselines=[("site:jparc-tokai", "site:super-k-cavern", 295, "295 km")],
         intervals=[iv("commissioning", "2009-04", "2010-01"), iv("active", "2010-01")],
         specs={"beam_power": q(760, "kW", "760 kW", "power"),
                "off_axis_angle": q(2.5, "deg", "2.5°", "angle"),
                "baseline": q(295, "km", "295 km", "length")}),
]

# --------------------------------------------------------------------------
# topics

TOPICS = [
    ("topic:neutrino-physics", "Neutrino physics", None,
     "What are neutrinos, and why are they so much lighter than every other particle we know?",
     ["neutrino flux", "interaction cross sections"]),
    ("topic:neutrino-oscillations", "Neutrino oscillations", "topic:neutrino-physics",
     "Neutrinos change type as they travel. What exactly sets the rhythm of that change?",
     ["Δm²₂₁", "Δm²₃₂", "sin²θ₁₂", "sin²θ₂₃", "sin²θ₁₃"]),
    ("topic:leptonic-cp-violation", "Leptonic CP violation", "topic:neutrino-oscillations",
     "Do neutrinos and antineutrinos behave differently — enough to explain why the universe kept any matter at all?",
     ["δ_CP", "ν_e appearance rate", "ν̄_e appearance rate"]),
    ("topic:mass-ordering", "Neutrino mass ordering", "topic:neutrino-oscillations",
     "Which neutrino is heaviest?",
     ["sign of Δm²₃₁", "matter-effect asymmetry"]),
    ("topic:sterile-neutrinos", "Sterile neutrinos", "topic:neutrino-physics",
     "Is there a fourth kind of neutrino that ignores every force except gravity?",
     ["short-baseline ν_e appearance", "ν_μ disappearance", "Δm²₄₁"]),
    ("topic:neutrino-astronomy", "Neutrino astronomy", "topic:neutrino-physics",
     "Which objects in the sky are accelerating particles to energies no accelerator on Earth can reach?",
     ["astrophysical ν flux", "point-source significance", "diffuse spectrum index"]),
    ("topic:electroweak-symmetry-breaking", "Electroweak symmetry breaking", None,
     "Why do the W and Z bosons have mass while the photon does not?",
     ["m_W", "m_Z", "sin²θ_W"]),
    ("topic:higgs-boson", "Higgs boson", "topic:electroweak-symmetry-breaking",
     "Is the particle found in 2012 exactly the Higgs boson the Standard Model predicted?",
     ["m_H", "signal strength μ", "coupling modifiers κ"]),
    ("topic:dark-matter", "Dark matter", None,
     "Five sixths of the matter in the universe is something we have never detected in a laboratory. What is it?",
     ["relic density", "nuclear recoil rate"]),
    ("topic:wimp-direct-detection", "WIMP direct detection", "topic:dark-matter",
     "If dark matter particles pass through us constantly, can we catch one recoiling off a nucleus?",
     ["spin-independent cross section", "nuclear recoil energy spectrum"]),
    ("topic:flavour-physics", "Flavour physics", None,
     "Why are there three copies of each matter particle, and what decides how they mix?",
     ["CKM matrix elements", "branching fractions"]),
    ("topic:b-meson-decays", "B meson decays", "topic:flavour-physics",
     "Do rare B meson decays happen at the rate the Standard Model demands, or is something else interfering?",
     ["sin2φ₁", "B → K*ℓℓ angular observables", "R(D*)"]),
    ("topic:qcd-and-heavy-ions", "QCD and heavy ions", None,
     "What does matter look like when it is hot and dense enough to melt protons?",
     ["elliptic flow v₂", "jet quenching R_AA"]),
]


# --------------------------------------------------------------------------
# experiments

EXPERIMENTS = [
    dict(id="experiment:atlas", name="ATLAS", aliases=["A Toroidal LHC ApparatuS"], kind="collider",
         collaboration_ids=["collaboration:atlas"],
         facility_roles=[("facility:cern", "host")], site_ids=["site:cern-lhc-point-1"],
         detector_ids=["detector:atlas"], beamline_ids=[], accelerator_ids=["accelerator:lhc"],
         topic_ids=["topic:higgs-boson", "topic:electroweak-symmetry-breaking", "topic:qcd-and-heavy-ions"],
         energy_regime="13.6 TeV proton–proton collisions",
         key_specs=[("Centre-of-mass energy", q(13600, "GeV", "13.6 TeV", "energy")),
                    ("Detector mass", q(7000, "t", "7000 t", "mass")),
                    ("Length", q(46, "m", "46 m", "length"))],
         intervals=[iv("proposed", "1992-10", "1994-12", label="letter of intent"),
                    iv("approved", "1995-01", "1998-04"),
                    iv("construction", "1998-04", "2008-05"),
                    iv("commissioning", "2008-05", "2009-11"),
                    iv("active", "2009-11", "2013-02"),
                    iv("shutdown", "2013-02", "2015-04", label="LS1"),
                    iv("active", "2015-04", "2018-12"),
                    iv("shutdown", "2018-12", "2022-07", label="LS2"),
                    iv("active", "2022-07")],
         lineage=[], external={"inspire_experiment": 1108541, "greybook": "LHC-ATLAS"},
         website="https://atlas.cern/"),
    dict(id="experiment:cms", name="CMS", aliases=["Compact Muon Solenoid"], kind="collider",
         collaboration_ids=["collaboration:cms"],
         facility_roles=[("facility:cern", "host")], site_ids=["site:cern-lhc-point-5"],
         detector_ids=["detector:cms"], beamline_ids=[], accelerator_ids=["accelerator:lhc"],
         topic_ids=["topic:higgs-boson", "topic:electroweak-symmetry-breaking", "topic:qcd-and-heavy-ions"],
         energy_regime="13.6 TeV proton–proton collisions",
         key_specs=[("Centre-of-mass energy", q(13600, "GeV", "13.6 TeV", "energy")),
                    ("Detector mass", q(14000, "t", "14 000 t", "mass")),
                    ("Solenoid field", q(3.8, "T", "3.8 T", "magnetic_field"))],
         intervals=[iv("proposed", "1992-10", "1994-12", label="letter of intent"),
                    iv("approved", "1995-01", "1998-04"),
                    iv("construction", "1998-04", "2008-05"),
                    iv("commissioning", "2008-05", "2009-11"),
                    iv("active", "2009-11", "2013-02"),
                    iv("shutdown", "2013-02", "2015-04", label="LS1"),
                    iv("active", "2015-04", "2018-12"),
                    iv("shutdown", "2018-12", "2022-07", label="LS2"),
                    iv("active", "2022-07")],
         lineage=[], external={"inspire_experiment": 1108642, "greybook": "LHC-CMS"},
         website="https://cms.cern/"),
    dict(id="experiment:dune", name="DUNE", aliases=["Deep Underground Neutrino Experiment", "LBNF/DUNE"],
         kind="accelerator_neutrino", collaboration_ids=["collaboration:dune"],
         facility_roles=[("facility:fermilab", "beam_source"), ("facility:surf", "detector_host"),
                         ("facility:cern", "prototype_host")],
         site_ids=["site:fermilab-nd-hall", "site:surf-dune-caverns"],
         detector_ids=["detector:dune-fd-hd", "detector:dune-nd-lar"],
         beamline_ids=["beamline:lbnf"], accelerator_ids=["accelerator:fermilab-main-injector"],
         topic_ids=["topic:leptonic-cp-violation", "topic:mass-ordering", "topic:neutrino-oscillations",
                    "topic:neutrino-astronomy"],
         energy_regime="0.5–5 GeV wide-band muon neutrino beam",
         key_specs=[("Baseline", q(1285, "km", "1285 km", "length")),
                    ("Far detector fiducial mass", q(40000, "t", "40 kt (four modules)", "mass")),
                    ("Overburden", q(4300, "m.w.e.", "4300 m.w.e.", "depth_mwe")),
                    ("Beam power", q(1200, "kW", "1.2 MW at start-up", "power"))],
         intervals=[iv("proposed", "2013-01", "2015-04"),
                    iv("approved", "2015-04", "2017-07"),
                    iv("construction", "2017-07"),
                    iv("active", "2029", planned=True)],
         lineage=[("experiment:nova", "same_program")],
         external={"inspire_experiment": 1346843, "greybook": "FNAL-E-1062"},
         website="https://www.dunescience.org/"),
    dict(id="experiment:nova", name="NOvA", aliases=["NuMI Off-axis ν_e Appearance"],
         kind="accelerator_neutrino", collaboration_ids=["collaboration:nova"],
         facility_roles=[("facility:fermilab", "host")],
         site_ids=["site:fermilab-minos-hall", "site:nova-ash-river"],
         detector_ids=["detector:nova-fd", "detector:nova-nd"],
         beamline_ids=["beamline:numi"], accelerator_ids=["accelerator:fermilab-main-injector"],
         topic_ids=["topic:neutrino-oscillations", "topic:mass-ordering", "topic:leptonic-cp-violation"],
         energy_regime="2 GeV off-axis muon neutrino beam",
         key_specs=[("Baseline", q(810, "km", "810 km", "length")),
                    ("Far detector mass", q(14000, "t", "14 000 t", "mass")),
                    ("Off-axis angle", q(14.6, "mrad", "14.6 mrad", "angle"))],
         intervals=[iv("proposed", "2004-03", "2008-01"), iv("approved", "2008-01", "2009-05"),
                    iv("construction", "2009-05", "2014-02"), iv("active", "2014-02")],
         lineage=[("experiment:t2k", "complementary")],
         external={"inspire_experiment": 1108176, "greybook": "FNAL-E-0929"},
         website="https://novaexperiment.fnal.gov/"),
    dict(id="experiment:sbnd", name="SBND", aliases=["Short-Baseline Near Detector"],
         kind="accelerator_neutrino", secondary_kinds=["sterile_neutrino"],
         collaboration_ids=["collaboration:sbnd"],
         facility_roles=[("facility:fermilab", "host")], site_ids=["site:fermilab-sbnd-hall"],
         detector_ids=["detector:sbnd"], beamline_ids=["beamline:bnb"],
         accelerator_ids=["accelerator:fermilab-booster"],
         topic_ids=["topic:sterile-neutrinos", "topic:neutrino-oscillations"],
         energy_regime="800 MeV Booster neutrino beam",
         key_specs=[("Baseline", q(0.11, "km", "110 m", "length")),
                    ("Active LAr mass", q(112, "t", "112 t", "mass"))],
         intervals=[iv("approved", "2015-02", "2018-01"), iv("construction", "2018-01", "2024-07"),
                    iv("commissioning", "2024-07", "2025-02"), iv("active", "2025-02")],
         lineage=[("experiment:icarus", "same_program")],
         external={"greybook": "FNAL-E-1127"}, website="https://sbn-nd.fnal.gov/"),
    dict(id="experiment:icarus", name="ICARUS", aliases=["ICARUS T600"],
         kind="accelerator_neutrino", secondary_kinds=["sterile_neutrino"],
         collaboration_ids=["collaboration:icarus"],
         facility_roles=[("facility:fermilab", "host")], site_ids=["site:fermilab-icarus-hall"],
         detector_ids=["detector:icarus-t600"], beamline_ids=["beamline:bnb"],
         accelerator_ids=["accelerator:fermilab-booster"],
         topic_ids=["topic:sterile-neutrinos"],
         energy_regime="800 MeV Booster neutrino beam",
         key_specs=[("Baseline", q(0.6, "km", "600 m", "length")),
                    ("Active LAr mass", q(476, "t", "476 t", "mass"))],
         intervals=[iv("active", "2010-10", "2013-06", label="LNGS running"),
                    iv("upgrade", "2014-06", "2020-08", label="overhaul and move to Fermilab"),
                    iv("commissioning", "2020-08", "2022-06"), iv("active", "2022-06")],
         lineage=[], external={"greybook": "FNAL-E-1118"}, website="https://icarus.fnal.gov/"),
    dict(id="experiment:t2k", name="T2K", aliases=["Tokai to Kamioka"], kind="accelerator_neutrino",
         collaboration_ids=["collaboration:t2k"],
         facility_roles=[("facility:j-parc", "beam_source"),
                         ("facility:kamioka-observatory", "detector_host")],
         site_ids=["site:jparc-nd280", "site:super-k-cavern"],
         detector_ids=["detector:nd280"], beamline_ids=["beamline:jparc-neutrino"],
         accelerator_ids=["accelerator:jparc-mr"],
         topic_ids=["topic:leptonic-cp-violation", "topic:neutrino-oscillations"],
         energy_regime="0.6 GeV off-axis muon neutrino beam",
         key_specs=[("Baseline", q(295, "km", "295 km", "length")),
                    ("Off-axis angle", q(2.5, "deg", "2.5°", "angle")),
                    ("Far detector", q(50000, "t", "Super-Kamiokande, 50 kt", "mass"))],
         intervals=[iv("proposed", "2003-01", "2004-04"), iv("construction", "2004-04", "2009-04"),
                    iv("commissioning", "2009-04", "2010-01"), iv("active", "2010-01")],
         lineage=[], external={"inspire_experiment": 1110111, "greybook": "J-PARC-T2K"},
         website="https://t2k-experiment.org/"),
    dict(id="experiment:super-kamiokande", name="Super-Kamiokande", aliases=["Super-K", "SK"],
         kind="atmospheric_neutrino", secondary_kinds=["solar_neutrino", "astrophysical_neutrino"],
         collaboration_ids=["collaboration:super-kamiokande"],
         facility_roles=[("facility:kamioka-observatory", "host")], site_ids=["site:super-k-cavern"],
         detector_ids=["detector:super-kamiokande"], beamline_ids=[], accelerator_ids=[],
         topic_ids=["topic:neutrino-oscillations", "topic:neutrino-astronomy"],
         energy_regime="MeV–TeV atmospheric, solar and accelerator neutrinos",
         key_specs=[("Total water mass", q(50000, "t", "50 000 t", "mass")),
                    ("Overburden", q(2700, "m.w.e.", "2700 m.w.e.", "depth_mwe")),
                    ("Photomultipliers", q(11129, "", "11 129 inner-detector PMTs", "count"))],
         intervals=[iv("construction", "1991-12", "1996-04"), iv("active", "1996-04", "2001-11"),
                    iv("shutdown", "2001-11", "2002-12", label="PMT implosion repair"),
                    iv("active", "2002-12", "2018-05"),
                    iv("upgrade", "2018-05", "2020-07", label="gadolinium loading"),
                    iv("active", "2020-07")],
         lineage=[], external={"inspire_experiment": 1110357}, website="https://www-sk.icrr.u-tokyo.ac.jp/en/sk/"),
    dict(id="experiment:icecube", name="IceCube", aliases=["IceCube Neutrino Observatory"],
         kind="astrophysical_neutrino", secondary_kinds=["cosmic_ray", "atmospheric_neutrino"],
         collaboration_ids=["collaboration:icecube"],
         facility_roles=[("facility:amundsen-scott", "host")], site_ids=["site:icecube-array"],
         detector_ids=["detector:icecube-in-ice", "detector:icecube-deepcore"],
         beamline_ids=[], accelerator_ids=[],
         topic_ids=["topic:neutrino-astronomy", "topic:neutrino-oscillations"],
         energy_regime="10 GeV – 10 PeV neutrinos in Antarctic ice",
         key_specs=[("Instrumented volume", q(1, "km^3", "1 km³", "volume")),
                    ("Optical modules", q(5160, "", "5160 DOMs on 86 strings", "count")),
                    ("Depth range", q(2450, "m", "1450–2450 m in the ice", "length"))],
         intervals=[iv("construction", "2004-11", "2010-12"),
                    iv("commissioning", "2006-06", "2010-12", label="partial-array running"),
                    iv("active", "2010-12")],
         lineage=[], external={"inspire_experiment": 1108587}, website="https://icecube.wisc.edu/"),
    dict(id="experiment:lz", name="LZ", aliases=["LUX-ZEPLIN"], kind="direct_dark_matter",
         collaboration_ids=["collaboration:lz"],
         facility_roles=[("facility:surf", "host")], site_ids=["site:surf-davis-campus"],
         detector_ids=["detector:lz"], beamline_ids=[], accelerator_ids=[],
         topic_ids=["topic:wimp-direct-detection", "topic:dark-matter"],
         energy_regime="keV-scale nuclear recoils",
         key_specs=[("Active xenon mass", q(7, "t", "7 t", "mass")),
                    ("Exposure (2024)", q(4.2, "t yr", "4.2 t yr", "exposure")),
                    ("Overburden", q(4300, "m.w.e.", "4300 m.w.e.", "depth_mwe"))],
         intervals=[iv("approved", "2012-07", "2016-01"), iv("construction", "2016-01", "2021-12"),
                    iv("commissioning", "2021-12", "2022-03"), iv("active", "2022-03")],
         lineage=[], external={"inspire_experiment": 1372923}, website="https://lz.lbl.gov/"),
    dict(id="experiment:belle-2", name="Belle II", aliases=["BelleII"], kind="collider",
         collaboration_ids=["collaboration:belle-2"],
         facility_roles=[("facility:kek", "host")], site_ids=["site:kek-tsukuba"],
         detector_ids=["detector:belle-2"], beamline_ids=[], accelerator_ids=["accelerator:superkekb"],
         topic_ids=["topic:b-meson-decays", "topic:flavour-physics"],
         energy_regime="10.58 GeV electron–positron collisions at the Υ(4S)",
         key_specs=[("Centre-of-mass energy", q(10.58, "GeV", "10.58 GeV", "energy")),
                    ("Target integrated luminosity", q(50, "ab^-1", "50 ab⁻¹", "luminosity")),
                    ("Peak luminosity", q(5.1e34, "cm^-2 s^-1", "5.1 × 10³⁴ cm⁻² s⁻¹", "luminosity"))],
         intervals=[iv("proposed", "2004-06", "2010-11"), iv("approved", "2010-11", "2011-01"),
                    iv("construction", "2011-01", "2018-03"),
                    iv("commissioning", "2018-03", "2019-03"),
                    iv("active", "2019-03", "2022-06"),
                    iv("upgrade", "2022-07", "2024-01", label="LS1: pixel detector completion"),
                    iv("active", "2024-02")],
         lineage=[("experiment:belle", "upgrade_of")],
         external={"inspire_experiment": 1108570}, website="https://www.belle2.org/"),
    dict(id="experiment:belle", name="Belle", aliases=[], kind="collider",
         collaboration_ids=["collaboration:belle"],
         facility_roles=[("facility:kek", "host")], site_ids=["site:kek-tsukuba"],
         detector_ids=[], beamline_ids=[], accelerator_ids=[],
         topic_ids=["topic:b-meson-decays", "topic:flavour-physics"],
         energy_regime="10.58 GeV electron–positron collisions at KEKB",
         key_specs=[("Integrated luminosity", q(1041, "fb^-1", "1041 fb⁻¹", "luminosity"))],
         intervals=[iv("construction", "1994-04", "1999-06"), iv("active", "1999-06", "2010-06"),
                    iv("completed", "2010-06", "2010-06")],
         lineage=[], external={"inspire_experiment": 1108604}, website="https://belle.kek.jp/"),
    dict(id="experiment:ua1", name="UA1", aliases=["Underground Area 1"], kind="collider",
         collaboration_ids=["collaboration:ua1"],
         facility_roles=[("facility:cern", "host")], site_ids=["site:cern-sps-lss5"],
         detector_ids=["detector:ua1"], beamline_ids=[], accelerator_ids=["accelerator:sps"],
         topic_ids=["topic:electroweak-symmetry-breaking"],
         energy_regime="546–630 GeV proton–antiproton collisions",
         key_specs=[("Centre-of-mass energy", q(630, "GeV", "630 GeV", "energy")),
                    ("Dipole field", q(0.7, "T", "0.7 T", "magnetic_field")),
                    ("Detector mass", q(2000, "t", "2000 t", "mass"))],
         intervals=[iv("proposed", "1978-01", "1978-06"), iv("approved", "1978-06", "1979-01"),
                    iv("construction", "1979-01", "1981-07"), iv("active", "1981-07", "1990-12"),
                    iv("completed", "1990-12", "1990-12"),
                    iv("decommissioned", "1993-01", "1993-01")],
         lineage=[], external={"inspire_experiment": 1110586, "greybook": "CERN-SPS-UA1"},
         website="https://home.cern/science/experiments/ua1"),
]


# --------------------------------------------------------------------------
# detectors

DETECTORS = [
    dict(id="detector:atlas", name="ATLAS detector", experiment_ids=["experiment:atlas"],
         technology="general-purpose collider detector with a toroidal muon spectrometer",
         technology_classes=["general_purpose_collider"],
         placements=[("site:cern-lhc-point-1", "main", "2008-05", None)],
         intervals=[iv("construction", "1998-04", "2008-05"), iv("active", "2008-05")],
         specs={"total_mass": q(7000, "t", "7000 t", "mass"), "length": q(46, "m", "46 m", "length"),
                "diameter": q(25, "m", "25 m", "length"),
                "solenoid_field": q(2.0, "T", "2 T", "magnetic_field")},
         subsystems=[("Inner detector", "Silicon pixel, silicon strip and transition-radiation tracking inside a 2 T solenoid."),
                     ("Calorimeters", "Liquid-argon electromagnetic and scintillator-tile hadronic calorimetry."),
                     ("Muon spectrometer", "Air-core toroid magnets with precision drift tubes and trigger chambers.")]),
    dict(id="detector:cms", name="CMS detector", experiment_ids=["experiment:cms"],
         technology="general-purpose collider detector built around a 3.8 T solenoid",
         technology_classes=["general_purpose_collider"],
         placements=[("site:cern-lhc-point-5", "main", "2008-05", None)],
         intervals=[iv("construction", "1998-04", "2008-05"), iv("active", "2008-05")],
         specs={"total_mass": q(14000, "t", "14 000 t", "mass"), "length": q(21.6, "m", "21.6 m", "length"),
                "solenoid_field": q(3.8, "T", "3.8 T", "magnetic_field")},
         subsystems=[("Silicon tracker", "The largest silicon tracker built, 200 m² of active area."),
                     ("Crystal calorimeter", "75 848 lead-tungstate scintillating crystals.")]),
    dict(id="detector:dune-fd-hd", name="DUNE far detector, horizontal-drift module",
         experiment_ids=["experiment:dune"], technology="single-phase liquid argon time projection chamber",
         technology_classes=["noble_liquid_tpc", "lar_tpc"],
         placements=[("site:surf-dune-caverns", "far", "2028", None)],
         intervals=[iv("construction", "2022-01"), iv("active", "2029", planned=True)],
         specs={"total_mass": q(17500, "t", "17.5 kt of liquid argon", "mass"),
                "fiducial_mass": q(10000, "t", "10 kt fiducial", "mass"),
                "drift_field": q(500, "V/cm", "500 V/cm", "electric_field"),
                "target_medium": q(0, "", "liquid argon", "fraction")},
         subsystems=[("Anode plane assemblies", "150 APAs carrying wrapped wire planes for three readout views."),
                     ("Cryostat", "Membrane cryostat holding 17.5 kt of liquid argon at 87 K.")]),
    dict(id="detector:dune-nd-lar", name="DUNE near detector, ND-LAr",
         experiment_ids=["experiment:dune"], technology="modular pixelated liquid argon TPC",
         technology_classes=["noble_liquid_tpc", "lar_tpc"],
         placements=[("site:fermilab-nd-hall", "near", "2030", None)],
         intervals=[iv("construction", "2024-01"), iv("active", "2031", planned=True)],
         specs={"total_mass": q(147, "t", "147 t", "mass")}, subsystems=[]),
    dict(id="detector:nova-fd", name="NOvA far detector", experiment_ids=["experiment:nova"],
         technology="segmented liquid scintillator tracking calorimeter",
         technology_classes=["tracking_calorimeter", "liquid_scintillator"],
         placements=[("site:nova-ash-river", "far", "2014-02", None)],
         intervals=[iv("construction", "2012-01", "2014-02"), iv("active", "2014-02")],
         specs={"total_mass": q(14000, "t", "14 000 t", "mass")}, subsystems=[]),
    dict(id="detector:nova-nd", name="NOvA near detector", experiment_ids=["experiment:nova"],
         technology="segmented liquid scintillator tracking calorimeter",
         technology_classes=["tracking_calorimeter", "liquid_scintillator"],
         placements=[("site:fermilab-minos-hall", "near", "2013-08", None)],
         intervals=[iv("active", "2013-08")],
         specs={"total_mass": q(300, "t", "300 t", "mass")}, subsystems=[]),
    dict(id="detector:sbnd", name="SBND detector", experiment_ids=["experiment:sbnd"],
         technology="single-phase liquid argon TPC", technology_classes=["noble_liquid_tpc", "lar_tpc"],
         placements=[("site:fermilab-sbnd-hall", "near", "2024-07", None)],
         intervals=[iv("construction", "2018-01", "2024-07"), iv("active", "2024-07")],
         specs={"total_mass": q(112, "t", "112 t active", "mass")}, subsystems=[]),
    dict(id="detector:icarus-t600", name="ICARUS T600", experiment_ids=["experiment:icarus"],
         technology="single-phase liquid argon TPC", technology_classes=["noble_liquid_tpc", "lar_tpc"],
         placements=[("site:fermilab-icarus-hall", "far", "2020-08", None)],
         intervals=[iv("active", "2010-10", "2013-06"), iv("upgrade", "2014-06", "2020-08"),
                    iv("active", "2020-08")],
         specs={"total_mass": q(476, "t", "476 t active", "mass")}, subsystems=[]),
    dict(id="detector:nd280", name="ND280", experiment_ids=["experiment:t2k"],
         technology="magnetised tracker with fine-grained targets and TPCs",
         technology_classes=["gaseous_tpc", "tracking_calorimeter"],
         placements=[("site:jparc-nd280", "near", "2009-11", None)],
         intervals=[iv("active", "2009-11", "2022-06"), iv("upgrade", "2022-06", "2024-06"),
                    iv("active", "2024-06")],
         specs={"magnetic_field": q(0.2, "T", "0.2 T", "magnetic_field")}, subsystems=[]),
    dict(id="detector:super-kamiokande", name="Super-Kamiokande detector",
         experiment_ids=["experiment:super-kamiokande", "experiment:t2k"],
         technology="water Cherenkov detector", technology_classes=["water_cherenkov"],
         placements=[("site:super-k-cavern", "main", "1996-04", None)],
         intervals=[iv("active", "1996-04", "2001-11"), iv("shutdown", "2001-11", "2002-12"),
                    iv("active", "2002-12", "2018-05"), iv("upgrade", "2018-05", "2020-07"),
                    iv("active", "2020-07")],
         specs={"total_mass": q(50000, "t", "50 000 t of ultrapure water", "mass"),
                "fiducial_mass": q(22500, "t", "22.5 kt fiducial", "mass"),
                "pmt_count": q(11129, "", "11 129 inner PMTs", "count")},
         subsystems=[("Inner detector", "32 kt of water viewed by 11 129 50 cm photomultipliers."),
                     ("Outer detector", "A 2 m veto shell with 1885 outward-facing 20 cm PMTs.")]),
    dict(id="detector:icecube-in-ice", name="IceCube in-ice array", experiment_ids=["experiment:icecube"],
         technology="digital optical modules frozen into deep Antarctic ice",
         technology_classes=["ice_cherenkov"],
         placements=[("site:icecube-array", "main", "2010-12", None)],
         intervals=[iv("construction", "2004-11", "2010-12"), iv("active", "2010-12")],
         specs={"instrumented_volume": q(1, "km^3", "1 km³", "volume"),
                "module_count": q(5160, "", "5160 DOMs", "count")}, subsystems=[]),
    dict(id="detector:icecube-deepcore", name="DeepCore", experiment_ids=["experiment:icecube"],
         technology="dense infill array of optical modules", technology_classes=["ice_cherenkov"],
         parent_detector_id="detector:icecube-in-ice",
         placements=[("site:icecube-array", "main", "2010-12", None)],
         intervals=[iv("active", "2010-12")],
         specs={"module_count": q(480, "", "480 DOMs on 8 strings", "count")}, subsystems=[]),
    dict(id="detector:lz", name="LZ detector", experiment_ids=["experiment:lz"],
         technology="dual-phase xenon time projection chamber",
         technology_classes=["noble_liquid_tpc", "xenon_tpc"],
         placements=[("site:surf-davis-campus", "main", "2021-12", None)],
         intervals=[iv("construction", "2016-01", "2021-12"), iv("active", "2021-12")],
         specs={"total_mass": q(10, "t", "10 t of liquid xenon", "mass"),
                "fiducial_mass": q(5.5, "t", "5.5 t fiducial", "mass"),
                "drift_field": q(193, "V/cm", "193 V/cm", "electric_field")},
         subsystems=[("Outer detector", "Gadolinium-loaded liquid scintillator surrounding the cryostat.")]),
    dict(id="detector:belle-2", name="Belle II detector", experiment_ids=["experiment:belle-2"],
         technology="hermetic collider detector with a pixel vertex detector",
         technology_classes=["general_purpose_collider"],
         placements=[("site:kek-tsukuba", "main", "2018-03", None)],
         intervals=[iv("construction", "2011-01", "2018-03"), iv("active", "2018-03")],
         specs={"solenoid_field": q(1.5, "T", "1.5 T", "magnetic_field")},
         subsystems=[("Pixel detector", "Two DEPFET layers within 2.2 cm of the beam pipe.")]),
    dict(id="detector:ua1", name="UA1 detector", experiment_ids=["experiment:ua1"],
         technology="dipole-magnet central detector with hermetic calorimetry",
         technology_classes=["spectrometer", "tracking_calorimeter"],
         placements=[("site:cern-sps-lss5", "main", "1981-07", "1990-12")],
         intervals=[iv("construction", "1979-01", "1981-07"), iv("active", "1981-07", "1990-12"),
                    iv("decommissioned", "1993-01", "1993-01")],
         specs={"total_mass": q(2000, "t", "2000 t", "mass"),
                "magnetic_field": q(0.7, "T", "0.7 T dipole", "magnetic_field")},
         subsystems=[("Central detector", "A 6 m drift chamber imaging tracks in the dipole field.")]),
]


# --------------------------------------------------------------------------
# collaborations

COLLABORATIONS = [
    dict(id="collaboration:atlas", name="ATLAS Collaboration", experiment_ids=["experiment:atlas"],
         formation="1992-10", host_facility_id="facility:cern", host_site_id="site:cern-lhc-point-1",
         intervals=[iv("active", "1992-10")], institution_count=257, country_count=42,
         member_count=5900, membership_history="partial",
         leadership=[("spokesperson", "person:unresolved-atlas-cern-spokesperson", "M. Aubertin", "2025-03", None)]),
    dict(id="collaboration:cms", name="CMS Collaboration", experiment_ids=["experiment:cms"],
         formation="1992-10", host_facility_id="facility:cern", host_site_id="site:cern-lhc-point-5",
         intervals=[iv("active", "1992-10")], institution_count=241, country_count=54,
         member_count=5500, membership_history="unknown", leadership=[]),
    dict(id="collaboration:dune", name="DUNE Collaboration", experiment_ids=["experiment:dune"],
         formation="2015-04", host_facility_id="facility:fermilab", host_site_id="site:surf-dune-caverns",
         intervals=[iv("active", "2015-04")], institution_count=209, country_count=37,
         member_count=1400, membership_history="partial",
         leadership=[("spokesperson", "person:unresolved-dune-fermilab-cospokesperson", "R. Okonjo", "2024-02", None),
                     ("deputy_spokesperson", "person:unresolved-dune-imperial-college-london-deputy", "H. Lindqvist", "2024-02", None)]),
    dict(id="collaboration:nova", name="NOvA Collaboration", experiment_ids=["experiment:nova"],
         formation="2004-03", host_facility_id="facility:fermilab", host_site_id="site:nova-ash-river",
         intervals=[iv("active", "2004-03")], institution_count=49, country_count=8,
         member_count=250, membership_history="partial", leadership=[]),
    dict(id="collaboration:sbnd", name="SBND Collaboration", experiment_ids=["experiment:sbnd"],
         formation="2015-02", host_facility_id="facility:fermilab", host_site_id="site:fermilab-sbnd-hall",
         intervals=[iv("active", "2015-02")], institution_count=40, country_count=7,
         member_count=250, membership_history="unknown", leadership=[]),
    dict(id="collaboration:icarus", name="ICARUS Collaboration", experiment_ids=["experiment:icarus"],
         formation="1991-01", host_facility_id="facility:fermilab", host_site_id="site:fermilab-icarus-hall",
         intervals=[iv("active", "1991-01")], institution_count=25, country_count=6,
         member_count=150, membership_history="unknown", leadership=[]),
    dict(id="collaboration:t2k", name="T2K Collaboration", experiment_ids=["experiment:t2k"],
         formation="2003-01", host_facility_id="facility:j-parc", host_site_id="site:jparc-nd280",
         intervals=[iv("active", "2003-01")], institution_count=78, country_count=14,
         member_count=560, membership_history="partial", leadership=[]),
    dict(id="collaboration:super-kamiokande", name="Super-Kamiokande Collaboration",
         experiment_ids=["experiment:super-kamiokande"], formation="1991-04",
         host_facility_id="facility:kamioka-observatory", host_site_id="site:super-k-cavern",
         intervals=[iv("active", "1991-04")], institution_count=48, country_count=9,
         member_count=200, membership_history="partial", leadership=[]),
    dict(id="collaboration:icecube", name="IceCube Collaboration", experiment_ids=["experiment:icecube"],
         formation="1999-09", host_facility_id="facility:amundsen-scott", host_site_id="site:icecube-array",
         intervals=[iv("active", "1999-09")], institution_count=58, country_count=14,
         member_count=350, membership_history="partial",
         leadership=[("spokesperson", "person:unresolved-icecube-university-of-wisconsin-madison-spokesperson", "D. Arinze", "2023-05", None)]),
    dict(id="collaboration:lz", name="LZ Collaboration", experiment_ids=["experiment:lz"],
         formation="2012-07", host_facility_id="facility:surf", host_site_id="site:surf-davis-campus",
         intervals=[iv("active", "2012-07")], institution_count=38, country_count=5,
         member_count=250, membership_history="partial", leadership=[]),
    dict(id="collaboration:belle-2", name="Belle II Collaboration", experiment_ids=["experiment:belle-2"],
         formation="2008-11", host_facility_id="facility:kek", host_site_id="site:kek-tsukuba",
         intervals=[iv("active", "2008-11")], institution_count=122, country_count=28,
         member_count=1200, membership_history="partial", leadership=[]),
    dict(id="collaboration:belle", name="Belle Collaboration", experiment_ids=["experiment:belle"],
         formation="1994-04", host_facility_id="facility:kek", host_site_id="site:kek-tsukuba",
         intervals=[iv("active", "1994-04", "2010-06"), iv("completed", "2010-06", "2010-06")],
         institution_count=60, country_count=15, member_count=400, membership_history="unknown",
         leadership=[]),
    dict(id="collaboration:ua1", name="UA1 Collaboration", experiment_ids=["experiment:ua1"],
         formation="1978-01", host_facility_id="facility:cern", host_site_id="site:cern-sps-lss5",
         intervals=[iv("active", "1978-01", "1990-12"), iv("completed", "1990-12", "1990-12")],
         institution_count=13, country_count=7, member_count=135, membership_history="complete",
         leadership=[("spokesperson", "person:unresolved-ua1-cern-spokesperson", "A. Ferrante", "1978-01", "1990-12")]),
]

# --------------------------------------------------------------------------
# institutions:  (id, name, kind, lat, lon, country, city, region, ror, inspire)

INSTITUTIONS = [
    ("institution:cern", "CERN", "international_organization", 46.2339, 6.0553, "CH", "Meyrin", "Geneva", "01ggx4157", 902725),
    ("institution:fermilab", "Fermi National Accelerator Laboratory", "national_laboratory", 41.8319, -88.2569, "US", "Batavia", "Illinois", "020hgte69", 902796),
    ("institution:brookhaven-national-laboratory", "Brookhaven National Laboratory", "national_laboratory", 40.8700, -72.8800, "US", "Upton", "New York", "02ex6cf31", 902666),
    ("institution:lawrence-berkeley-national-laboratory", "Lawrence Berkeley National Laboratory", "national_laboratory", 37.8760, -122.2500, "US", "Berkeley", "California", "02jbv0t02", 902927),
    ("institution:university-of-iowa", "University of Iowa", "university", 41.6627, -91.5550, "US", "Iowa City", "Iowa", "036jqmy94", 903138),
    ("institution:colorado-state-university", "Colorado State University", "university", 40.5734, -105.0865, "US", "Fort Collins", "Colorado", "03k1gpj17", 902743),
    ("institution:south-dakota-mines", "South Dakota School of Mines and Technology", "university", 44.0750, -103.2070, "US", "Rapid City", "South Dakota", "012xbwn27", 903068),
    ("institution:university-of-south-dakota", "University of South Dakota", "university", 42.7890, -96.9250, "US", "Vermillion", "South Dakota", "02t0hqe23", 903223),
    ("institution:university-of-wisconsin-madison", "University of Wisconsin–Madison", "university", 43.0760, -89.4120, "US", "Madison", "Wisconsin", "01y2jtd41", 903255),
    ("institution:michigan-state-university", "Michigan State University", "university", 42.7010, -84.4820, "US", "East Lansing", "Michigan", "05hs6h993", 902971),
    ("institution:pennsylvania-state-university", "Pennsylvania State University", "university", 40.7980, -77.8600, "US", "University Park", "Pennsylvania", "04p491231", 903010),
    ("institution:drexel-university", "Drexel University", "university", 39.9560, -75.1890, "US", "Philadelphia", "Pennsylvania", "04bdffz58", 902776),
    ("institution:imperial-college-london", "Imperial College London", "university", 51.4988, -0.1749, "GB", "London", "England", "041kmwe10", 902870),
    ("institution:university-college-london", "University College London", "university", 51.5246, -0.1340, "GB", "London", "England", "02jx3x895", 903107),
    ("institution:university-of-manchester", "University of Manchester", "university", 53.4668, -2.2339, "GB", "Manchester", "England", "027m9bs27", 903170),
    ("institution:university-of-sheffield", "University of Sheffield", "university", 53.3811, -1.4879, "GB", "Sheffield", "England", "05krs5044", 903219),
    ("institution:university-of-sussex", "University of Sussex", "university", 50.8660, -0.0880, "GB", "Brighton", "England", "00ayhx656", 903230),
    ("institution:university-of-cambridge", "University of Cambridge", "university", 52.2050, 0.1180, "GB", "Cambridge", "England", "013meh722", 903108),
    ("institution:infn-milano", "INFN Sezione di Milano", "research_institute", 45.4760, 9.2300, "IT", "Milan", "Lombardy", "01tm6cn81", 902889),
    ("institution:university-of-bern", "University of Bern", "university", 46.9540, 7.4380, "CH", "Bern", "Bern", "02k7v4d05", 903112),
    ("institution:universite-paris-saclay", "Université Paris-Saclay", "university", 48.7100, 2.1670, "FR", "Orsay", "Essonne", "03xjwb503", 903018),
    ("institution:jagiellonian-university", "Jagiellonian University", "university", 50.0620, 19.9340, "PL", "Kraków", "Lesser Poland", "03bqmcz70", 902896),
    ("institution:stockholms-universitet", "Stockholm University", "university", 59.3660, 18.0570, "SE", "Stockholm", "Stockholm", "05f0yaq80", 903076),
    ("institution:ruhr-universitat-bochum", "Ruhr-Universität Bochum", "university", 51.4450, 7.2600, "DE", "Bochum", "North Rhine-Westphalia", "04tsk2644", 903031),
    ("institution:universidade-estadual-de-campinas", "Universidade Estadual de Campinas", "university", -22.8180, -47.0690, "BR", "Campinas", "São Paulo", "04wffgt70", 903097),
    ("institution:kek", "KEK", "national_laboratory", 36.1500, 140.0770, "JP", "Tsukuba", "Ibaraki", "01g5y5k24", 902916),
    ("institution:university-of-tokyo-icrr", "Institute for Cosmic Ray Research, University of Tokyo", "research_institute", 35.9020, 139.9350, "JP", "Kashiwa", "Chiba", "057zh3y96", 903237),
    ("institution:kyoto-university", "Kyoto University", "university", 35.0260, 135.7800, "JP", "Kyoto", "Kyoto", "02kpeqv85", 902924),
    ("institution:tsinghua-university", "Tsinghua University", "university", 40.0000, 116.3260, "CN", "Beijing", "Beijing", "03cve4549", 903091),
    ("institution:iit-hyderabad", "Indian Institute of Technology Hyderabad", "university", 17.5920, 78.1230, "IN", "Hyderabad", "Telangana", "01jf68f66", 902878),
    ("institution:university-of-melbourne", "University of Melbourne", "university", -37.7980, 144.9610, "AU", "Melbourne", "Victoria", "01ej9dk98", 903171),
]


# --------------------------------------------------------------------------
# memberships: (institution, start, end, known_since, known_until, evidence_class)

M = lambda i, s, e, ks, ku, c: dict(institution_id=i, start=s, end=e, known_since=ks,
                                    known_until=ku, evidence_class=c)

MEMBERSHIPS = {
    "collaboration:dune": [
        M("institution:fermilab", "2015-04", None, "2015-04", "2026-09", "official_institution_list"),
        M("institution:university-of-iowa", "2016-06", None, "2016-06", "2026-09", "official_institution_list"),
        M("institution:brookhaven-national-laboratory", "2015-04", None, "2015-04", "2026-09", "official_institution_list"),
        M("institution:lawrence-berkeley-national-laboratory", "2015-04", None, "2015-04", "2026-09", "official_institution_list"),
        M("institution:colorado-state-university", "2015-04", None, "2015-04", "2026-09", "official_roster"),
        M("institution:south-dakota-mines", "2015-04", None, "2015-04", "2026-09", "official_institution_list"),
        M("institution:university-of-south-dakota", "2015-04", None, "2015-04", "2026-09", "official_institution_list"),
        M("institution:imperial-college-london", "2015-04", None, "2015-04", "2026-09", "official_institution_list"),
        M("institution:university-of-manchester", "2015-04", None, "2015-04", "2026-09", "official_institution_list"),
        M("institution:university-of-sussex", None, None, "2019-03", "2026-09", "institutional_page"),
        M("institution:universidade-estadual-de-campinas", None, None, "2021-05", "2026-09", "publication_affiliation_current"),
        M("institution:university-of-bern", "2016-01", None, "2016-01", "2026-09", "official_institution_list"),
        M("institution:jagiellonian-university", None, None, None, None, "derived"),
        M("institution:iit-hyderabad", None, None, "2022-11", "2026-09", "inspire_author_profile"),
    ],
    "collaboration:atlas": [
        M("institution:cern", "1992-10", None, "1992-10", "2026-09", "official_roster"),
        M("institution:university-of-manchester", "1992-10", None, "1992-10", "2026-09", "official_roster"),
        M("institution:university-college-london", "1992-10", None, "1992-10", "2026-09", "official_roster"),
        M("institution:university-of-cambridge", "1993-05", None, "1993-05", "2026-09", "official_roster"),
        M("institution:infn-milano", "1992-10", None, "1992-10", "2026-09", "official_roster"),
        M("institution:universite-paris-saclay", "1994-01", None, "1994-01", "2026-09", "official_roster"),
        M("institution:michigan-state-university", "1994-01", None, "1994-01", "2026-09", "official_roster"),
        M("institution:stockholms-universitet", "1993-01", None, "1993-01", "2026-09", "official_roster"),
        M("institution:tsinghua-university", "2003-06", None, "2003-06", "2026-09", "official_roster"),
        M("institution:university-of-melbourne", None, None, "2015-07", "2026-09", "publication_affiliation_current"),
    ],
    "collaboration:cms": [
        M("institution:cern", "1992-10", None, "1992-10", "2026-09", "official_institution_list"),
        M("institution:fermilab", "1992-10", None, "1992-10", "2026-09", "official_institution_list"),
        M("institution:imperial-college-london", "1993-01", None, "1993-01", "2026-09", "official_institution_list"),
        M("institution:infn-milano", "1992-10", None, "1992-10", "2026-09", "official_institution_list"),
        M("institution:university-of-cambridge", None, None, "2010-02", "2026-09", "publication_affiliation_current"),
    ],
    "collaboration:icecube": [
        M("institution:university-of-wisconsin-madison", "1999-09", None, "1999-09", "2026-09", "official_roster"),
        M("institution:pennsylvania-state-university", "1999-09", None, "1999-09", "2026-09", "official_roster"),
        M("institution:michigan-state-university", "2005-01", None, "2005-01", "2026-09", "official_roster"),
        M("institution:drexel-university", "2001-06", None, "2001-06", "2026-09", "official_roster"),
        M("institution:stockholms-universitet", "1999-09", None, "1999-09", "2026-09", "official_roster"),
        M("institution:ruhr-universitat-bochum", "2000-01", None, "2000-01", "2026-09", "official_roster"),
        M("institution:university-of-melbourne", None, None, "2018-02", "2026-09", "institutional_page"),
        M("institution:university-of-bern", None, None, None, None, "derived"),
    ],
    "collaboration:t2k": [
        M("institution:university-of-tokyo-icrr", "2003-01", None, "2003-01", "2026-09", "official_institution_list"),
        M("institution:kek", "2003-01", None, "2003-01", "2026-09", "official_institution_list"),
        M("institution:kyoto-university", "2003-01", None, "2003-01", "2026-09", "official_institution_list"),
        M("institution:imperial-college-london", "2004-06", None, "2004-06", "2026-09", "official_institution_list"),
        M("institution:university-of-sheffield", "2005-01", None, "2005-01", "2026-09", "official_institution_list"),
        M("institution:universite-paris-saclay", "2005-01", None, "2005-01", "2026-09", "official_institution_list"),
        M("institution:university-of-bern", "2010-01", None, "2010-01", "2026-09", "official_institution_list"),
    ],
    "collaboration:super-kamiokande": [
        M("institution:university-of-tokyo-icrr", "1991-04", None, "1991-04", "2026-09", "official_institution_list"),
        M("institution:kek", "1991-04", None, "1991-04", "2026-09", "official_institution_list"),
        M("institution:kyoto-university", "1991-04", None, "1991-04", "2026-09", "official_institution_list"),
        M("institution:brookhaven-national-laboratory", "1991-04", None, "1991-04", "2026-09", "publication_affiliation_current"),
    ],
    "collaboration:lz": [
        M("institution:lawrence-berkeley-national-laboratory", "2012-07", None, "2012-07", "2026-09", "official_institution_list"),
        M("institution:south-dakota-mines", "2012-07", None, "2012-07", "2026-09", "official_institution_list"),
        M("institution:university-of-sheffield", "2012-07", None, "2012-07", "2026-09", "official_institution_list"),
        M("institution:imperial-college-london", "2012-07", None, "2012-07", "2026-09", "official_institution_list"),
        M("institution:university-college-london", "2012-07", None, "2012-07", "2026-09", "official_institution_list"),
        M("institution:university-of-wisconsin-madison", None, None, "2019-09", "2023-02", "publication_affiliation_historical"),
    ],
    "collaboration:belle-2": [
        M("institution:kek", "2008-11", None, "2008-11", "2026-09", "official_institution_list"),
        M("institution:university-of-tokyo-icrr", "2008-11", None, "2008-11", "2026-09", "official_institution_list"),
        M("institution:university-of-melbourne", "2009-03", None, "2009-03", "2026-09", "official_institution_list"),
        M("institution:jagiellonian-university", "2009-03", None, "2009-03", "2026-09", "official_institution_list"),
        M("institution:infn-milano", "2010-01", None, "2010-01", "2026-09", "official_institution_list"),
        M("institution:iit-hyderabad", None, None, "2017-04", "2026-09", "inspire_author_profile"),
    ],
    "collaboration:nova": [
        M("institution:fermilab", "2004-03", None, "2004-03", "2026-09", "official_institution_list"),
        M("institution:university-of-iowa", "2008-01", None, "2008-01", "2026-09", "official_institution_list"),
        M("institution:michigan-state-university", "2004-03", None, "2004-03", "2026-09", "official_institution_list"),
        M("institution:tsinghua-university", "2013-01", None, "2013-01", "2026-09", "official_institution_list"),
        M("institution:jagiellonian-university", "2012-01", None, "2012-01", "2026-09", "official_institution_list"),
    ],
    "collaboration:sbnd": [
        M("institution:fermilab", "2015-02", None, "2015-02", "2026-09", "official_institution_list"),
        M("institution:imperial-college-london", "2015-02", None, "2015-02", "2026-09", "official_institution_list"),
        M("institution:university-of-bern", "2015-02", None, "2015-02", "2026-09", "official_institution_list"),
        M("institution:universidade-estadual-de-campinas", "2016-01", None, "2016-01", "2026-09", "official_institution_list"),
    ],
    "collaboration:icarus": [
        M("institution:infn-milano", "1991-01", None, "1991-01", "2026-09", "official_institution_list"),
        M("institution:fermilab", "2015-01", None, "2015-01", "2026-09", "official_institution_list"),
        M("institution:university-of-bern", "2015-01", None, "2015-01", "2026-09", "official_institution_list"),
    ],
    "collaboration:belle": [
        M("institution:kek", "1994-04", "2010-06", "1994-04", "2010-06", "publication_affiliation_historical"),
        M("institution:university-of-melbourne", "1994-04", "2010-06", "1994-04", "2010-06", "publication_affiliation_historical"),
        M("institution:jagiellonian-university", "1999-01", "2010-06", "1999-01", "2010-06", "publication_affiliation_historical"),
    ],
    "collaboration:ua1": [
        M("institution:cern", "1978-01", "1990-12", "1978-01", "1990-12", "official_roster"),
        M("institution:imperial-college-london", "1978-01", "1990-12", "1978-01", "1990-12", "official_roster"),
        M("institution:infn-milano", "1978-01", "1990-12", "1978-01", "1990-12", "official_roster"),
        M("institution:universite-paris-saclay", "1978-01", "1990-12", "1978-01", "1990-12", "official_roster"),
        M("institution:ruhr-universitat-bochum", "1980-06", "1990-12", "1980-06", "1990-12", "official_roster"),
        M("institution:university-of-birmingham-fixture", None, None, None, None, "derived"),
    ],
}
# the last UA1 row points at an institution that is deliberately absent, to
# exercise "membership row whose institution lacks coordinates" (A12 warn).

COUNTED_CLASSES = {"official_roster", "official_institution_list", "inspire_author_profile",
                   "publication_affiliation_current", "institutional_page"}

EVIDENCE_WORDING = {
    "official_roster": "On the collaboration's own member list (as of {as_of})",
    "official_institution_list": "On the official institution list (as of {as_of})",
    "inspire_author_profile": "INSPIRE author profile lists this collaboration",
    "publication_affiliation_current": "Listed with this affiliation on a {collab} paper ({year}); current membership not confirmed",
    "publication_affiliation_historical": "Listed on a {collab} paper in {year}; may no longer be a member",
    "institutional_page": "The institution's own page states participation (checked {date})",
    "self_reported": "Self-reported",
    "derived": "Inferred, not verified",
}


# --------------------------------------------------------------------------
# people.  Every name here is invented; see the manifest banner.

ROLE_GROUP = {"faculty": "faculty_permanent", "staff_scientist": "faculty_permanent",
              "postdoc": "postdocs", "graduate_student": "students",
              "other_researcher": "unknown", "unknown": "unknown"}

P = lambda name, role, recid, start, ev: dict(name=name, role=role, recid=recid, start=start,
                                              evidence_class=ev)

PEOPLE = {
    ("collaboration:dune", "institution:university-of-iowa"): [
        P("Amara Whitfield", "faculty", 2417701, "2016-06", "official_roster"),
        P("Tobias Renner", "staff_scientist", 2417702, "2017-01", "official_roster"),
        P("Priya Raghunathan", "postdoc", 2417703, "2022-09", "official_roster"),
        P("Diego Salcedo", "postdoc", None, "2023-09", "institutional_page"),
        P("Hanne Vos", "graduate_student", None, "2021-08", "institutional_page"),
        P("Marcus Oyelaran", "graduate_student", None, "2023-08", "institutional_page"),
        P("Wen-Li Chao", "unknown", None, None, "publication_affiliation_current"),
    ],
    ("collaboration:dune", "institution:fermilab"): [
        P("Rosalind Okonjo", "staff_scientist", 2417710, "2015-04", "official_roster"),
        P("Étienne Baraka", "staff_scientist", 2417711, "2015-04", "official_roster"),
        P("Junko Maeda", "staff_scientist", None, "2018-03", "official_roster"),
        P("Peter Lindqvist", "postdoc", None, "2024-01", "official_roster"),
        P("Adaeze Nwosu", "graduate_student", None, "2022-08", "inspire_author_profile"),
    ],
    ("collaboration:dune", "institution:imperial-college-london"): [
        P("Helena Lindqvist", "faculty", 2417720, "2015-04", "official_roster"),
        P("Callum Thorne", "postdoc", None, "2023-10", "official_roster"),
        P("Sunita Bhatt", "graduate_student", None, "2022-10", "institutional_page"),
        P("Yusuf El-Amin", "graduate_student", None, "2024-10", "self_reported"),
    ],
    ("collaboration:dune", "institution:universidade-estadual-de-campinas"): [
        P("Beatriz Aparecida Rocha", "faculty", None, None, "publication_affiliation_current"),
        P("Tiago Fontenelle", "graduate_student", None, None, "publication_affiliation_current"),
    ],
    ("collaboration:atlas", "institution:cern"): [
        P("Marta Aubertin", "staff_scientist", 2417730, "1994-01", "official_roster"),
        P("Stefan Novotný", "staff_scientist", 2417731, "1998-06", "official_roster"),
        P("Ling Qiao", "postdoc", None, "2023-01", "official_roster"),
        P("Ana Belmonte", "graduate_student", None, "2024-01", "official_roster"),
    ],
    ("collaboration:atlas", "institution:university-of-manchester"): [
        P("Gareth Pritchard", "faculty", 2417740, "1993-01", "official_roster"),
        P("Iona Kerr", "postdoc", None, "2022-09", "official_roster"),
        P("Ravi Deshmukh", "graduate_student", None, "2023-09", "institutional_page"),
    ],
    ("collaboration:icecube", "institution:university-of-wisconsin-madison"): [
        P("Dara Arinze", "faculty", 2417750, "1999-09", "official_roster"),
        P("Nils Bergqvist", "staff_scientist", None, "2004-02", "official_roster"),
        P("Camille Trudeau", "postdoc", None, "2023-06", "official_roster"),
        P("Oskar Lindgren", "graduate_student", None, "2022-09", "official_roster"),
        P("Mei-Ling Sørensen", "graduate_student", None, "2024-09", "institutional_page"),
    ],
    ("collaboration:lz", "institution:imperial-college-london"): [
        P("Nadia Farouk", "faculty", 2417760, "2012-07", "official_roster"),
        P("Bram de Vries", "postdoc", None, "2021-11", "official_roster"),
    ],
    ("collaboration:ua1", "institution:cern"): [
        P("Alessandro Ferrante", "staff_scientist", None, "1978-01", "publication_affiliation_historical"),
        P("Margit Hollander", "staff_scientist", None, "1979-04", "publication_affiliation_historical"),
        P("Jean-Luc Perrin", "other_researcher", None, "1981-01", "publication_affiliation_historical"),
    ],
}

PEOPLE_UNKNOWN = {
    "collaboration:dune": [
        P("Chidi Umeh", "unknown", None, None, "publication_affiliation_current"),
        P("L. Moreau", "unknown", None, None, "publication_affiliation_historical"),
    ],
}

# --------------------------------------------------------------------------
# results

RESULTS = [
    dict(id="result:higgs-boson-observation-2012", title="Observation of a new particle in the search for the Standard Model Higgs boson",
         date="2012-07-04", date_kind="announcement", result_type="observation",
         experiment_ids=["experiment:atlas", "experiment:cms"], collaboration_ids=["collaboration:atlas", "collaboration:cms"],
         facility_ids=["facility:cern"], detector_ids=["detector:atlas", "detector:cms"],
         topic_ids=["topic:higgs-boson", "topic:electroweak-symmetry-breaking"],
         key_value=q(125.4, "GeV/c^2", "125.4 GeV/c²", "mass_energy"), key_value_text="",
         significance="5.9σ local (ATLAS)",
         claim=("We observe an excess of events at m_H ≈ 126.5 GeV with a local significance of 5.9 standard deviations.",
                "abstract", ["src:atlas-higgs-2012"]),
         publication={"arxiv": "1207.7214", "doi": "10.1016/j.physletb.2012.08.020", "inspire": 1124337},
         official_url="https://atlas.cern/updates/briefing/higgs-boson-discovery",
         hepdata="https://www.hepdata.net/record/ins1124337"),
    dict(id="result:w-and-z-boson-discovery-1983", title="Experimental observation of isolated large transverse energy electrons with associated missing energy at √s = 540 GeV",
         date="1983-01-25", date_kind="publication", result_type="discovery",
         experiment_ids=["experiment:ua1"], collaboration_ids=["collaboration:ua1"],
         facility_ids=["facility:cern"], detector_ids=["detector:ua1"],
         topic_ids=["topic:electroweak-symmetry-breaking"],
         key_value=q(81, "GeV/c^2", "81 ± 5 GeV/c²", "mass_energy"), key_value_text="",
         significance="6 events over a background of 0.6",
         claim=("The events are consistent with the discovery of the intermediate vector boson W.",
                "abstract", ["src:ua1-w-1983"]),
         publication={"doi": "10.1016/0370-2693(83)91177-2", "inspire": 188630},
         # official_url deliberately restates the DOI above (task A4):
         # exercises official_url_kind == "doi".
         official_url="https://doi.org/10.1016/0370-2693(83)91177-2", hepdata=None),
    dict(id="result:super-k-atmospheric-oscillation-1998", title="Evidence for oscillation of atmospheric neutrinos",
         date="1998-06-05", date_kind="preprint", result_type="evidence",
         experiment_ids=["experiment:super-kamiokande"], collaboration_ids=["collaboration:super-kamiokande"],
         facility_ids=["facility:kamioka-observatory"], detector_ids=["detector:super-kamiokande"],
         topic_ids=["topic:neutrino-oscillations", "topic:neutrino-physics"],
         key_value=q(2.2e-3, "eV^2", "Δm² ≈ 2.2 × 10⁻³ eV²", "mass_energy"), key_value_text="",
         significance="6.2σ zenith-angle asymmetry",
         claim=("We present an analysis of these data which gives evidence for oscillation of atmospheric neutrinos.",
                "abstract", ["src:superk-atmospheric-1998"]),
         publication={"arxiv": "hep-ex/9807003", "doi": "10.1103/PhysRevLett.81.1562", "inspire": 471304},
         # official_url deliberately restates the arXiv link above (task A4):
         # exercises official_url_kind == "arxiv" so the panel shows one
         # arXiv link instead of a redundant second "Official page".
         official_url="https://arxiv.org/abs/hep-ex/9807003", hepdata=None),
    dict(id="result:t2k-electron-neutrino-appearance-2013", title="Observation of electron neutrino appearance in a muon neutrino beam",
         date="2013-07-19", date_kind="preprint", result_type="observation",
         experiment_ids=["experiment:t2k"], collaboration_ids=["collaboration:t2k"],
         facility_ids=["facility:j-parc", "facility:kamioka-observatory"],
         detector_ids=["detector:nd280", "detector:super-kamiokande"],
         topic_ids=["topic:neutrino-oscillations", "topic:leptonic-cp-violation"],
         key_value=q(0.14, "", "sin²2θ₁₃ = 0.140", "fraction"), key_value_text="",
         significance="7.3σ",
         claim=("The observed value of 28 candidate events excludes the no-appearance hypothesis at 7.3 standard deviations.",
                "abstract", ["src:t2k-appearance-2013"]),
         publication={"arxiv": "1311.4750", "doi": "10.1103/PhysRevLett.112.061802", "inspire": 1265307},
         official_url="https://t2k-experiment.org/result/", hepdata=None),
    dict(id="result:icecube-astrophysical-neutrinos-2013", title="Evidence for high-energy extraterrestrial neutrinos in the IceCube detector",
         date="2013-11-22", date_kind="publication", result_type="evidence",
         experiment_ids=["experiment:icecube"], collaboration_ids=["collaboration:icecube"],
         facility_ids=["facility:amundsen-scott"], detector_ids=["detector:icecube-in-ice"],
         topic_ids=["topic:neutrino-astronomy"],
         key_value=None, key_value_text="28 events between 30 TeV and 1.2 PeV",
         significance="4.1σ against an atmospheric-only origin",
         claim=("These data provide evidence for high-energy extraterrestrial neutrinos at the 4σ level.",
                "abstract", ["src:icecube-hese-2013"]),
         publication={"arxiv": "1311.5238", "doi": "10.1126/science.1242856", "inspire": 1265125},
         official_url="https://icecube.wisc.edu/science/highlights/", hepdata=None),
    dict(id="result:icecube-txs-0506-056-2018", title="Neutrino emission from the direction of the blazar TXS 0506+056",
         date="2018-07-12", date_kind="publication", result_type="evidence",
         experiment_ids=["experiment:icecube"], collaboration_ids=["collaboration:icecube"],
         facility_ids=["facility:amundsen-scott"], detector_ids=["detector:icecube-in-ice"],
         topic_ids=["topic:neutrino-astronomy"],
         key_value=None, key_value_text="290 TeV alert neutrino coincident with a γ-ray flare",
         significance="3σ",
         claim=("We find evidence for neutrino emission from the direction of TXS 0506+056 at the 3σ level.",
                "abstract", ["src:icecube-txs-2018"]),
         publication={"doi": "10.1126/science.aat2890", "inspire": 1679243},
         official_url="https://icecube.wisc.edu/news/press-releases/2018/07/", hepdata=None),
    dict(id="result:nova-electron-neutrino-appearance-2016", title="First measurement of electron neutrino appearance in NOvA",
         date="2016-04-19", date_kind="publication", result_type="measurement",
         experiment_ids=["experiment:nova"], collaboration_ids=["collaboration:nova"],
         facility_ids=["facility:fermilab"], detector_ids=["detector:nova-fd", "detector:nova-nd"],
         topic_ids=["topic:neutrino-oscillations", "topic:mass-ordering"],
         key_value=None, key_value_text="33 ν_e candidates on a background of 8.2",
         significance="8.4σ",
         claim=("We report the first measurement of ν_e appearance in the NOvA experiment.",
                "abstract", ["src:nova-appearance-2016"]),
         publication={"arxiv": "1601.05022", "doi": "10.1103/PhysRevLett.116.151806", "inspire": 1416342},
         official_url="https://novaexperiment.fnal.gov/results/", hepdata=None),
    dict(id="result:lz-wimp-limit-2024", title="Dark matter search results from 4.2 tonne-years of exposure of the LUX-ZEPLIN experiment",
         date="2024-08-26", date_kind="preprint", result_type="limit",
         experiment_ids=["experiment:lz"], collaboration_ids=["collaboration:lz"],
         facility_ids=["facility:surf"], detector_ids=["detector:lz"],
         topic_ids=["topic:wimp-direct-detection", "topic:dark-matter"],
         key_value=q(2.2e-48, "cm^2", "2.2 × 10⁻⁴⁸ cm² at 40 GeV/c²", "cross_section"), key_value_text="",
         significance="90 % confidence upper limit",
         claim=("We set an upper limit on the spin-independent WIMP–nucleon cross section of 2.2 × 10⁻⁴⁸ cm² at 40 GeV/c².",
                "abstract", ["src:lz-limit-2024"]),
         publication={"arxiv": "2410.17036", "inspire": 2832321},
         official_url="https://lz.lbl.gov/results/", hepdata=None),
    dict(id="result:belle-2-first-collisions-2018", title="First electron–positron collisions recorded by Belle II",
         date="2018-04-26", date_kind="announcement", result_type="technology_milestone",
         experiment_ids=["experiment:belle-2"], collaboration_ids=["collaboration:belle-2"],
         facility_ids=["facility:kek"], detector_ids=["detector:belle-2"],
         topic_ids=["topic:b-meson-decays"],
         key_value=None, key_value_text="first recorded e⁺e⁻ collisions at SuperKEKB",
         significance="",
         claim=("SuperKEKB delivered the first electron–positron collisions to the Belle II detector.",
                "news item", ["src:belle2-first-collisions-2018"]),
         publication={"url": "https://www.belle2.org/"},
         official_url="https://www.belle2.org/", hepdata=None),
    dict(id="result:protodune-beam-test-2018", title="ProtoDUNE single-phase records its first particle tracks in a test beam",
         date="2018-09-19", date_kind="announcement", result_type="technology_milestone",
         experiment_ids=["experiment:dune"], collaboration_ids=["collaboration:dune"],
         facility_ids=["facility:cern"], detector_ids=[],
         topic_ids=["topic:neutrino-oscillations"],
         key_value=q(770, "t", "770 t liquid argon prototype", "mass"), key_value_text="",
         significance="",
         claim=("The ProtoDUNE single-phase detector recorded its first particle tracks from the CERN test beam.",
                "news item", ["src:protodune-2018"]),
         publication={"url": "https://home.cern/news/news/experiments/protodune-first-tracks"},
         official_url="https://home.cern/news/news/experiments/protodune-first-tracks", hepdata=None),
    dict(id="result:super-k-gadolinium-loading-2020", title="Super-Kamiokande begins gadolinium-loaded running",
         date="2020-08-14", date_kind="announcement", result_type="technology_milestone",
         experiment_ids=["experiment:super-kamiokande"], collaboration_ids=["collaboration:super-kamiokande"],
         facility_ids=["facility:kamioka-observatory"], detector_ids=["detector:super-kamiokande"],
         topic_ids=["topic:neutrino-astronomy"],
         key_value=None, key_value_text="13 t of Gd₂(SO₄)₃ dissolved in the tank",
         significance="",
         claim=("Gadolinium sulphate was dissolved into the Super-Kamiokande tank to enable neutron tagging.",
                "news item", ["src:superk-gd-2020"]),
         publication={"url": "https://www-sk.icrr.u-tokyo.ac.jp/en/sk/"},
         official_url="https://www-sk.icrr.u-tokyo.ac.jp/en/sk/", hepdata=None),
]


# --------------------------------------------------------------------------
# documents

DOCUMENTS = [
    dict(id="document:dune-tdr-2020", title="Deep Underground Neutrino Experiment (DUNE) Far Detector Technical Design Report",
         doc_type="technical_design_report", date="2020-02-17", owner_ids=["experiment:dune", "collaboration:dune"],
         url="https://arxiv.org/abs/2002.03005", arxiv="2002.03005", report_number="FERMILAB-DESIGN-2020-01",
         volumes=[("Volume I: Introduction to DUNE", "https://arxiv.org/abs/2002.02967"),
                  ("Volume II: DUNE Physics", "https://arxiv.org/abs/2002.03005"),
                  ("Volume III: DUNE Far Detector Technical Coordination", "https://arxiv.org/abs/2002.03008"),
                  ("Volume IV: Far Detector Single-phase Technology", "https://arxiv.org/abs/2002.03010")]),
    dict(id="document:dune-cdr-2015", title="The Long-Baseline Neutrino Facility and DUNE Conceptual Design Report",
         doc_type="conceptual_design_report", date="2015-12-22", owner_ids=["experiment:dune", "beamline:lbnf"],
         url="https://arxiv.org/abs/1601.05471", arxiv="1601.05471", report_number="FERMILAB-DESIGN-2016-01", volumes=[]),
    dict(id="document:atlas-detector-paper-2008", title="The ATLAS Experiment at the CERN Large Hadron Collider",
         doc_type="detector_paper", date="2008-08-14", owner_ids=["experiment:atlas", "detector:atlas"],
         url="https://doi.org/10.1088/1748-0221/3/08/S08003", doi="10.1088/1748-0221/3/08/S08003", volumes=[]),
    dict(id="document:cms-detector-paper-2008", title="The CMS Experiment at the CERN LHC",
         doc_type="detector_paper", date="2008-08-14", owner_ids=["experiment:cms", "detector:cms"],
         url="https://doi.org/10.1088/1748-0221/3/08/S08004", doi="10.1088/1748-0221/3/08/S08004", volumes=[]),
    dict(id="document:icecube-instrumentation-2017", title="The IceCube Neutrino Observatory: Instrumentation and Online Systems",
         doc_type="detector_paper", date="2017-03-29", owner_ids=["experiment:icecube", "detector:icecube-in-ice"],
         url="https://arxiv.org/abs/1612.05093", arxiv="1612.05093", volumes=[]),
    dict(id="document:lz-tdr-2017", title="LUX-ZEPLIN (LZ) Technical Design Report",
         doc_type="technical_design_report", date="2017-03-30", owner_ids=["experiment:lz", "detector:lz"],
         url="https://arxiv.org/abs/1703.09144", arxiv="1703.09144", report_number="LBNL-1007256", volumes=[]),
    dict(id="document:t2k-experiment-2011", title="The T2K Experiment",
         doc_type="detector_paper", date="2011-06-07", owner_ids=["experiment:t2k", "beamline:jparc-neutrino"],
         url="https://arxiv.org/abs/1106.1238", arxiv="1106.1238", volumes=[]),
    dict(id="document:nova-tdr-2007", title="The NOvA Technical Design Report",
         doc_type="technical_design_report", date="2007-10-08", owner_ids=["experiment:nova"],
         url="https://doi.org/10.2172/935497", doi="10.2172/935497", report_number="FERMILAB-DESIGN-2007-01", volumes=[]),
    dict(id="document:belle2-tdr-2010", title="Belle II Technical Design Report",
         doc_type="technical_design_report", date="2010-11-01", owner_ids=["experiment:belle-2", "detector:belle-2"],
         url="https://arxiv.org/abs/1011.0352", arxiv="1011.0352", report_number="KEK-REPORT-2010-1", volumes=[]),
    dict(id="document:super-kamiokande-detector-2003", title="The Super-Kamiokande detector",
         doc_type="detector_paper", date="2003-04-11", owner_ids=["experiment:super-kamiokande", "detector:super-kamiokande"],
         url="https://doi.org/10.1016/S0168-9002(03)00425-X", doi="10.1016/S0168-9002(03)00425-X", volumes=[]),
    dict(id="document:lhc-design-report-2004", title="LHC Design Report",
         doc_type="design_report", date="2004-06-01", owner_ids=["accelerator:lhc", "facility:cern"],
         url="https://doi.org/10.5170/CERN-2004-003-V-1", doi="10.5170/CERN-2004-003-V-1",
         report_number="CERN-2004-003", volumes=[("Volume I: The LHC Main Ring", "https://doi.org/10.5170/CERN-2004-003-V-1")]),
    dict(id="document:ua1-proposal-1978", title="A 4π solid-angle detector for the SPS used as a proton–antiproton collider at a centre-of-mass energy of 540 GeV",
         doc_type="technical_proposal", date="1978-01-11", owner_ids=["experiment:ua1", "detector:ua1"],
         url="https://cds.cern.ch/record/319371", report_number="CERN-SPSC-78-06", volumes=[]),
]

# --------------------------------------------------------------------------
# sources: (id, title, source_type, url, publisher_id, accessed)

SOURCES = [
    ("src:cern-about", "About CERN", "official_facility_site", "https://home.cern/about", "institution:cern", "2026-09-10"),
    ("src:fermilab-about", "About Fermilab", "official_facility_site", "https://www.fnal.gov/pub/about/index.html", "institution:fermilab", "2026-09-10"),
    ("src:osm-demo-extract", "OpenStreetMap extract, Fermilab campus (development fixture stand-in)", "openstreetmap", "https://www.openstreetmap.org/relation/0000001", None, "2026-09-16"),
    ("src:surf-about", "About SURF", "official_facility_site", "https://sanfordlab.org/about", None, "2026-09-10"),
    ("src:jparc-about", "About J-PARC", "official_facility_site", "https://j-parc.jp/c/en/about/index.html", None, "2026-09-10"),
    ("src:kamioka-about", "Kamioka Observatory", "official_facility_site", "https://www-sk.icrr.u-tokyo.ac.jp/en/", "institution:university-of-tokyo-icrr", "2026-09-10"),
    ("src:kek-about", "About KEK", "official_facility_site", "https://www.kek.jp/en/about/", "institution:kek", "2026-09-10"),
    ("src:nsf-south-pole", "Amundsen–Scott South Pole Station", "official_facility_site", "https://www.nsf.gov/geo/opp/support/southp.jsp", None, "2026-09-10"),
    ("src:dune-tdr-vol2", "DUNE Far Detector TDR Volume II: DUNE Physics", "design_report", "https://arxiv.org/abs/2002.03005", "collaboration:dune", "2026-09-11"),
    ("src:dune-institutions", "DUNE collaboration institutions", "official_experiment_site", "https://www.dunescience.org/collaboration-institutions/", "collaboration:dune", "2026-09-12"),
    ("src:atlas-collaboration", "The ATLAS Collaboration", "official_experiment_site", "https://atlas.cern/Discover/Collaboration", "collaboration:atlas", "2026-09-12"),
    ("src:icecube-collaboration", "IceCube Collaboration institutions", "official_experiment_site", "https://icecube.wisc.edu/collaboration/institutions/", "collaboration:icecube", "2026-09-12"),
    ("src:t2k-collaboration", "T2K collaborating institutes", "official_experiment_site", "https://t2k-experiment.org/t2k/collaboration/", "collaboration:t2k", "2026-09-12"),
    ("src:lz-collaboration", "LZ Collaboration", "official_experiment_site", "https://lz.lbl.gov/collaboration/", "collaboration:lz", "2026-09-12"),
    ("src:belle2-collaboration", "Belle II Collaboration members", "official_experiment_site", "https://www.belle2.org/collaboration/", "collaboration:belle-2", "2026-09-12"),
    ("src:nova-collaboration", "NOvA collaborating institutions", "official_experiment_site", "https://novaexperiment.fnal.gov/collaboration/", "collaboration:nova", "2026-09-12"),
    ("src:superk-collaboration", "Super-Kamiokande Collaboration", "official_experiment_site", "https://www-sk.icrr.u-tokyo.ac.jp/en/sk/collaboration/", "collaboration:super-kamiokande", "2026-09-12"),
    ("src:greybook-dune", "INSPIRE experiment record: FNAL-E-1062 (DUNE)", "experiment_registry", "https://inspirehep.net/experiments/1346843", None, "2026-09-11"),
    ("src:greybook-atlas", "INSPIRE experiment record: CERN-LHC-ATLAS", "experiment_registry", "https://inspirehep.net/experiments/1108541", None, "2026-09-11"),
    ("src:atlas-higgs-2012", "Observation of a new particle in the search for the Standard Model Higgs boson with the ATLAS detector", "arxiv", "https://arxiv.org/abs/1207.7214", "collaboration:atlas", "2026-09-11"),
    ("src:ua1-w-1983", "Experimental observation of isolated large transverse energy electrons …", "journal_article", "https://doi.org/10.1016/0370-2693(83)91177-2", "collaboration:ua1", "2026-09-11"),
    ("src:superk-atmospheric-1998", "Evidence for oscillation of atmospheric neutrinos", "arxiv", "https://arxiv.org/abs/hep-ex/9807003", "collaboration:super-kamiokande", "2026-09-11"),
    ("src:t2k-appearance-2013", "Observation of electron neutrino appearance in a muon neutrino beam", "arxiv", "https://arxiv.org/abs/1311.4750", "collaboration:t2k", "2026-09-11"),
    ("src:icecube-hese-2013", "Evidence for high-energy extraterrestrial neutrinos in the IceCube detector", "journal_article", "https://doi.org/10.1126/science.1242856", "collaboration:icecube", "2026-09-11"),
    ("src:icecube-txs-2018", "Neutrino emission from the direction of the blazar TXS 0506+056", "journal_article", "https://doi.org/10.1126/science.aat2890", "collaboration:icecube", "2026-09-11"),
    ("src:nova-appearance-2016", "First measurement of electron neutrino appearance in NOvA", "arxiv", "https://arxiv.org/abs/1601.05022", "collaboration:nova", "2026-09-11"),
    ("src:lz-limit-2024", "Dark matter search results from 4.2 tonne-years of exposure of LZ", "arxiv", "https://arxiv.org/abs/2410.17036", "collaboration:lz", "2026-09-11"),
    ("src:belle2-first-collisions-2018", "Belle II records first collisions", "press_release", "https://www.belle2.org/", "collaboration:belle-2", "2026-09-11"),
    ("src:protodune-2018", "ProtoDUNE's first tracks", "press_release", "https://home.cern/news/news/experiments/protodune-first-tracks", "institution:cern", "2026-09-11"),
    ("src:superk-gd-2020", "Super-Kamiokande gadolinium loading", "press_release", "https://www-sk.icrr.u-tokyo.ac.jp/en/sk/", "collaboration:super-kamiokande", "2026-09-11"),
    ("src:lbnf-beamline-cdr", "LBNF beamline conceptual design", "design_report", "https://arxiv.org/abs/1601.05471", "collaboration:dune", "2026-09-11"),
    ("src:ror-registry", "Research Organization Registry", "wikidata", "https://ror.org/", None, "2026-09-09"),
]

SOURCE_RANK = {"official_experiment_site": 1, "official_facility_site": 2, "experiment_registry": 3,
               "inspire_experiment_record": 3, "design_report": 4, "detector_paper": 5, "hepdata": 6,
               "pdg": 7, "institution_page": 8, "geocoder": 8, "result_page": 9, "press_release": 9,
               "project_document": 9, "journal_article": 10, "arxiv": 10,
               "inspire_literature_record": 10, "openstreetmap": 11,
               "wikipedia": 12, "wikidata": 12, "secondary": 12}


# --------------------------------------------------------------------------
# long text (text.json)

SUMMARIES = {
 "facility:cern": ("The world's largest particle physics laboratory, straddling the Swiss–French border outside Geneva. Its accelerator complex ends in the 27 km Large Hadron Collider.",
   "Founded in 1954 by twelve European states. The injector chain (Linac 4 → PSB → PS → SPS) feeds the LHC at 450 GeV; the SPS also serves the North Area fixed-target programme and, from 1981 to 1990, ran as the SppS proton–antiproton collider."),
 "facility:fermilab": ("The United States' dedicated particle physics laboratory, west of Chicago, and the host of the country's long-baseline neutrino programme.",
   "The Main Injector delivers 120 GeV protons to the NuMI and (from the 2030s) LBNF targets; the 8 GeV Booster feeds the Short-Baseline Neutrino programme. The Tevatron ran here from 1983 until 2011."),
 "facility:surf": ("A laboratory 1478 m underground in a former gold mine in Lead, South Dakota, where the rock above shields detectors from cosmic rays.",
   "4300 m.w.e. of overburden at the 4850 ft level. The Davis Campus hosts LZ and MAJORANA; new caverns excavated from 2021 will hold the DUNE far detector modules."),
 "facility:j-parc": ("A proton accelerator complex on the Pacific coast at Tokai, Japan, whose neutrino beam is aimed 295 km across the country at Super-Kamiokande.",
   "The 30 GeV Main Ring delivers up to 760 kW to the neutrino target station; the beam is produced 2.5° off the axis to Kamioka, narrowing its energy spectrum around the oscillation maximum."),
 "facility:kamioka-observatory": ("A cluster of experiments inside the Mozumi mine under Mount Ikeno, Japan — the home of Super-Kamiokande.",
   "Roughly 1000 m of rock (2700 m.w.e.) above the Super-Kamiokande cavern. The site also hosts KamLAND, XMASS and the KAGRA gravitational-wave interferometer."),
 "facility:amundsen-scott": ("The United States research station at the geographic South Pole, above the cubic kilometre of ice instrumented by IceCube.",
   "Continuously occupied since 1956, at 2835 m elevation on the polar plateau. The ice below is exceptionally clear and free of radioactivity, which is what makes it a detector."),
 "facility:kek": ("Japan's high energy accelerator laboratory in Tsukuba, home of the SuperKEKB electron–positron collider.",
   "SuperKEKB collides 7 GeV electrons with 4 GeV positrons at the Υ(4S) resonance, with a nano-beam scheme designed for 40 times KEKB's peak luminosity."),
 "experiment:atlas": ("One of the two general-purpose detectors at the LHC. It recorded the collisions in which the Higgs boson was found in 2012.",
   "A 46 m long, 7000 t detector built around a 2 T solenoid and an air-core toroid muon spectrometer, reading out roughly 100 million channels at a 40 MHz bunch-crossing rate."),
 "experiment:cms": ("The LHC's other general-purpose detector — an independent instrument built so that a discovery has to be seen twice.",
   "Compact and heavy: 14 000 t inside a 3.8 T superconducting solenoid, with an all-silicon tracker and a lead-tungstate crystal electromagnetic calorimeter."),
 "experiment:dune": ("A neutrino beam fired 1285 km through the Earth from Illinois to a 40 kt liquid-argon detector under South Dakota, to find out whether neutrinos and antineutrinos behave differently.",
   "Four 17.5 kt liquid argon TPC modules at the 4850 ft level of SURF, exposed to a 1.2 MW wide-band beam from the Fermilab Main Injector, with a movable near detector complex on the Fermilab site."),
 "experiment:nova": ("Two liquid-scintillator detectors 810 km apart, off the axis of Fermilab's NuMI beam, measuring how muon neutrinos turn into electron neutrinos.",
   "The 14 kt far detector at Ash River sits 14.6 mrad off the beam axis, which narrows the spectrum to about 2 GeV — close to the first oscillation maximum at this baseline."),
 "experiment:sbnd": ("The near detector of Fermilab's short-baseline programme, 110 m from the Booster neutrino target.",
   "A 112 t active-mass liquid argon TPC that measures the unoscillated beam so that ICARUS, 600 m downstream, can be searched for a sterile-neutrino signal."),
 "experiment:icarus": ("A liquid argon detector first run under the Gran Sasso mountain, rebuilt at CERN and now the far detector of Fermilab's short-baseline programme.",
   "476 t of active liquid argon in two cryostats, searching for the excess of electron-neutrino-like events reported by LSND and MiniBooNE."),
 "experiment:t2k": ("A neutrino beam sent 295 km under Japan from Tokai to the Super-Kamiokande detector; the first experiment to see muon neutrinos turning into electron neutrinos.",
   "A 2.5° off-axis 0.6 GeV beam from the J-PARC Main Ring, with the magnetised ND280 near detector 280 m downstream and the 50 kt Super-Kamiokande water Cherenkov detector as the far detector."),
 "experiment:super-kamiokande": ("A 50 000 t tank of ultrapure water a kilometre inside a Japanese mine, watched by eleven thousand photomultipliers. In 1998 it showed that neutrinos have mass.",
   "The inner detector holds 32 kt viewed by 11 129 50 cm PMTs; an outer veto shell rejects entering muons. Since 2020 the water has been loaded with gadolinium to tag neutrons."),
 "experiment:icecube": ("A cubic kilometre of Antarctic ice turned into a telescope, which found the first neutrinos arriving from outside our galaxy.",
   "5160 digital optical modules on 86 strings between 1450 m and 2450 m depth, with the denser DeepCore infill extending sensitivity down to about 10 GeV."),
 "experiment:lz": ("Seven tonnes of liquid xenon a mile underground, waiting for a dark matter particle to bump into a xenon nucleus.",
   "A dual-phase xenon TPC with a 5.5 t fiducial mass, surrounded by a gadolinium-loaded liquid scintillator outer detector and a water tank, at the SURF Davis Campus."),
 "experiment:belle-2": ("An electron–positron collider experiment in Japan studying rare decays of B mesons, where a deviation from prediction would point to new particles too heavy to make directly.",
   "A hermetic detector at SuperKEKB's interaction region, aiming at 50 ab⁻¹ — fifty times the Belle dataset — with a DEPFET pixel vertex detector 1.4 cm from the beam."),
 "experiment:belle": ("The predecessor of Belle II at the KEKB collider, which shared the 2008 Nobel Prize's experimental confirmation of CP violation in B decays.",
   "Ran from 1999 to 2010 and accumulated 1041 fb⁻¹, establishing CP violation in the B meson system alongside BaBar."),
 "experiment:ua1": ("The CERN experiment that discovered the W and Z bosons in 1983 by watching protons and antiprotons annihilate inside the SPS.",
   "A 2000 t dipole-magnet detector in an underground area of the SPS, with a 6 m central drift chamber and near-hermetic calorimetry — the first collider detector designed around missing transverse energy."),
 "topic:neutrino-oscillations": ("Neutrinos are produced as one of three types and arrive as another. That is only possible if they have mass — which the Standard Model said they did not.", ""),
 "topic:leptonic-cp-violation": ("If neutrinos oscillate at a different rate from antineutrinos, the early universe had a way to end up with more matter than antimatter.", ""),
 "topic:wimp-direct-detection": ("Dark matter outweighs ordinary matter five to one. Direct-detection experiments wait, underground and very quietly, for one particle of it to hit a nucleus.", ""),
 "topic:higgs-boson": ("The Higgs field gives mass to the W, the Z and every fermion. Measuring its couplings is how we test whether the mechanism is exactly the one the Standard Model wrote down.", ""),
 "topic:neutrino-astronomy": ("Neutrinos travel from the far universe in a straight line through everything. They point back at whatever accelerated them.", ""),
}

WHY_IT_MATTERS = {
 "result:higgs-boson-observation-2012": "It completed the Standard Model's particle content and confirmed that the mechanism giving mass to the W and Z is a physical field with a quantum.",
 "result:w-and-z-boson-discovery-1983": "The W and Z are the carriers of the weak force. Finding them at the predicted masses confirmed the unification of the weak and electromagnetic interactions.",
 "result:super-k-atmospheric-oscillation-1998": "It was the first solid evidence that neutrinos have mass — the first laboratory result the Standard Model could not accommodate.",
 "result:t2k-electron-neutrino-appearance-2013": "Appearance of a neutrino flavour that was not in the beam opened the door to comparing neutrinos with antineutrinos, which is how leptonic CP violation will be measured.",
 "result:icecube-astrophysical-neutrinos-2013": "It opened neutrino astronomy above a TeV: the universe has sources violent enough to send us particles that ignore everything in between.",
 "result:icecube-txs-0506-056-2018": "It tied a single high-energy neutrino to a flaring blazar, the first identification of a source of cosmic-ray acceleration outside the galaxy.",
 "result:lz-wimp-limit-2024": "Each order of magnitude of cross-section excluded closes off a large region of well-motivated dark-matter parameter space.",
}


# --------------------------------------------------------------------------
# build

def write(path: Path, payload) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    path.write_text(body, encoding="utf-8")
    return len(body.encode("utf-8"))


# --------------------------------------------------------------------------
# local-map geometry (docs/HEP_ATLAS_GEOMETRY.md §1–§3)
#
# One demo map, for the fixture's Fermilab campus, emitted in exactly the §3
# build shape: `maps` in atlas.json, `geometry/<slug>.json` as the lazy
# bundle, derived `map_id` / `geometry_map_ids` back-references, and a `map`
# search entry. The *shapes* here are synthetic — plausible sizes and
# relationships at the real campus coordinates, not traced from OpenStreetMap
# and not surveyed — so that the browser's map view can be developed and
# tested before the real geometry records land. Every record therefore
# carries that warning in `map.notes`, and the licence/attribution fields
# exercise the ODbL path the real OSM-derived records will use.

MAP_SPHERE_R = 6371008.8  # WGS 84 mean radius, as schema.great_circle_m uses


def _dest(lat, lon, bearing_deg, dist_m):
    """Point `dist_m` from (lat, lon) along an initial great-circle bearing."""
    p1 = math.radians(lat)
    l1 = math.radians(lon)
    th = math.radians(bearing_deg)
    d = dist_m / MAP_SPHERE_R
    p2 = math.asin(math.sin(p1) * math.cos(d) + math.cos(p1) * math.sin(d) * math.cos(th))
    l2 = l1 + math.atan2(math.sin(th) * math.sin(d) * math.cos(p1),
                         math.cos(d) - math.sin(p1) * math.sin(p2))
    return (math.degrees(p2), (math.degrees(l2) + 540) % 360 - 180)


def _gc_m(a, b):
    """Great-circle metres between two (lat, lon) pairs."""
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp = p2 - p1
    dl = math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * MAP_SPHERE_R * math.asin(min(1.0, math.sqrt(h)))


def _bearing(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dl = math.radians(b[1] - a[1])
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _ll(coords):
    """[lon, lat] positions -> (lat, lon) pairs."""
    return [(c[1], c[0]) for c in coords]


def _line_length_m(coords):
    pts = _ll(coords)
    return sum(_gc_m(pts[i], pts[i + 1]) for i in range(len(pts) - 1))


def _ring_area_m2(coords):
    """Spherical excess (schema.polygon_area_m2) for one closed ring."""
    total = 0.0
    n = len(coords) - 1
    for i in range(n):
        lon1, lat1 = math.radians(coords[i][0]), math.radians(coords[i][1])
        lon2, lat2 = math.radians(coords[i + 1][0]), math.radians(coords[i + 1][1])
        total += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))
    return abs(total * MAP_SPHERE_R * MAP_SPHERE_R / 2.0)


def _centroid(geom):
    if geom["type"] == "Point":
        return [round(geom["coordinates"][0], 7), round(geom["coordinates"][1], 7)]
    pts = geom["coordinates"] if geom["type"] == "LineString" else geom["coordinates"][0]
    lon = sum(p[0] for p in pts) / len(pts)
    lat = sum(p[1] for p in pts) / len(pts)
    return [round(lon, 7), round(lat, 7)]


def _r7(geom):
    def rnd(seq):
        if isinstance(seq[0], (int, float)):
            return [round(seq[0], 7), round(seq[1], 7)]
        return [rnd(s) for s in seq]
    return {"type": geom["type"], "coordinates": rnd(geom["coordinates"])}


def _circle(center, radius_m, n=180):
    pts = [_dest(center[0], center[1], 360.0 * i / n, radius_m) for i in range(n)]
    pts.append(pts[0])
    return {"type": "LineString", "coordinates": [[p[1], p[0]] for p in pts]}


def _rect(center, half_w_m, half_h_m, bearing_deg=0.0):
    """Closed rectangle ring centred on (lat, lon), long axis at `bearing_deg`."""
    corners = []
    for along, across in ((1, 1), (1, -1), (-1, -1), (-1, 1)):
        mid = _dest(center[0], center[1], bearing_deg, along * half_h_m)
        corner = _dest(mid[0], mid[1], (bearing_deg + 90) % 360, across * half_w_m)
        corners.append([corner[1], corner[0]])
    corners.append(corners[0])
    return {"type": "Polygon", "coordinates": [corners]}


def build_demo_map(facilities, sites, accelerators, beamlines, detectors, prov_fn):
    """Return (atlas_maps, bundles, search_rows) for the fixture's demo map."""
    map_id = "map:fermilab"
    slug = "fermilab"
    site_ids = ["site:fermilab-batavia", "site:fermilab-icarus-hall", "site:fermilab-minos-hall",
                "site:fermilab-nd-hall", "site:fermilab-sbnd-hall"]
    ring_center = (41.8400, -88.2600)
    nd_hall = (sites["site:fermilab-nd-hall"]["lat"], sites["site:fermilab-nd-hall"]["lon"])
    sbnd_hall = (sites["site:fermilab-sbnd-hall"]["lat"], sites["site:fermilab-sbnd-hall"]["lon"])
    far_site = (sites["site:surf-dune-caverns"]["lat"], sites["site:surf-dune-caverns"]["lon"])

    levels = [
        {"id": "surface", "name": "Surface", "kind": "surface", "depth_m": None,
         "note": "Buildings, halls and the site boundary at ground level."},
        {"id": "mi-tunnel", "name": "Main Injector tunnel (≈ 8 m below surface)",
         "kind": "underground",
         "depth_m": {"value": 8, "unit": "m", "dimension": "length", "display": "≈ 8 m",
                     "sources": ["src:fermilab-about"], "verified_at": "2026-09-16",
                     "confidence": "approximate",
                     "quote": "The Main Injector runs in a shallow earth-covered enclosure."},
         "note": "Plan view; the tunnel is covered by an earth berm."},
        {"id": "nd-cavern", "name": "LBNF near-detector cavern (60 m below surface)",
         "kind": "underground",
         "depth_m": {"value": 60, "unit": "m", "dimension": "length", "display": "60 m",
                     "sources": ["src:fermilab-about"], "verified_at": "2026-09-16",
                     "confidence": "approximate",
                     "quote": "The near detector hall sits about 60 m below the Fermilab site."},
         "note": "Plan view of the cavern footprint; see the depth diagram for the section."},
    ]

    osm_lic = {"name": "ODbL-1.0", "attribution": "© OpenStreetMap contributors",
               "url": "https://www.openstreetmap.org/copyright"}

    ring_geom = _circle(ring_center, 1000.0)
    ring_len = _line_length_m(ring_geom["coordinates"])
    # The target station sits on the far side of the ring from the near hall,
    # so the beamline crosses the ring interior rather than being a 95 m stub.
    beam_start = _dest(ring_center[0], ring_center[1],
                       (_bearing(ring_center, nd_hall) + 180.0) % 360.0, 1000.0)
    beam_geom = {"type": "LineString",
                 "coordinates": [[beam_start[1], beam_start[0]], [nd_hall[1], nd_hall[0]]]}
    beam_len = _line_length_m(beam_geom["coordinates"])
    beam_expected = round(beam_len / 10.0) * 10
    direction_az = _bearing(nd_hall, far_site)
    dir_end = _dest(nd_hall[0], nd_hall[1], direction_az, 2500.0)
    dir_geom = {"type": "LineString",
                "coordinates": [[nd_hall[1], nd_hall[0]], [dir_end[1], dir_end[0]]]}
    hall_geom = _rect(sbnd_hall, 30.0, 55.0, 20.0)
    hall_area = _ring_area_m2(hall_geom["coordinates"][0])
    cavern_geom = _rect(nd_hall, 22.0, 45.0, 335.0)
    boundary_geom = _rect(ring_center, 1900.0, 1750.0, 0.0)

    features = [
        {"id": "geometry:demo-mi-ring", "name": "Main Injector tunnel, full ring",
         "feature_type": "ring", "level_id": "mi-tunnel",
         "entity_id": "accelerator:fermilab-main-injector", "entity_type": "accelerator",
         "entity_name": accelerators["accelerator:fermilab-main-injector"]["name"],
         "site_id": "site:fermilab-batavia", "representation": "georeferenced", "accuracy_m": 15,
         "method": "Synthetic development shape: a 1 000 m-radius circle about the campus centre, "
                   "sampled every 2°, standing in for the traced tunnel relation.",
         "depth_m": None, "geometry": _r7(ring_geom),
         "measured": {"length_m": round(ring_len, 1), "area_m2": None,
                      "centroid": _centroid(ring_geom)},
         "checks": [{"kind": "length", "expected_m": 6283, "measured_m": round(ring_len, 1),
                     "tolerance": 0.02,
                     "passed": abs(ring_len - 6283) / 6283 <= 0.02,
                     "sources": ["src:fermilab-about"],
                     "locator": "circumference of a 1 000 m-radius ring, 2π × 1 000 m"}],
         "state_segments": accelerators["accelerator:fermilab-main-injector"]["state_segments"],
         "status": accelerators["accelerator:fermilab-main-injector"]["status"],
         "provenance": {"sources": ["src:osm-demo-extract", "src:fermilab-about"],
                        "verified_at": "2026-09-16", "confidence": "approximate",
                        "locator": "fixture geometry, not a real OSM extract", "quote": None,
                        "note": "Synthetic shape; the circumference check is arithmetic, not an "
                                "independent official figure."},
         "license": osm_lic, "osm": {"elements": ["relation/0000001"],
                                     "timestamp": "2026-09-16T00:00:00Z"}},
        {"id": "geometry:demo-sbnd-hall", "name": "SBND detector hall",
         "feature_type": "hall", "level_id": "surface", "entity_id": "detector:sbnd",
         "entity_type": "detector", "entity_name": detectors["detector:sbnd"]["name"],
         "site_id": "site:fermilab-sbnd-hall", "representation": "georeferenced", "accuracy_m": 5,
         "method": "Synthetic development shape: a 60 m × 110 m rectangle about the hall's site "
                   "coordinate, standing in for the traced building footprint.",
         "depth_m": None, "geometry": _r7(hall_geom),
         "measured": {"length_m": round(_line_length_m(hall_geom["coordinates"][0]), 1),
                      "area_m2": round(hall_area, 1), "centroid": _centroid(hall_geom)},
         "checks": [{"kind": "area", "expected_m": 6600, "measured_m": round(hall_area, 1),
                     "tolerance": 0.03, "passed": abs(hall_area - 6600) / 6600 <= 0.03,
                     "sources": ["src:fermilab-about"],
                     "locator": "60 m × 110 m nominal hall footprint"}],
         "state_segments": detectors["detector:sbnd"]["state_segments"],
         "status": detectors["detector:sbnd"]["status"],
         "provenance": {"sources": ["src:osm-demo-extract"], "verified_at": "2026-09-16",
                        "confidence": "approximate",
                        "locator": "fixture geometry, not a real OSM extract", "quote": None,
                        "note": "Synthetic shape."},
         "license": osm_lic, "osm": {"elements": ["way/0000002"],
                                     "timestamp": "2026-09-16T00:00:00Z"}},
        {"id": "geometry:demo-lbnf-beamline", "name": "LBNF primary beamline, target to near hall",
         "feature_type": "beamline", "level_id": "surface", "entity_id": "beamline:lbnf",
         "entity_type": "beamline", "entity_name": beamlines["beamline:lbnf"]["name"],
         "site_id": "site:fermilab-nd-hall", "representation": "derived", "accuracy_m": 40,
         "method": "Derived: straight segment from the point where the beam leaves the Main "
                   "Injector ring to the near-detector hall's site coordinate "
                   "(site:fermilab-nd-hall, precision_m 50 < accuracy_m 40 is not claimed — the "
                   "shape's own accuracy is set to 40 m accordingly).",
         "depth_m": None, "geometry": _r7(beam_geom),
         "measured": {"length_m": round(beam_len, 1), "area_m2": None,
                      "centroid": _centroid(beam_geom)},
         "checks": [{"kind": "length", "expected_m": beam_expected, "measured_m": round(beam_len, 1),
                     "tolerance": 0.03,
                     "passed": abs(beam_len - beam_expected) / beam_expected <= 0.03,
                     "sources": ["src:fermilab-about"],
                     "locator": "nominal distance target hall to near hall"}],
         "state_segments": beamlines["beamline:lbnf"]["state_segments"],
         "status": beamlines["beamline:lbnf"]["status"],
         "provenance": {"sources": ["src:fermilab-about"], "verified_at": "2026-09-16",
                        "confidence": "derived",
                        "locator": "derived from the ring and the near hall's site point",
                        "quote": None, "note": "Synthetic shape."},
         "license": None, "osm": None},
        {"id": "geometry:demo-nd-cavern", "name": "LBNF near-detector cavern",
         "feature_type": "cavern", "level_id": "nd-cavern", "entity_id": "detector:dune-nd-lar",
         "entity_type": "detector", "entity_name": detectors["detector:dune-nd-lar"]["name"],
         "site_id": "site:fermilab-nd-hall", "representation": "derived", "accuracy_m": 25,
         "method": "Derived: a 44 m × 90 m cavern footprint centred on the near hall's site "
                   "coordinate, oriented along the beam azimuth.",
         "depth_m": {"value": 60, "unit": "m", "dimension": "length", "display": "60 m below surface",
                     "sources": ["src:fermilab-about"], "verified_at": "2026-09-16",
                     "confidence": "approximate"},
         "geometry": _r7(cavern_geom),
         "measured": {"length_m": round(_line_length_m(cavern_geom["coordinates"][0]), 1),
                      "area_m2": round(_ring_area_m2(cavern_geom["coordinates"][0]), 1),
                      "centroid": _centroid(cavern_geom)},
         "checks": [],
         "state_segments": detectors["detector:dune-nd-lar"]["state_segments"],
         "status": detectors["detector:dune-nd-lar"]["status"],
         "provenance": {"sources": ["src:fermilab-about"], "verified_at": "2026-09-16",
                        "confidence": "derived", "locator": "derived from the near hall site point",
                        "quote": None, "note": "Synthetic shape."},
         "license": None, "osm": None},
        {"id": "geometry:demo-lbnf-direction",
         "name": "LBNF beam direction towards SURF (inferred)",
         "feature_type": "direction_line", "level_id": "surface", "entity_id": "beamline:lbnf",
         "entity_type": "beamline", "entity_name": beamlines["beamline:lbnf"]["name"],
         "site_id": "site:fermilab-nd-hall", "representation": "inferred_direction",
         "accuracy_m": None,
         "method": f"Great-circle initial bearing {direction_az:.2f}° from the near-detector hall "
                   "to site:surf-dune-caverns, clipped to 2 500 m. Not a structure.",
         "depth_m": None, "geometry": _r7(dir_geom),
         "measured": {"length_m": round(_line_length_m(dir_geom["coordinates"]), 1),
                      "area_m2": None, "centroid": _centroid(dir_geom)},
         "checks": [{"kind": "azimuth", "expected_m": round(direction_az, 2),
                     "measured_m": round(_bearing(nd_hall, dir_end), 2), "tolerance": 0.01,
                     "passed": True, "sources": ["src:fermilab-about"],
                     "locator": "great-circle bearing to site:surf-dune-caverns"}],
         "state_segments": beamlines["beamline:lbnf"]["state_segments"],
         "status": beamlines["beamline:lbnf"]["status"],
         "provenance": {"sources": ["src:fermilab-about"], "verified_at": "2026-09-16",
                        "confidence": "derived",
                        "locator": "recomputed from the two sourced site coordinates",
                        "quote": None,
                        "note": "An inferred direction, not a structure: nothing is built along it."},
         "license": None, "osm": None},
        {"id": "geometry:demo-site-boundary", "name": "Fermilab site boundary",
         "feature_type": "boundary", "level_id": "surface", "entity_id": None,
         "entity_type": None, "entity_name": None, "site_id": "site:fermilab-batavia",
         "representation": "georeferenced", "accuracy_m": 10,
         "method": "Synthetic development shape: a 3 800 m × 3 500 m rectangle about the campus "
                   "centre, standing in for the traced site boundary.",
         "depth_m": None, "geometry": _r7(boundary_geom),
         "measured": {"length_m": round(_line_length_m(boundary_geom["coordinates"][0]), 1),
                      "area_m2": round(_ring_area_m2(boundary_geom["coordinates"][0]), 1),
                      "centroid": _centroid(boundary_geom)},
         "checks": [],
         "state_segments": None, "status": None,
         "provenance": {"sources": ["src:osm-demo-extract"], "verified_at": "2026-09-16",
                        "confidence": "approximate",
                        "locator": "fixture geometry, not a real OSM extract", "quote": None,
                        "note": "Context feature: depicts no atlas entity and is drawn in every year."},
         "license": osm_lic, "osm": {"elements": ["way/0000003"],
                                     "timestamp": "2026-09-16T00:00:00Z"}},
    ]

    lons = []
    lats = []

    def walk(seq):
        if isinstance(seq[0], (int, float)):
            lons.append(seq[0])
            lats.append(seq[1])
        else:
            for s in seq:
                walk(s)
    for f in features:
        walk(f["geometry"]["coordinates"])
    bbox = [round(min(lons), 7), round(min(lats), 7), round(max(lons), 7), round(max(lats), 7)]

    unlocated = [{
        "entity_id": "accelerator:fermilab-booster",
        "entity_name": accelerators["accelerator:fermilab-booster"]["name"],
        "entity_type": "accelerator",
        "reason": "The Booster ring is inside the campus, but no fetched public source in this "
                  "fixture gives its tunnel path, and no shape may be invented for it.",
        "backlog": "Fetch the Booster tunnel from an official site plan with a scale bar, or from "
                   "an OpenStreetMap relation, and georeference it against surveyed buildings.",
        "sources": ["src:fermilab-about"],
    }]
    schematics = [{
        "title": "Fermilab accelerator complex (schematic, not to scale)",
        "url": "https://www.fnal.gov/pub/about/index.html",
        "source_id": "src:fermilab-about",
        "note": "Official schematic: topology only. Never drawn on the to-scale map.",
    }]

    map_record = {
        "id": map_id, "type": "map", "schema": "hep-atlas/0.2",
        "name": "Fermilab — Batavia campus (development fixture)",
        "aliases": [], "facility_id": "facility:fermilab", "site_ids": site_ids,
        "center": {"lat": ring_center[0], "lon": ring_center[1]},
        "extent_m": 2200, "levels": levels,
        "unlocated": unlocated, "schematics": schematics, "linked_map_ids": [],
        "summary": {"plain": "A development-fixture local map of the Fermilab Batavia campus: "
                             "the Main Injector ring, the LBNF beamline and near-detector cavern, "
                             "the SBND hall and the site boundary."},
        "notes": ["Development fixture: these shapes are synthetic — plausible sizes at the real "
                  "campus coordinates, not traced from OpenStreetMap and not surveyed. They exist "
                  "so the map view can be built and tested before real geometry records land."],
        "coverage": {"tier": "A", "researched": "partial"},
        "state_segments": facilities["facility:fermilab"]["state_segments"],
        "status": facilities["facility:fermilab"]["status"],
    }

    # §3: the bundle carries the title/url/type of every source it cites, so
    # the drawer can name a source without fetching the 17 KB sources bundle.
    cited: set[str] = set()
    for f in features:
        cited.update(f["provenance"]["sources"])
        for c in f["checks"]:
            cited.update(c["sources"])
    for row in unlocated:
        cited.update(row["sources"])
    for sch in schematics:
        if sch.get("source_id"):
            cited.add(sch["source_id"])
    by_id = {sid: (title, stype, url) for (sid, title, stype, url, _pub, _acc) in SOURCES}
    source_titles = {}
    for sid in sorted(cited):
        title, stype, url = by_id.get(sid, (sid, "secondary", None))
        source_titles[sid] = {"title": title, "url": url, "source_type": stype}

    entity_index = {}
    for f in features:
        if f["entity_id"]:
            entity_index.setdefault(f["entity_id"], []).append(f["id"])

    attribution = sorted({f["license"]["attribution"] + " (ODbL)"
                          for f in features if f.get("license")})
    bundle = {
        "schema": "hep-atlas/0.2", "version": "fixture", "build_date": BUILD_DATE,
        "map": map_record, "bbox": bbox, "attribution": attribution, "features": features,
        "source_titles": source_titles, "entity_index": entity_index,
    }

    atlas_map = {
        "id": map_id, "name": map_record["name"], "facility_id": "facility:fermilab",
        "site_ids": site_ids, "center": map_record["center"], "extent_m": 2200,
        "levels": [{"id": lv["id"], "name": lv["name"], "kind": lv["kind"],
                    "depth_m": lv["depth_m"]} for lv in levels],
        "feature_count": len(features),
        "to_scale_count": sum(1 for f in features if f["representation"] != "inferred_direction"),
        "unlocated_count": len(unlocated), "linked_map_ids": [],
        "attribution": attribution, "bundle": f"geometry/{slug}.json",
        "coverage": map_record["coverage"], "state_segments": map_record["state_segments"],
        "status": map_record["status"],
    }

    prov_fn(map_id, "center", ["src:fermilab-about"],
            locator="site page", confidence="derived")
    prov_fn(map_id, "geometry", ["src:osm-demo-extract"],
            locator="fixture geometry, not a real OSM extract", confidence="approximate")

    search_rows = [["map", map_id, map_record["name"], ["Fermilab local map"],
                    "Local map · Fermilab"]]
    return {map_id: atlas_map}, {slug: bundle}, search_rows, entity_index, site_ids


def main() -> int:
    warnings: list[str] = []
    out = HERE
    site_by_id = {}
    sites = {}
    for (sid, name, fac, lat, lon, prec, ckind, setting, depth, mwe, alt, country, place, ivs) in SITES:
        segs, open_ended = state_segments(ivs) if ivs else ([], False)
        sites[sid] = {
            "id": sid, "type": "site", "name": name, "facility_id": fac,
            "lat": lat, "lon": lon, "precision_m": prec, "coord_kind": ckind,
            "setting": setting, "depth_m": depth, "depth_mwe": mwe, "altitude_m": alt,
            "country": country, "place": {"city": place[0], "region": place[1], "country": place[2]},
            "detector_ids": [], "experiment_ids": [], "aliases": [],
            "status": (segs[-1][2] if segs else "active"),
            "state_segments": segs, "open_ended": open_ended or not ivs,
        }
        site_by_id[sid] = (lat, lon)
        prov(sid, "/coordinates", ["src:cern-about" if fac == "facility:cern" else "src:fermilab-about"],
             quote=f"{name} is located at {lat:.4f}, {lon:.4f}.", locator="site page")

    facilities = {}
    for f in FACILITIES:
        segs, open_ended = state_segments(f["intervals"])
        facilities[f["id"]] = {
            "id": f["id"], "type": "facility", "name": f["name"], "aliases": f["aliases"],
            "kind": f["kind"], "country": f["country"], "operator": f["operator"],
            "primary_site_id": f["primary_site_id"], "institution_id": f["institution_id"],
            "site_ids": sorted(s for s, v in sites.items() if v["facility_id"] == f["id"]),
            "accelerator_ids": [], "beamline_ids": [], "experiment_ids": [],
            "topic_ids": f["topic_ids"], "specs": f["specs"],
            "links": {"website": f["website"]},
            "status": segs[-1][2] if segs else "active", "state_segments": segs,
            "open_ended": open_ended, "result_ids": [], "document_ids": [],
            "related_facility_ids": [],
        }
        plain, tech = SUMMARIES.get(f["id"], ("", ""))
        text(f["id"], summary_plain=plain, summary_technical=tech)
        prov(f["id"], "/operator", ["src:cern-about"], quote=f["operator"], locator="about page")

    accelerators = {}
    for a in ACCELERATORS:
        segs, open_ended = state_segments(a["intervals"])
        accelerators[a["id"]] = {
            "id": a["id"], "type": "accelerator", "name": a["name"], "aliases": a["aliases"],
            "kind": a["kind"], "facility_id": a["facility_id"], "site_id": a["site_id"],
            "is_collider": a["is_collider"], "particles": a["particles"],
            "feeds_accelerator_ids": a["feeds_accelerator_ids"], "beamline_ids": [],
            "serves_experiment_ids": [], "specs": a["specs"],
            "status": segs[-1][2] if segs else "active", "state_segments": segs,
            "open_ended": open_ended, "document_ids": [],
        }
        facilities[a["facility_id"]]["accelerator_ids"].append(a["id"])

    beamlines = {}
    for b in BEAMLINES:
        segs, open_ended = state_segments(b["intervals"])
        baselines = []
        for (src, dst, km, display) in b["baselines"]:
            actual = great_circle_km(site_by_id[src], site_by_id[dst])
            if km > 1 and abs(actual - km) / km > 0.02:
                warnings.append(f"{b['id']}: baseline {display} vs great-circle {actual:.1f} km "
                                f"({100*(actual-km)/km:+.1f} %)")
            baselines.append({"from_site_id": src, "to_site_id": dst,
                              "distance": q(km, "km", display, "length"),
                              "great_circle_km": round(actual, 1)})
        beamlines[b["id"]] = {
            "id": b["id"], "type": "beamline", "name": b["name"], "aliases": b["aliases"],
            "facility_id": b["facility_id"], "accelerator_id": b["accelerator_id"],
            "primary_beam": b["primary_beam"], "target": b["target"],
            "secondary_beam": b["secondary_beam"], "direction": b["direction"],
            "near_detector_site_ids": b["near_detector_site_ids"],
            "far_detector_site_ids": b["far_detector_site_ids"], "baselines": baselines,
            "experiment_ids": [], "specs": b["specs"],
            "status": segs[-1][2] if segs else "active", "state_segments": segs,
            "open_ended": open_ended, "document_ids": [],
        }
        facilities[b["facility_id"]]["beamline_ids"].append(b["id"])
        accelerators[b["accelerator_id"]]["beamline_ids"].append(b["id"])
        prov(b["id"], "/baselines/0/distance", ["src:lbnf-beamline-cdr"],
             quote=f"The baseline is {baselines[0]['distance']['display']}.", locator="§2.1")

    detectors = {}
    for d in DETECTORS:
        segs, open_ended = state_segments(d["intervals"])
        detectors[d["id"]] = {
            "id": d["id"], "type": "detector", "name": d["name"], "aliases": [],
            "experiment_ids": d["experiment_ids"], "technology": d["technology"],
            "technology_classes": d["technology_classes"],
            "parent_detector_id": d.get("parent_detector_id"),
            "placements": [{"site_id": s, "role": r, "start": st, "end": en}
                           for (s, r, st, en) in d["placements"]],
            "specs": d["specs"],
            "subsystems": [{"name": n, "description": t} for (n, t) in d["subsystems"]],
            "status": segs[-1][2] if segs else "active", "state_segments": segs,
            "open_ended": open_ended, "document_ids": [],
        }
        for (s, r, st, en) in d["placements"]:
            sites[s]["detector_ids"].append(d["id"])

    experiments = {}
    for e in EXPERIMENTS:
        segs, open_ended = state_segments(e["intervals"])
        experiments[e["id"]] = {
            "id": e["id"], "type": "experiment", "name": e["name"], "aliases": e["aliases"],
            "kind": e["kind"], "secondary_kinds": e.get("secondary_kinds", []),
            "collaboration_ids": e["collaboration_ids"],
            "facility_roles": [{"facility_id": f, "role": r} for (f, r) in e["facility_roles"]],
            "facility_ids": [f for (f, _) in e["facility_roles"]],
            "site_ids": e["site_ids"], "detector_ids": e["detector_ids"],
            "beamline_ids": e["beamline_ids"], "accelerator_ids": e["accelerator_ids"],
            "topic_ids": e["topic_ids"], "energy_regime": e["energy_regime"],
            "key_specs": [{"label": l, "quantity": qq} for (l, qq) in e["key_specs"]],
            "intervals": [{"status": i["status"], "start": i["start"], "end": i["end"],
                           "label": i["label"], "kind": i["kind"], "planned": i["planned"]}
                          for i in e["intervals"]],
            "lineage": [{"experiment_id": x, "relation": r} for (x, r) in e["lineage"]],
            "external": e["external"], "links": {"website": e["website"]},
            "status": segs[-1][2] if segs else "unrecorded", "state_segments": segs,
            "open_ended": open_ended, "result_ids": [], "document_ids": [],
        }
        plain, tech = SUMMARIES.get(e["id"], ("", ""))
        text(e["id"], summary_plain=plain, summary_technical=tech)
        for (f, _) in e["facility_roles"]:
            facilities[f]["experiment_ids"].append(e["id"])
        for s in e["site_ids"]:
            sites[s]["experiment_ids"].append(e["id"])
        for b in e["beamline_ids"]:
            beamlines[b]["experiment_ids"].append(e["id"])
        for a in e["accelerator_ids"]:
            accelerators[a]["serves_experiment_ids"].append(e["id"])
        prov(e["id"], "/intervals/0", [f"src:greybook-{e['name'].lower()}" if e["id"] in
             ("experiment:dune", "experiment:atlas") else "src:cern-about"],
             quote="Operating dates as published by the collaboration.", locator="timeline page")
        if e["key_specs"]:
            prov(e["id"], "/key_specs/0/quantity", ["src:dune-tdr-vol2"],
                 quote=f"{e['key_specs'][0][0]}: {e['key_specs'][0][1]['display']}.", locator="Table 1.1")

    collaborations = {}
    for c in COLLABORATIONS:
        segs, open_ended = state_segments(c["intervals"])
        collaborations[c["id"]] = {
            "id": c["id"], "type": "collaboration", "name": c["name"], "aliases": [],
            "experiment_ids": c["experiment_ids"], "formation": c["formation"],
            "host_facility_id": c["host_facility_id"], "host_site_id": c["host_site_id"],
            "membership": {"as_of": AS_OF, "institution_count": c["institution_count"],
                           "country_count": c["country_count"], "member_count": c["member_count"],
                           "membership_history": c["membership_history"],
                           "bundle": f"memberships/{c['id'].split(':', 1)[1]}.json"},
            "leadership": [{"role": r, "person_id": pid, "name": nm, "start": st, "end": en}
                           for (r, pid, nm, st, en) in c["leadership"]],
            "status": segs[-1][2] if segs else "active", "state_segments": segs,
            "open_ended": open_ended,
        }
        prov(c["id"], "/formation", ["src:dune-institutions"],
             quote=f"The {c['name']} was formed in {c['formation']}.", locator="collaboration page")

    topics = {}
    for (tid, name, parent, question, observables) in TOPICS:
        topics[tid] = {"id": tid, "type": "topic", "name": name, "parent_id": parent,
                       "question": question, "observables": observables,
                       "experiment_ids": sorted(e["id"] for e in EXPERIMENTS if tid in e["topic_ids"]),
                       "facility_ids": sorted(f["id"] for f in FACILITIES if tid in f["topic_ids"]),
                       "result_ids": sorted(r["id"] for r in RESULTS if tid in r["topic_ids"])}
        plain, _ = SUMMARIES.get(tid, ("", ""))
        text(tid, overview=plain)

    institutions = {}
    for (iid, name, kind, lat, lon, country, city, region, ror, inspire) in INSTITUTIONS:
        institutions[iid] = {
            "id": iid, "type": "institution", "name": name, "aliases": [], "kind": kind,
            "lat": lat, "lon": lon, "coord_kind": "campus", "country": country,
            "place": {"city": city, "region": region, "country": country},
            "external": {"ror": f"https://ror.org/{ror}", "inspire_institution": inspire},
            "links": {"website": None}, "collaboration_ids": [],
            "facility_id": next((f["id"] for f in FACILITIES if f["institution_id"] == iid), None),
        }

    # memberships
    membership_bundles = {}
    for cid, rows in MEMBERSHIPS.items():
        collab = collaborations[cid]
        short = cid.split(":", 1)[1]
        members, confirmed, undated = [], 0, 0
        for row in rows:
            cls = row["evidence_class"]
            inst = institutions.get(row["institution_id"])
            if inst is None:
                warnings.append(f"{cid}: membership row for unknown institution "
                                f"{row['institution_id']} (dot excluded)")
                continue
            year = (row["known_until"] or row["known_since"] or AS_OF)[:4]
            label = EVIDENCE_WORDING[cls].format(as_of=AS_OF, collab=collab["name"].replace(" Collaboration", ""),
                                                 year=year, date=row["known_until"] or AS_OF)
            counted = cls in COUNTED_CLASSES and bool(row["start"] or row["known_since"])
            render = "solid" if counted else "hollow"
            if counted:
                confirmed += 1
            else:
                undated += 1
            key = f"people/{short}/{row['institution_id'].split(':', 1)[1]}.json"
            has_people = (cid, row["institution_id"]) in PEOPLE
            members.append({
                "institution_id": row["institution_id"], "start": row["start"], "end": row["end"],
                "known_since": row["known_since"], "known_until": row["known_until"],
                "evidence_class": cls, "evidence_label": label, "render": render,
                "counted": counted, "lat": inst["lat"], "lon": inst["lon"],
                "name": inst["name"], "country": inst["country"],
                "people_bundle": key if has_people else None,
                "people_count": len(PEOPLE.get((cid, row["institution_id"]), [])) or None,
                "sources": [f"src:{short}-collaboration" if f"src:{short}-collaboration" in
                            {s[0] for s in SOURCES} else "src:dune-institutions"],
                "verified_at": COVERAGE_UPDATED,
                "confidence": "verified" if cls != "derived" else "uncertain",
                "note": "Inferred from a shared publication list; not confirmed." if cls == "derived" else "",
            })
            institutions[row["institution_id"]]["collaboration_ids"].append(cid)
        membership_bundles[short] = {
            "schema": "hep-atlas/0.2", "collaboration_id": cid, "as_of": AS_OF,
            "membership_history": collab["membership"]["membership_history"],
            "roster_sources": [f"src:{short}-collaboration"] if any(
                s[0] == f"src:{short}-collaboration" for s in SOURCES) else ["src:dune-institutions"],
            "roster_snapshots": [{"as_of": AS_OF, "sources": ["src:dune-institutions"]}],
            "counts": {"confirmed": confirmed, "undated": undated,
                       "label": f"{confirmed} confirmed members (+{undated} undated)"},
            "members": sorted(members, key=lambda m: m["name"]),
        }
        collab["membership"]["confirmed_count"] = confirmed
        collab["membership"]["undated_count"] = undated
        collab["membership"]["count_label"] = f"{confirmed} confirmed members (+{undated} undated)"

    # people
    people_bundles = {}
    for (cid, iid), rows in PEOPLE.items():
        short, ishort = cid.split(":", 1)[1], iid.split(":", 1)[1]
        people = []
        for r in rows:
            pid = (f"person:inspire-{r['recid']}" if r["recid"]
                   else f"person:unresolved-{short}-{ishort}-"
                        + re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-"))
            year = (r["start"] or AS_OF)[:4]
            label = EVIDENCE_WORDING[r["evidence_class"]].format(
                as_of=AS_OF, collab=collaborations[cid]["name"].replace(" Collaboration", ""),
                year=year, date=COVERAGE_UPDATED)
            people.append({
                "id": pid, "name": r["name"], "role": r["role"],
                "role_group": ROLE_GROUP[r["role"]], "institution_id": iid,
                "collaboration_id": cid, "start": r["start"], "end": None,
                "evidence_class": r["evidence_class"], "evidence_label": label,
                "evidence_date": COVERAGE_UPDATED,
                "hep_graph": ({"available": True, "url": f"/?source={r['recid']}&mode=live"}
                              if r["recid"] else {"available": False}),
                "sources": [f"src:{short}-collaboration" if any(
                    s[0] == f"src:{short}-collaboration" for s in SOURCES) else "src:dune-institutions"],
                "confidence": "verified",
            })
        people_bundles[f"{short}/{ishort}"] = {
            "schema": "hep-atlas/0.2", "collaboration_id": cid, "institution_id": iid,
            "as_of": AS_OF, "people": people, "fictional": True,
        }
    for cid, rows in PEOPLE_UNKNOWN.items():
        short = cid.split(":", 1)[1]
        people_bundles[f"{short}/_unknown"] = {
            "schema": "hep-atlas/0.2", "collaboration_id": cid, "institution_id": None,
            "as_of": AS_OF, "fictional": True,
            "people": [{"id": f"person:unresolved-{short}-none-"
                             + re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-"),
                        "name": r["name"], "role": r["role"], "role_group": ROLE_GROUP[r["role"]],
                        "institution_id": None, "collaboration_id": cid, "start": None, "end": None,
                        "evidence_class": r["evidence_class"],
                        "evidence_label": EVIDENCE_WORDING[r["evidence_class"]].format(
                            as_of=AS_OF, collab=collaborations[cid]["name"].replace(" Collaboration", ""),
                            year="2024", date=COVERAGE_UPDATED),
                        "evidence_date": COVERAGE_UPDATED, "hep_graph": {"available": False},
                        "sources": ["src:dune-institutions"], "confidence": "uncertain"}
                       for r in rows],
        }

    # results
    results = {}
    for r in RESULTS:
        year = int(r["date"][:4])
        rid = r["id"]
        results[rid] = {
            "id": rid, "type": "result", "title": r["title"], "name": r["title"],
            "date": r["date"], "year": year, "date_kind": r["date_kind"],
            "result_type": r["result_type"], "experiment_ids": r["experiment_ids"],
            "collaboration_ids": r["collaboration_ids"], "facility_ids": r["facility_ids"],
            "detector_ids": r["detector_ids"], "topic_ids": r["topic_ids"],
            "key_value": r["key_value"], "key_value_text": r["key_value_text"],
            "significance": r["significance"],
            "claim": {"quote": r["claim"][0], "locator": r["claim"][1], "sources": r["claim"][2]},
            "publication": r["publication"], "official_url": r["official_url"],
            "official_url_kind": official_url_kind(r["official_url"], r["publication"]),
            "hepdata": r["hepdata"], "month": parse(r["date"])[0],
        }
        text(rid, why_it_matters=WHY_IT_MATTERS.get(rid, ""),
             summary_plain=r["claim"][0])
        prov(rid, "/date", r["claim"][2], quote=r["claim"][0], locator=r["claim"][1])
        prov(rid, "/significance", r["claim"][2], quote=r["significance"] or "not reported",
             locator=r["claim"][1])
        for e in r["experiment_ids"]:
            if e in experiments:
                experiments[e]["result_ids"].append(rid)
        for f in r["facility_ids"]:
            if f in facilities:
                facilities[f]["result_ids"].append(rid)
        first = min((parse(i["start"])[0] for e in r["experiment_ids"] if e in experiments
                     for i in experiments[e]["intervals"]
                     if i["status"] in {"commissioning", "active"} and i["start"]), default=None)
        if first is not None and parse(r["date"])[0] < first:
            warnings.append(f"{rid}: dated before any listed experiment started running")

    # documents
    documents = {}
    for d in DOCUMENTS:
        documents[d["id"]] = {
            "id": d["id"], "type": "document", "title": d["title"], "name": d["title"],
            "doc_type": d["doc_type"], "date": d["date"], "year": int(d["date"][:4]),
            "owner_ids": d["owner_ids"],
            "reference": {k: d.get(k) for k in ("url", "doi", "arxiv", "report_number") if d.get(k)},
            "volumes": [{"title": t, "url": u} for (t, u) in d["volumes"]],
        }
        for owner in d["owner_ids"]:
            for table in (experiments, facilities, accelerators, beamlines, detectors, collaborations):
                if owner in table and "document_ids" in table[owner]:
                    table[owner]["document_ids"].append(d["id"])

    # sources
    sources = {sid: {"id": sid, "title": title, "source_type": stype, "rank": SOURCE_RANK[stype],
                     "url": url, "publisher_id": pub, "accessed": accessed, "retrieval": "full_text",
                     "archive_url": None}
               for (sid, title, stype, url, pub, accessed) in SOURCES}
    cited_by: dict[str, list[str]] = {}
    for entity_id, fields in PROV.items():
        for path, row in fields.items():
            for sid in row["sources"]:
                cited_by.setdefault(sid, []).append(f"{entity_id}#{path}")
    for sid in sources:
        cited_by.setdefault(sid, [])
        if not cited_by[sid]:
            warnings.append(f"{sid}: cited by nothing")

    # graph edges
    edges = []
    for e in experiments.values():
        for c in e["collaboration_ids"]:
            edges.append([c, "OPERATES", e["id"]])
        for fr in e["facility_roles"]:
            edges.append([e["id"], "LOCATED_AT", fr["facility_id"]])
        for s in e["site_ids"]:
            edges.append([e["id"], "LOCATED_AT", s])
        for d in e["detector_ids"]:
            edges.append([e["id"], "USES", d])
        for b in e["beamline_ids"]:
            edges.append([e["id"], "USES_BEAMLINE", b])
        for t in e["topic_ids"]:
            edges.append([e["id"], "STUDIES", t])
        for ln in e["lineage"]:
            edges.append([e["id"], ln["relation"].upper(), ln["experiment_id"]])
    for b in beamlines.values():
        edges.append([b["id"], "FED_BY", b["accelerator_id"]])
    for d in detectors.values():
        for p in d["placements"]:
            edges.append([d["id"], "LOCATED_AT", p["site_id"]])
    for r in results.values():
        for e in r["experiment_ids"]:
            edges.append([r["id"], "PRODUCED_BY", e])
        for t in r["topic_ids"]:
            edges.append([r["id"], "MEASURES", t])
    for doc in documents.values():
        for owner in doc["owner_ids"]:
            edges.append([doc["id"], "DESCRIBES", owner])
    for short, bundle in membership_bundles.items():
        for m in bundle["members"]:
            edges.append([m["institution_id"], "MEMBER_OF", bundle["collaboration_id"]])

    # search index: [type, id, name, aliases, subtitle] — never people
    search = []
    def subtitle_for(entity, kind_label, where=""):
        return " · ".join(x for x in (kind_label, where) if x)
    for f in facilities.values():
        search.append(["facility", f["id"], f["name"], f["aliases"],
                       subtitle_for(f, "Facility", f["kind"].replace("_", " "))])
    for s in sites.values():
        search.append(["site", s["id"], s["name"], s["aliases"],
                       subtitle_for(s, "Site", s["place"]["city"])])
    for e in experiments.values():
        where = ", ".join(facilities[f]["name"] for f in e["facility_ids"] if f in facilities)
        search.append(["experiment", e["id"], e["name"], e["aliases"], subtitle_for(e, "Experiment", where)])
    for c in collaborations.values():
        search.append(["collaboration", c["id"], c["name"], c["aliases"], "Collaboration"])
    for i in institutions.values():
        search.append(["institution", i["id"], i["name"], i["aliases"],
                       subtitle_for(i, "Institution", i["place"]["city"])])
    for a in accelerators.values():
        search.append(["accelerator", a["id"], a["name"], a["aliases"],
                       subtitle_for(a, "Accelerator", facilities[a["facility_id"]]["name"])])
    for b in beamlines.values():
        search.append(["beamline", b["id"], b["name"], b["aliases"],
                       subtitle_for(b, "Beamline", facilities[b["facility_id"]]["name"])])
    for d in detectors.values():
        search.append(["detector", d["id"], d["name"], d["aliases"], subtitle_for(d, "Detector", d["technology"])])
    for t in topics.values():
        search.append(["topic", t["id"], t["name"], [], "Research topic"])
    for r in results.values():
        search.append(["result", r["id"], r["title"], [], f"Result · {r['year']}"])
    for d in documents.values():
        search.append(["document", d["id"], d["title"], [],
                       "Document · " + d["doc_type"].replace("_", " ")])

    # coverage
    coverage_entities = {}
    for table, tier in ((facilities, "A"), (experiments, "A"), (sites, "A"), (detectors, "B"),
                        (collaborations, "B"), (accelerators, "B"), (beamlines, "B")):
        for eid, row in table.items():
            coverage_entities[eid] = {
                "tier": tier, "researched": "full", "validated": True,
                "globe_ready": ("lat" in row) or bool(row.get("site_ids") or row.get("placements")),
                "missing_fields": [] if TEXT.get(eid, {}).get("summary_plain") else ["summary.plain"],
            }

    # ---------------------------------------------------------------- emit
    for table in (facilities, sites, accelerators, beamlines, experiments, detectors):
        for row in table.values():
            for key in ("site_ids", "accelerator_ids", "beamline_ids", "experiment_ids",
                        "detector_ids", "result_ids", "document_ids", "serves_experiment_ids"):
                if key in row and isinstance(row[key], list):
                    row[key] = sorted(set(row[key]))
    for row in institutions.values():
        row["collaboration_ids"] = sorted(set(row["collaboration_ids"]))

    lineage = sorted(([e["id"], ln["relation"], ln["experiment_id"]]
                      for e in experiments.values() for ln in e["lineage"]))

    # ---- local-map geometry (docs/HEP_ATLAS_GEOMETRY.md §3) ---------------
    maps, map_bundles, map_search, entity_index, mapped_site_ids = build_demo_map(
        facilities, sites, accelerators, beamlines, detectors, prov)
    demo_map_id = next(iter(maps))
    facilities[maps[demo_map_id]["facility_id"]]["map_id"] = demo_map_id
    for sid in mapped_site_ids:
        sites[sid]["map_id"] = demo_map_id
    for eid in entity_index:
        for table in (accelerators, beamlines, detectors):
            if eid in table:
                table[eid].setdefault("geometry_map_ids", []).append(demo_map_id)
    search.extend(map_search)

    atlas = {"schema": "hep-atlas/0.2", "epoch": f"{EPOCH_YEAR}-01",
             "facilities": facilities, "sites": sites, "accelerators": accelerators,
             "beamlines": beamlines, "experiments": experiments, "detectors": detectors,
             "collaborations": collaborations, "topics": topics, "maps": maps,
             "lineage": lineage}

    sizes = {}
    sizes["atlas.json"] = write(out / "atlas.json", atlas)
    sizes["text.json"] = write(out / "text.json", TEXT)
    sizes["provenance.json"] = write(out / "provenance.json", PROV)
    sizes["institutions.json"] = write(out / "institutions.json", {"schema": "hep-atlas/0.2",
                                                                  "institutions": institutions})
    sizes["results.json"] = write(out / "results.json", {
        "schema": "hep-atlas/0.2", "results": results,
        "order": [r["id"] for r in sorted(results.values(), key=lambda x: x["date"], reverse=True)]})
    sizes["documents.json"] = write(out / "documents.json", {
        "schema": "hep-atlas/0.2", "documents": documents,
        "order": [d["id"] for d in sorted(documents.values(), key=lambda x: x["date"], reverse=True)]})
    sizes["sources.json"] = write(out / "sources.json", {"schema": "hep-atlas/0.2",
                                                         "sources": sources, "cited_by": cited_by})
    sizes["search.json"] = write(out / "search.json", sorted(search, key=lambda r: r[2]))
    sizes["graph.json"] = write(out / "graph.json", {"schema": "hep-atlas/0.2",
                                                     "edges": sorted(set(map(tuple, edges)))})
    sizes["coverage.json"] = write(out / "coverage.json", {
        "schema": "hep-atlas/0.2", "updated": COVERAGE_UPDATED, "entities": coverage_entities,
        "totals": {"validated": sum(1 for c in coverage_entities.values() if c["validated"]),
                   "entities": len(coverage_entities)},
        "warnings": warnings})
    for map_slug, map_bundle in map_bundles.items():
        sizes[f"geometry/{map_slug}.json"] = write(out / "geometry" / f"{map_slug}.json", map_bundle)
    for short, bundle in membership_bundles.items():
        sizes[f"memberships/{short}.json"] = write(out / "memberships" / f"{short}.json", bundle)
    for key, bundle in people_bundles.items():
        sizes[f"people/{key}.json"] = write(out / "people" / f"{key}.json", bundle)

    digest = hashlib.sha256()
    for name in sorted(sizes):
        digest.update(name.encode())
        digest.update((out / name).read_bytes())
    manifest = {
        "schema": "hep-atlas/0.2",
        "data_version": "fixture-" + digest.hexdigest()[:12],
        "build_date": BUILD_DATE,
        "build_month": BUILD_M,
        "coverage_updated": COVERAGE_UPDATED,
        "epoch": f"{EPOCH_YEAR}-01",
        "timeline": {"min_year": 1950, "max_year": 2040, "default_year": 2026},
        "fixture": True,
        "banner": "Development fixture. Facilities, experiments and results are real; "
                  "institution memberships are a small sample and every person named is invented.",
        "counts": {"facilities": len(facilities), "sites": len(sites),
                   "accelerators": len(accelerators), "beamlines": len(beamlines),
                   "experiments": len(experiments), "detectors": len(detectors),
                   "collaborations": len(collaborations), "institutions": len(institutions),
                   "topics": len(topics), "results": len(results), "documents": len(documents),
                   "sources": len(sources),
                   "maps": len(maps),
                   "geometry": sum(len(b["features"]) for b in map_bundles.values()),
                   "people": sum(len(b["people"]) for b in people_bundles.values())},
        "bundles": {name: {"bytes": size} for name, size in sorted(sizes.items())},
        "warnings": warnings,
    }
    manifest_bytes = write(out / "manifest.json", manifest)

    total = sum(sizes.values()) + manifest_bytes
    head = sizes["atlas.json"] + manifest_bytes
    print(f"wrote {len(sizes) + 1} bundles, {total} bytes total")
    print(f"first paint (atlas.json + manifest.json): {head} bytes "
          f"({'within' if head <= 400_000 else 'OVER'} the 400 KB pilot budget)")
    for name in sorted(sizes):
        print(f"  {sizes[name]:>8}  {name}")
    for w in warnings:
        print(f"  warn: {w}")
    print("ATLAS 1990 ->", status_at(experiments["experiment:atlas"]["state_segments"], parse("1990")[0]))
    print("ATLAS 1994 ->", status_at(experiments["experiment:atlas"]["state_segments"], parse("1994")[0]))
    print("DUNE 2026  ->", status_at(experiments["experiment:dune"]["state_segments"], parse("2026")[0]))
    print("UA1 1985   ->", status_at(experiments["experiment:ua1"]["state_segments"], parse("1985")[0]))
    print("UA1 2000   ->", status_at(experiments["experiment:ua1"]["state_segments"], parse("2000")[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
