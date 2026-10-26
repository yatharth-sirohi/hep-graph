# Release round 9 — release candidate frozen and checked end to end

Integration branch `atlas-release`, 2026-10-25.

## What changed

* **Release report** — `docs/HEP_ATLAS_RELEASE_REPORT.md`: what a reader gets,
  before/after numbers against `main`, how the work was checked, the bugs fixed
  that predate the release, known gaps, and the deployment notes. It is the PR
  description.
* **Coverage report regenerated** after every data merge
  (`docs/HEP_ATLAS_COVERAGE.md`): 48 of 48 facilities with a local map, 0 failed
  geometry checks.
* **Deployment payload checked** — 13 MB of static files (the generated bundles
  are compact; the largest map bundle, Auger's ~1,600 stations, is 307 KB and
  loads only when that map opens); no build step on Vercel.
* **Scratch and worktrees cleaned** — the machine's disk had filled during the
  fact-checking runs (scratch reached ~7 GB); finished streams' scratch output
  and merged worktrees were removed, branches kept.

## How the experience improved, and why it is better

This round changes nothing a reader sees. It makes the release reviewable:
anyone deciding whether to ship it can read one report with the numbers and the
caveats, and each claim in it points to a round workup that says how it was
checked.

## Verified, and how (the frozen candidate)

| Check | Result |
| --- | --- |
| Validator | 0 errors |
| Python suite (whole repository) | 682 passed, 139 skipped (PostgreSQL-backed tests skip without a throwaway database) |
| Browser suite, real build | Chrome 96/96, Firefox 95/95, WebKit 95/95 |
| Accessibility suite | 35/35, 0 axe violations over 24 states |
| Map walkthrough | all 50 maps, recorded in round 10 |
| Quote checker | 3,682 verbatim + 319 joined segments of 4,206; no new misses |

## Open decision for the owner

"Report an error" links to the GitHub repository, which is private: a public
reader gets a 404. Options: a public issue form, an e-mail address, or making the
repository public. The release ships with the link as it is on `main` today.
