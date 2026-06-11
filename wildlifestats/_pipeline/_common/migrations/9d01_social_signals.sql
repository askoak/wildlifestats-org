-- Phase 9d.01.1 — social-signals sink table.
--
-- Applied to Supabase project oamqicylpytbldrnybcc via Supabase MCP
-- apply_migration on 2026-06-11 (migration name: wildlifestats_9d01_social_signals)
-- once cross-lane #290 (PostgREST Exposed Schemas) closed. Version-controlled copy
-- for repo history; re-applying is a safe no-op (idempotency verified live).
--
-- This is a PUBLIC-TIER bucket: it stores EXTRACTED signals only (event type,
-- species, county, week, confidence) — never raw post text. Per the §19
-- clarification, brand mentions in attributed public-content tables are allowed;
-- the raw-record exclusion applies only to wildlifestats_secure_bucket_05_raw_records.
-- So there is no BRWC-EIN CHECK here, by design.

CREATE TABLE IF NOT EXISTS wildlifestats_bucket_01_social_signals.signals (
  id                     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  record_id              text NOT NULL,              -- §4 sha256(source_url+signal_id+event_date)
  signal_id              text NOT NULL,
  org_slug               text,
  source_org_id          text,
  platform               text,
  event_type             text,
  species_canonical      text,
  species_verbatim       text,
  geo_state              text,
  geo_county_fips        text,
  geo_locality_verbatim  text,
  event_date             date,
  event_date_precision   text,
  confidence             numeric,
  iso_week               text,
  extraction_method      text,
  extraction_prompt_hash text,
  -- provenance envelope (required by supabase_client._validate_provenance)
  fetched_at             timestamptz NOT NULL,
  source_url             text NOT NULL,
  content_hash           text NOT NULL,
  created_at             timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT signals_uniq UNIQUE (record_id)
);

ALTER TABLE wildlifestats_bucket_01_social_signals.signals ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS public_read_signals ON wildlifestats_bucket_01_social_signals.signals;
CREATE POLICY public_read_signals ON wildlifestats_bucket_01_social_signals.signals
  FOR SELECT TO anon, authenticated USING (true);
GRANT SELECT ON wildlifestats_bucket_01_social_signals.signals TO anon, authenticated;
GRANT ALL ON wildlifestats_bucket_01_social_signals.signals TO service_role;
CREATE INDEX IF NOT EXISTS signals_signal_week_idx
  ON wildlifestats_bucket_01_social_signals.signals (signal_id, geo_state, iso_week);

-- on_conflict key for supabase_client.upsert(): record_id (UNIQUE signals_uniq).
