# V0.3 free-tier storage decision — provisional, 2026-09-16

## Decision

Prototype the private, immutable versioned graph on **Turso Cloud** and serve it from the existing Python application on Vercel through Turso's remote Python `libsql` client. Turso is a Vercel Marketplace integration and can attach `TURSO_DATABASE_URL` and `TURSO_AUTH_TOKEN` to the `hep-graph` project when that project is accessible. Do not create a paid plan, enable overages, or provision a permanent build server.

This is a **conditional free-tier target**, not a promise that the unknown full INSPIRE graph fits. [Turso's current pricing](https://turso.tech/pricing) lists a free plan with 5 GB storage, 500 million rows read and 10 million rows written per month, without a required credit card. Candidate B and rollback copy A must coexist within the storage limit. A single large full build could exceed the monthly write allowance, even when its final file fits. Verify precisely how import/build operations are metered before full bootstrap; if the free allowance is insufficient, stop rather than silently upgrading.

[Neon's free Postgres plan](https://neon.com/pricing) has 0.5 GB storage per project, which is already too close to the lower-bound pilot extrapolation for a versioned graph. [Vercel Blob Hobby](https://vercel.com/docs/vercel-blob/usage-and-pricing) includes only 1 GB-month of storage. It is suitable for small manifests but not a presumed full raw INSPIRE archive. [Cloudflare R2's free Standard tier](https://developers.cloudflare.com/r2/pricing/) offers 10 GB-month and an operations allowance, but would add a separate account, credentials and serving path; revisit it only if measured snapshot artifacts require it. None of these services is guaranteed to hold a full corpus plus rollback within free limits.

One read-only INSPIRE count request on 2026-09-16 returned **1,885,680 literature records** across the endpoint, before applying HEP Graph's eligibility policy. This is a useful upper-level scale signal, **not** an audited partition count, and it does not reveal authorship incidence or index size. The synthetic prototype is **5.3 MB** for 1,501 works and 3,000 people including one 2,932-author paper. That deliberately skewed fixture says nothing reliable about full corpus size, write volume, object archive size, or Vercel latency. The saved pilot-based scenarios in `PRODUCTION_GRAPH_STORAGE_DESIGN.md` are also lower bounds, not a capacity certificate. At its pilot density, even the incidence rows alone could approach Turso's 10-million-per-month free write limit during bootstrap; precomputed adjacency adds further writes. Whether [Turso's SQLite-file import](https://docs.turso.tech/cli/db/create) (limited to 2 GB per file) counts differently against that quota is unverified and must be checked before a full build.

## Account and project status

The connected Vercel Hobby team currently lists `ouriowacity` but no `hep-graph` project. The `hep-graph` GitHub repository exists. Project creation/linking must be verified before any preview deployment or Marketplace provision. The requested university email is `yatharth-sirohi@uiowa.edu`; account registration and email verification have not been completed. No credentials or private URLs belong in this repository.

## Free-only gate before a full build

1. Confirm INSPIRE's approved bulk acquisition method or independently validate a bounded, rate-compliant partition strategy.
2. Measure representative work count, author-incidence and large-team distribution. Estimate final hot index, simultaneous candidate/active storage and one-time row writes.
3. Verify free-tier limits in the target account, with overages **off**. If the candidate plus rollback cannot fit or build allowance is insufficient, do not launch the full harvest or switch to paid service without a new user decision.
4. Build, validate, benchmark, preview and explicitly promote only after the complete-source certificate passes. The pilot and synthetic data cannot be promoted.

V0.3 has no scheduler, automatic refresh, incremental importer or automatic promotion, so its recurring synchronization compute is zero. The remaining recurring cost can be $0 **only if** production use stays inside every provider's free allowance; otherwise service may pause rather than accrue charges.
