CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE questions (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL REFERENCES users(id),
    question       TEXT NOT NULL,
    answer         TEXT,
    sources        TEXT[],
    latency_ms     INTEGER,
    first_token_ms INTEGER,
    top_similarity REAL,
    chunks_used    INTEGER,
    refused        BOOLEAN NOT NULL DEFAULT FALSE,
    feedback       SMALLINT CHECK (feedback IN (1, -1)),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE chunks (
    id         SERIAL PRIMARY KEY,
    source_url TEXT NOT NULL,
    content    TEXT NOT NULL,
    embedding  vector(384) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sources (
    url          TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    last_checked TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE eval_results (
    id             SERIAL PRIMARY KEY,
    run_id         TEXT NOT NULL,
    question       TEXT NOT NULL,
    answerable     BOOLEAN NOT NULL,
    top_similarity REAL,
    passed         BOOLEAN NOT NULL,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE eval_answers (
    id         SERIAL PRIMARY KEY,
    run_id     TEXT NOT NULL,
    question   TEXT NOT NULL,
    case_type  TEXT NOT NULL,
    answer     TEXT NOT NULL,
    faithful   BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE VIEW v_usage AS
SELECT id, created_at::date AS day, latency_ms, first_token_ms,
       top_similarity, chunks_used, refused, feedback
FROM questions;

CREATE VIEW v_eval AS
SELECT run_id, created_at::date AS day, answerable, passed, top_similarity
FROM eval_results;

CREATE VIEW v_faithfulness AS
SELECT run_id, created_at::date AS day, case_type, faithful
FROM eval_answers;