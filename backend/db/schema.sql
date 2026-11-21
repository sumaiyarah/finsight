CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS companies (
    ticker  TEXT PRIMARY KEY,
    name    TEXT NOT NULL,
    cik     TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS filings (
    id           SERIAL PRIMARY KEY,
    ticker       TEXT NOT NULL REFERENCES companies(ticker),
    accession    TEXT NOT NULL UNIQUE,
    form_type    TEXT NOT NULL DEFAULT '10-K',
    fiscal_year  INT NOT NULL,
    period_end   DATE NOT NULL,
    filed_date   DATE NOT NULL,
    source_url   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sections (
    id          SERIAL PRIMARY KEY,
    filing_id   INT NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    item        TEXT NOT NULL,
    title       TEXT NOT NULL,
    start_page  INT NOT NULL,
    end_page    INT NOT NULL,
    UNIQUE (filing_id, item)
);

CREATE TABLE IF NOT EXISTS chunks (
    id           SERIAL PRIMARY KEY,
    section_id   INT NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    chunk_index  INT NOT NULL,
    page         INT,
    content      TEXT NOT NULL,
    token_count  INT,
    embedding    vector(384),
    UNIQUE (section_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS financial_facts (
    id            SERIAL PRIMARY KEY,
    filing_id     INT NOT NULL REFERENCES filings(id) ON DELETE CASCADE,
    metric        TEXT NOT NULL,
    fiscal_year   INT NOT NULL,
    value         NUMERIC NOT NULL,
    units         TEXT NOT NULL,
    source_table  TEXT,
    UNIQUE (filing_id, metric, fiscal_year)
);