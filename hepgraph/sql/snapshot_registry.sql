-- Version metadata and a single active pointer. Graph data is stored in
-- separate immutable, snapshot_id-keyed tables created by the eventual loader.
CREATE TABLE IF NOT EXISTS graph_snapshot (
    snapshot_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    build_code_commit TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_cutoff TIMESTAMPTZ NOT NULL,
    source_description TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN (
        'CREATED', 'FETCHING', 'BUILDING', 'VALIDATING', 'READY',
        'ACTIVE', 'FAILED', 'SUPERSEDED'
    )),
    checksum TEXT CHECK (checksum ~ '^[0-9a-f]{64}$'),
    validation_report JSONB
);
CREATE TABLE IF NOT EXISTS graph_pointer (
    singleton BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (singleton),
    current_snapshot TEXT REFERENCES graph_snapshot(snapshot_id),
    previous_snapshot TEXT REFERENCES graph_snapshot(snapshot_id),
    generation BIGINT NOT NULL DEFAULT 0
);
INSERT INTO graph_pointer(singleton) VALUES (TRUE) ON CONFLICT DO NOTHING;
