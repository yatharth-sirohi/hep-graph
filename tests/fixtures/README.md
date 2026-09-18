# Deterministic and live regression inputs

- `identity_collisions.json` contains five specific Peter/Philip Bergmann literature cases, the current historical profile, and the transposed adviser-name/reference entries from Chen-Ning Yang's profile. Only selected public scholarly fields are retained. See `docs/IDENTITY_COLLISIONS.md` for source review and conservative handling.
- `live_pairs.json` is an explicit live-query matrix with stable author IDs, filters and known route upper bounds. Run `python tests/live_regression.py --group demo`; no network checks run automatically under pytest.

Synthetic graphs in the Python tests independently exercise boundaries, missing identities, multiple advisers, full author counts, repeat-work thresholds, errata, pagination, network failures, cancellation, and concurrency. NetworkX is the independent reference for graph calculations.
