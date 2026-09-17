-- Doctoral edges are not collaboration topology and are not produced by the
-- compact INSPIRE import.  They arrive as a separately sourced overlay with its
-- own version, so a graph version is the pair (import_id, overlay_id) and a
-- neighborhood that needs doctoral edges cannot claim completeness from an
-- import certificate alone.
--
-- Apply to a candidate branch with a writer credential.  The serving credential
-- must be read-only.

CREATE TABLE IF NOT EXISTS graph_genealogy_overlay (
    overlay_id TEXT PRIMARY KEY,
    source_description TEXT NOT NULL,
    source_cutoff TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    -- Set only from an independent validation report, never by the loader.
    certified_complete BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS graph_genealogy_edge (
    overlay_id TEXT NOT NULL REFERENCES graph_genealogy_overlay(overlay_id),
    adviser_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    -- The INSPIRE record the relation was read from; it is the displayed
    -- evidence reference, so it is part of the key rather than a free column.
    source_record TEXT NOT NULL,
    degree TEXT,
    year SMALLINT,
    PRIMARY KEY (overlay_id, adviser_id, student_id, source_record),
    CHECK (adviser_id <> student_id)
);

CREATE INDEX IF NOT EXISTS graph_genealogy_edge_student
    ON graph_genealogy_edge (overlay_id, student_id, adviser_id);
CREATE INDEX IF NOT EXISTS graph_genealogy_edge_adviser
    ON graph_genealogy_edge (overlay_id, adviser_id, student_id);
