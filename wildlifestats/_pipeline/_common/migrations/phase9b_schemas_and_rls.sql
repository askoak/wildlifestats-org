-- Phase 9b.1 — WildlifeStats lane schemas + §19 RLS contract.
--
-- Applied to Supabase project oamqicylpytbldrnybcc via the Supabase MCP
-- apply_migration tool on 2026-06-11 (migration name:
-- wildlifestats_phase9b_schemas_and_rls). This file is the version-controlled
-- copy for repo history; re-applying it is a safe no-op (see idempotency note).
--
-- LANE DISCIPLINE (§19): the project is SHARED with askoak-web (BRWC) and
-- SmartDiag. This migration is ADDITIVE ONLY — it creates new wildlifestats_*
-- schemas and never touches brwc_*, public, or any existing object. A
-- pre-flight check confirmed no brwc_* / wildlifestats_* schema existed before
-- apply, so there was no collision to escalate.
--
-- §19 SERVER-SIDE ENFORCEMENT — design note:
-- The engineer order's template uses an RLS policy `TO authenticated`. But the
-- production write path (supabase_client.upsert) uses the service_role token,
-- and service_role BYPASSES RLS. So RLS alone could NOT stop a misconfigured
-- service_role caller from writing a BRWC raw record. The load-bearing gate is
-- therefore a CHECK CONSTRAINT (raw_records_no_brwc_ein), which no role —
-- including service_role — can bypass. The RLS policy is retained as
-- defense-in-depth for the authenticated role, per the order. Both gates live.
--
-- IDEMPOTENCY (9b.3): every statement is CREATE ... IF NOT EXISTS, an
-- idempotent GRANT/ALTER DEFAULT PRIVILEGES, or DROP POLICY IF EXISTS +
-- CREATE POLICY. Re-running converges to the same state with no error.

-- 1) Public-tier bucket schemas (anon + authenticated read; service_role write)
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_01_social_signals;
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_02_firm_profile;
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_03_publications;
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_04_help_content;
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_06_aggregate;
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_07_regulatory;
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_08_media_academic;
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_09_network;
CREATE SCHEMA IF NOT EXISTS wildlifestats_bucket_10_events;

-- 2) Secure schemas (authenticated only; NO anon; service_role write)
CREATE SCHEMA IF NOT EXISTS wildlifestats_secure_bucket_05_raw_records;
CREATE SCHEMA IF NOT EXISTS wildlifestats_secure_aggregate_drafts;

-- 3) Grants + default privileges
DO $$
DECLARE s text;
BEGIN
  FOREACH s IN ARRAY ARRAY[
    'wildlifestats_bucket_01_social_signals','wildlifestats_bucket_02_firm_profile',
    'wildlifestats_bucket_03_publications','wildlifestats_bucket_04_help_content',
    'wildlifestats_bucket_06_aggregate','wildlifestats_bucket_07_regulatory',
    'wildlifestats_bucket_08_media_academic','wildlifestats_bucket_09_network',
    'wildlifestats_bucket_10_events'] LOOP
    EXECUTE format('GRANT USAGE ON SCHEMA %I TO anon, authenticated, service_role', s);
    EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT SELECT ON TABLES TO anon, authenticated', s);
    EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT ALL ON TABLES TO service_role', s);
  END LOOP;
  FOREACH s IN ARRAY ARRAY[
    'wildlifestats_secure_bucket_05_raw_records','wildlifestats_secure_aggregate_drafts'] LOOP
    EXECUTE format('GRANT USAGE ON SCHEMA %I TO authenticated, service_role', s);
    EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT SELECT ON TABLES TO authenticated', s);
    EXECUTE format('ALTER DEFAULT PRIVILEGES IN SCHEMA %I GRANT ALL ON TABLES TO service_role', s);
  END LOOP;
END $$;

-- 4) Bucket 05 raw_records — the §19 load-bearing table.
--    CHECK constraint = bulletproof gate (no role, incl. service_role, bypasses).
--    RLS policy       = defense-in-depth for authenticated, per the order.
CREATE TABLE IF NOT EXISTS wildlifestats_secure_bucket_05_raw_records.raw_records (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  rehab_org_ein text NOT NULL,
  rehab_org_id  text,
  record        jsonb NOT NULL,
  fetched_at    timestamptz NOT NULL,
  source_url    text NOT NULL,
  content_hash  text NOT NULL,
  created_at    timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT raw_records_no_brwc_ein CHECK (rehab_org_ein <> '54-1641798'),
  CONSTRAINT raw_records_uniq UNIQUE (rehab_org_ein, content_hash)
);
ALTER TABLE wildlifestats_secure_bucket_05_raw_records.raw_records ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS no_brwc_rawrecords ON wildlifestats_secure_bucket_05_raw_records.raw_records;
CREATE POLICY no_brwc_rawrecords ON wildlifestats_secure_bucket_05_raw_records.raw_records
  FOR ALL TO authenticated
  USING (rehab_org_ein <> '54-1641798')
  WITH CHECK (rehab_org_ein <> '54-1641798');
GRANT SELECT, INSERT, UPDATE ON wildlifestats_secure_bucket_05_raw_records.raw_records TO authenticated;
GRANT ALL ON wildlifestats_secure_bucket_05_raw_records.raw_records TO service_role;

-- NOTE — PostgREST schema exposure is NOT performed here.
-- For supabase_client.upsert() to write via REST, the wildlifestats_* schemas
-- must be added to the project's "Exposed schemas" (Settings → API). That is a
-- project-level config change with blast radius on the shared project's REST
-- API (SmartDiag's 23 public tables), unverifiable from this lane, so it is
-- intentionally left as an owner/architect-gated step rather than forced into a
-- migration here. The live upsert test is flag-gated until exposure is set.
