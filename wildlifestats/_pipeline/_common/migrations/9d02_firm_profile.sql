-- Phase 9d.02 — firm-profile website dossiers.
--
-- Version-controlled migration copy for the shared Supabase project
-- oamqicylpytbldrnybcc. PUBLIC-TIER bucket: public website-derived content only.
-- No BRWC raw-record exclusion is needed here because this table stores
-- attributed public content, not patient-level or partner raw records.

CREATE TABLE IF NOT EXISTS wildlifestats_bucket_02_firm_profile.orgs (
  id                           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  slug                         text NOT NULL,
  country_code                 text NOT NULL,
  region_code                  text,
  legal_name                   text,
  common_name                  text,
  primary_url                  text,
  harvest_status               text,
  extractor                    text,
  mission_statement            text,
  mission_statement_source_url text,
  leadership                   jsonb NOT NULL DEFAULT '[]'::jsonb,
  services_offered             jsonb NOT NULL DEFAULT '[]'::jsonb,
  accreditations               jsonb NOT NULL DEFAULT '[]'::jsonb,
  partnerships                 jsonb NOT NULL DEFAULT '[]'::jsonb,
  contact_info                 jsonb NOT NULL DEFAULT '{}'::jsonb,
  source_urls                  jsonb NOT NULL DEFAULT '[]'::jsonb,
  page_extracts                jsonb NOT NULL DEFAULT '[]'::jsonb,
  fetched_at                   timestamptz NOT NULL,
  source_url                   text NOT NULL,
  content_hash                 text NOT NULL,
  created_at                   timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT firm_profile_orgs_uniq UNIQUE (slug, fetched_at)
);

ALTER TABLE wildlifestats_bucket_02_firm_profile.orgs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS public_read_firm_profile_orgs
  ON wildlifestats_bucket_02_firm_profile.orgs;
CREATE POLICY public_read_firm_profile_orgs
  ON wildlifestats_bucket_02_firm_profile.orgs
  FOR SELECT TO anon, authenticated USING (true);

GRANT SELECT ON wildlifestats_bucket_02_firm_profile.orgs TO anon, authenticated;
GRANT ALL ON wildlifestats_bucket_02_firm_profile.orgs TO service_role;

CREATE INDEX IF NOT EXISTS firm_profile_orgs_slug_idx
  ON wildlifestats_bucket_02_firm_profile.orgs (slug, fetched_at DESC);
CREATE INDEX IF NOT EXISTS firm_profile_orgs_geo_idx
  ON wildlifestats_bucket_02_firm_profile.orgs (country_code, region_code, slug);

-- on_conflict key for supabase_client.upsert(): slug,fetched_at
