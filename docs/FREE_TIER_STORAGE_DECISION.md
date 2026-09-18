# V0.3 cost-minimized storage decision — 2026-09-16

## Decision

Target **Neon Postgres** for the private, immutable graph and its transactional active-version pointer. An existing Neon project (`lively-voice-03358486`, `Hep-Atlas`) is now linked directly to this repository on its `production` branch; no graph schema or data has been loaded. Connect that project to the actual `hep-graph` Vercel project only after the latter is visible to the connected account. Keep Vercel on **Hobby** initially; do not buy Vercel Pro solely to obtain a database. Use Neon's Free plan only for a bounded prototype that fits its limits, then move to **usage-based Launch** when the measured active + candidate + rollback footprint exceeds Free. Do not change to a paid plan or begin a full harvest until the source method, size, and spend ceiling are verified. Keep source/checkpoint artifacts private; add object storage only when a measured need justifies a second service. No scheduler or automatic refresh is part of v0.3.

This supersedes the earlier conditional Turso-free target. [Vercel Postgres is no longer provisioned for new projects](https://vercel.com/docs/postgres); [Marketplace is available on all Vercel plans](https://vercel.com/changelog/neon-now-available-on-vercel-marketplace). The user supplied an **existing** Neon project, so this setup used Neon's CLI rather than creating a duplicate Marketplace database. The project reports region `aws-us-east-2`; future Vercel functions should be colocated as closely as practical, with pooled connections and server-only, least-privilege credentials.

## Why this is the cheaper *viable* target

One read-only INSPIRE count on 2026-09-16 returned **1,885,680 literature records** before HEP Graph eligibility filtering. It is not a certified graph count. The saved, biased pilot has 1,180 works and 5,996 work-author incidences (5.08/work). At that density, the all-literature count implies about **9.6 million incidence rows**; adding work records alone passes **11 million inserts**, before authors, small-team adjacency, evidence, indexes or a second immutable version. The eligible subset may be smaller, and a provider's file-import metering may differ; this is a risk estimate, not a measured invoice. [Turso Free](https://turso.tech/pricing) offers 5 GB storage but only **10 million rows written per month**. One full candidate build could hit that ceiling even if the finished database fits. Its SQLite-file import also has a [2 GB file limit](https://docs.turso.tech/cli/db/create); how imports consume the write allowance is unverified. A paid Turso plan could work, but would not obviously beat low-volume Neon Launch on cost or operational simplicity for transactional, versioned graph data.

[Neon Free](https://neon.com/pricing) includes **0.5 GB storage per project** and **100 CU-hours/month per project**. The pilot's local SQLite hybrid index scales to about **0.62 GB for 1.89 million works** and **1.24 GB for two versions**, *before* profiles, evidence, indexes, checkpoints, history or large-team skew. Postgres bytes are not SQLite bytes. This makes Free useful for development, but not a credible full-snapshot capacity promise. Neon Launch has no analogous monthly row-write quota and charges by compute/storage; this avoids a one-time bootstrap being blocked at an arbitrary row count. Keep at least active and previous known-good snapshots; candidate overlap is additional temporary storage.

## Planning estimate, not a quote

At [Neon Launch's published rates](https://neon.com/pricing) of **$0.106/CU-hour** and **$0.35/GB-month** database storage, illustrative monthly database charges are:

| Measured usage scenario | Compute | Database storage | Subtotal before history, transfer and other usage |
|---|---:|---:|---:|
| Light, 25 CU-hours and 2 GB | $2.65 | $0.70 | **$3.35** |
| Moderate, 100 CU-hours and 5 GB | $10.60 | $1.75 | **$12.35** |
| Higher, 200 CU-hours and 10 GB | $21.20 | $3.50 | **$24.70** |

Neon also meters retained history/data changes and potentially transfer; full initial loading may consume more compute than steady serving. Scale-to-zero can keep intermittent-use compute low, but latency and actual usage must be measured. These scenarios do **not** include Vercel function overages, tax, object storage or extra branch costs. The actual database could be substantially larger than the SQLite lower bound.

[Vercel Pro](https://vercel.com/docs/plans/pro-plan) is a **$20/month platform fee** with a $20 credit for Vercel-managed infrastructure, not a $20 all-in database subscription. [Marketplace integrations have independent billing](https://vercel.com/docs/integrations/create-integration/billing), so do **not** subtract the Vercel credit from Neon charges. If Hobby suffices, total fixed Vercel platform fee remains $0 and the database alone may cost a few to a few dozen dollars per month. If Pro is later required, add $20/month to Neon and any other charges. Do not upgrade speculatively.

[Vercel Blob Hobby](https://vercel.com/docs/vercel-blob/usage-and-pricing) includes only 1 GB-month, so it is not a presumed full source archive. [Cloudflare R2 Standard](https://developers.cloudflare.com/r2/pricing/) has 10 GB-month free storage but adds a separate account and credential set. Select private object storage only after measuring the compressed source/checkpoint artifacts; until then, do not pay for an unused store or claim the full archive fits a free tier.

## External setup and acceptance gate

The currently connected Vercel Hobby team listed `ouriowacity` but **not** `hep-graph`; its project lookup failed. The GitHub repository exists, but the correct Vercel account/team or project must be exposed before attaching Neon or running a preview. The existing Neon project `lively-voice-03358486` (`Hep-Atlas`) was linked locally to branch `production`, and `neon deploy` reported no remote changes. The CLI pulled credentials into gitignored `.env.local`; none are committed. Account ownership/email and billing plan should be verified in the Neon dashboard. No new database, paid-plan change, graph schema, production graph data, or full INSPIRE acquisition has been initiated.

Before provisioning or promoting: (1) establish an approved, bounded INSPIRE acquisition method; (2) measure a representative eligible corpus, incidence/large-team distribution, final hot index, and simultaneous active/candidate/rollback storage; (3) set an explicit provider spend control and verify the selected plan in the user's account; (4) build and independently validate a complete-source candidate; (5) benchmark the preview and explicitly promote with rollback tested. The saved pilot and synthetic tests cannot be promoted. All private artifacts and credentials stay out of Git.
