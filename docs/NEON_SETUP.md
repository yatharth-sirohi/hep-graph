# Neon setup checkpoint — 2026-09-16

The HEP-Graph repository's `cloud-database-migration` branch is linked to an **existing** Neon project, `Hep-Atlas` (`lively-voice-03358486`), on the `production` branch (`br-still-cherry-b5csn5wd`) in `aws-us-east-2`. PostgreSQL version is 18. This is infrastructure configuration only: the application still uses live INSPIRE, and no graph schema, source corpus, or snapshot has been written into Neon.

Setup performed with Neon CLI 4.19.0:

1. Updated the globally installed CLI and authenticated its existing `DEFAULT` profile.
2. Installed Neon agent skills in the project for Claude Code (the CLI's automatic detection) and for Codex. Installed Neon MCP for **Codex in this project only**, pinned to `lively-voice-03358486` with OAuth; no account-wide API key was minted for MCP. The MCP entry is `.codex/config.toml` and contains no secret.
3. Ran `neon link --project-id lively-voice-03358486 --branch production -y`. The local `.neon` pointer and `.env.local` are gitignored. Neon pulled `DATABASE_URL`, `DATABASE_URL_UNPOOLED`, and `NEON_BRANCH`; their values must never be logged or committed.
4. Ran `neon config init`, then reduced `neon.ts` to the requested `defineConfig({})`. The generated `@neon/config` and `@neon/env` dependencies are recorded in `package.json`/`package-lock.json`.
5. `neon config plan` reported **no changes** to `production` (Postgres only). `neon deploy` succeeded with **no remote changes** and refreshed only the local ignored env file. A read-only `SELECT 1` against `production` succeeded.

Do **not** apply `hepgraph/sql/snapshot_registry.sql` or load the partial `data/current.json` as a production graph. Before the next phase, verify the INSPIRE full-source acquisition and completeness policy, test schema changes on an isolated Neon branch, and use `DATABASE_URL_UNPOOLED` (direct connection) for migrations; `DATABASE_URL` is pooled for future serverless reads. The connected Vercel account still does not expose the requested `hep-graph` project, so no Vercel environment variables or preview deployment have been configured. `neon.ts` declares no Auth, Functions, Object Storage, Data API, AI Gateway, or scheduled triggers.
