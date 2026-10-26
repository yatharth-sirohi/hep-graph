# Rules for every Atlas work stream (M1–M6 and the coverage wave)

Read `CLAUDE.md` at the repository root first; these rules add to it.

## Git and the machine

* Work only inside your own worktree (the path in your brief). Never run
  `git checkout`, `switch`, `reset`, `restore` or `stash` in any other worktree
  or in `~/Desktop/HEP-Graph`. Commit on your own branch; never push, never merge
  other branches unless your brief says so.
* Never commit `static/atlas/generated/`. Build to check your work, then
  `git checkout -- static/atlas/generated` in your own worktree before committing.
  The integrator rebuilds at merge.
* The disk is nearly full. Keep downloads in your scratch directory, delete PDFs
  once you have extracted what you need, install nothing.
* Python: `/Users/yatharthsirohi/Desktop/HEP-Graph/.venv/bin/python`. Validator:
  `… -m hepgraph.atlas.validate` (must end with 0 errors). Build:
  `… -m hepgraph.atlas.build`.
* End commit messages with
  `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Never

* Never contact inspirehep.net (its rate budget belongs to the supervised
  importer). Never touch Neon, Vercel, or any deployment.
* Never cite Wikipedia or another encyclopaedia. You may use one to find the
  primary source, then cite and quote that source.
* Never invent a value, a date, a coordinate or a quote. A field nobody
  publishes stays empty and goes into your log's "unresolved" list.

## Every fact is sourced

Follow `docs/HEP_ATLAS_ONTOLOGY.md` (amendments A1–A26) and copy the shape of
existing records in `data/atlas/`.

* A sourced value carries `quote` (copied **verbatim** from the page or PDF you
  fetched today), `locator` (section, page, table), `sources` (ids of records in
  `data/atlas/sources/`), `confidence`, and `verified_at: "2026-10-26"`.
* Prefer, in order:
  1. collaboration papers (arXiv, journal);
  2. official laboratory or collaboration pages;
  3. design reports;
  4. the PDG;
  5. reputable lab news offices.

  Before creating a source record, search `data/atlas/sources/` for the same URL
  and reuse it.
* Coordinates follow A17: an underground lab's or a detector's coordinate may not
  rest only on a rank ≥ 8 source (geocoder, map tile). Otherwise use a
  campus-grade point marked `approximate` with its precision.
* `status` is as of 2026-10-26 and must agree with the dated intervals (A10).
  Proposed experiments are `proposed` only when a design report or collaboration
  document names them and their host site.
* Canonical JSON formatting (A11): `json.dumps(sort_keys=True, indent=2,
  ensure_ascii=False)` plus a trailing newline.

## The mandatory bar for a new experiment

1. **Identity:** name, aliases and kind.
2. **Time:** status and dated intervals (a start, and an end if it ended).
3. **Place:** a located site with coordinates on a facility.
4. **Content:**
   * topics;
   * `summary.plain` (≤ 60 words, for a newcomer) and `summary.technical`;
   * the official website if one exists;
   * at least one authoritative source;
   * a collaboration record if a collaboration exists;
   * lineage (predecessor, successor, upgrade) where a source states it.
5. **Tracking:** a coverage registry row in `data/atlas/coverage/<owner>.json`.

Tier A is reserved for flagships researched to full depth, with key results and
specifications. Most new rows are B–D.

## Ownership

Create only the facilities, sites, accelerators, topics and experiments your
brief assigns to you. Reference only ids that already exist on your branch. If
you need something another stream owns, leave the reference out and list it
under "for the integrator" in your log.

## What you hand back

* **A log** at `docs/atlas-worklog/<OWNER>.md`, containing:
  * scope;
  * a table of every entity written, with its start/end/status/site and the URL
    and quote behind each date and coordinate;
  * conflicts (claim / source A / source B / chosen / why);
  * unresolved fields;
  * candidates you considered and excluded, with the reason.
* **A final report** of at most 400 words: counts, new facilities, anything
  unresolved, and the checks you ran (validator line, build line, tests).
