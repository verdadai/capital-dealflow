-- Capital Dealflow CRM schema
-- Demand side (opportunities) x supply side (providers) + matches

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TYPE sector_type AS ENUM (
  'oil_gas_upstream',
  'oil_gas_midstream',
  'mining',
  'power_renewables',
  'other_energy'
);

CREATE TYPE project_stage AS ENUM (
  'exploration',
  'pea',
  'pfs',
  'dfs',
  'construction',
  'producing',
  'acquisition_ad',
  'distress_dip',
  'unknown'
);

CREATE TYPE ask_type AS ENUM (
  'rbl',
  'project_debt',
  'senior_debt',
  'private_credit',
  'acquisition_finance',
  'equity',
  'royalty_streaming',
  'mezz',
  'unknown'
);

CREATE TYPE opportunity_status AS ENUM (
  'new',
  'researching',
  'teaser_requested',
  'under_nda',
  'mandated',
  'marketing',
  'term_sheet',
  'closed',
  'dead',
  'pass'
);

CREATE TYPE provider_capital_type AS ENUM (
  'bank_rbl',
  'bank_project_finance',
  'bank_abl',
  'private_credit',
  'pe_equity',
  'royalty_streaming',
  'family_office',
  'offtake_trader',
  'special_situations',
  'other'
);

CREATE TYPE warmth_level AS ENUM ('cold', 'warm', 'mandated');
CREATE TYPE package_readiness AS ENUM (
  'signal_only',
  'teaser',
  'partial_package',
  'lender_ready'
);
CREATE TYPE broker_friendly AS ENUM ('yes', 'unknown', 'no');
CREATE TYPE verification_status AS ENUM (
  'unverified',
  'desk_confirmed',
  'docs_on_file',
  'counsel_cleared',
  'blocked'
);
CREATE TYPE match_status AS ENUM (
  'suggested',
  'queued',
  'contacted',
  'interested',
  'passed',
  'term_sheet',
  'won'
);

CREATE TABLE companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  website TEXT,
  ticker TEXT,
  cik TEXT,
  jurisdiction TEXT,
  hq_location TEXT,
  sector sector_type,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX companies_cik_uidx ON companies (cik) WHERE cik IS NOT NULL;
CREATE INDEX companies_ticker_idx ON companies (ticker);

CREATE TABLE opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID REFERENCES companies(id) ON DELETE SET NULL,
  project_name TEXT,
  sector sector_type NOT NULL DEFAULT 'other_energy',
  stage project_stage NOT NULL DEFAULT 'unknown',
  ask_type ask_type NOT NULL DEFAULT 'unknown',
  ask_amount_min_usd NUMERIC(18,2),
  ask_amount_max_usd NUMERIC(18,2),
  commodity TEXT,
  geography TEXT,
  status opportunity_status NOT NULL DEFAULT 'new',
  warmth warmth_level NOT NULL DEFAULT 'cold',
  package_readiness package_readiness NOT NULL DEFAULT 'signal_only',
  confidence NUMERIC(4,3) NOT NULL DEFAULT 0.50 CHECK (confidence >= 0 AND confidence <= 1),
  summary TEXT,
  source TEXT,
  source_url TEXT,
  source_filing_accession TEXT,
  signal_keywords TEXT[],
  needs_bd_license BOOLEAN NOT NULL DEFAULT FALSE,
  engagement_fee_pct NUMERIC(6,4),
  next_action TEXT,
  next_action_due DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX opportunities_status_idx ON opportunities (status);
CREATE INDEX opportunities_sector_stage_idx ON opportunities (sector, stage);
CREATE INDEX opportunities_ask_type_idx ON opportunities (ask_type);
CREATE INDEX opportunities_created_idx ON opportunities (created_at DESC);

CREATE TABLE providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  firm_name TEXT NOT NULL,
  desk_name TEXT,
  capital_type provider_capital_type NOT NULL,
  check_size_min_usd NUMERIC(18,2),
  check_size_max_usd NUMERIC(18,2),
  sectors sector_type[] NOT NULL DEFAULT '{}',
  stages project_stage[] NOT NULL DEFAULT '{}',
  geographies TEXT[] NOT NULL DEFAULT '{}',
  broker_friendly broker_friendly NOT NULL DEFAULT 'unknown',
  broker_friendly_verification verification_status NOT NULL DEFAULT 'unverified',
  investor_category TEXT,           -- institutional, accredited, etc.
  accreditation_status verification_status NOT NULL DEFAULT 'unverified',
  kyc_status verification_status NOT NULL DEFAULT 'unverified',
  website TEXT,
  notes TEXT,
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX providers_capital_type_idx ON providers (capital_type);
CREATE INDEX providers_active_idx ON providers (active);

CREATE TABLE provider_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  title TEXT,
  email TEXT,
  linkedin_url TEXT,
  phone TEXT,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX provider_contacts_provider_idx ON provider_contacts (provider_id);

CREATE TABLE provider_deals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
  deal_name TEXT,
  sector sector_type,
  stage project_stage,
  amount_usd NUMERIC(18,2),
  role TEXT,
  closed_on DATE,
  source_url TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  opportunity_id UUID NOT NULL REFERENCES opportunities(id) ON DELETE CASCADE,
  provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
  score NUMERIC(6,3) NOT NULL DEFAULT 0,
  reasons TEXT[] NOT NULL DEFAULT '{}',
  status match_status NOT NULL DEFAULT 'suggested',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (opportunity_id, provider_id)
);

CREATE INDEX matches_opportunity_score_idx ON matches (opportunity_id, score DESC);

CREATE TABLE interactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  opportunity_id UUID REFERENCES opportunities(id) ON DELETE SET NULL,
  provider_id UUID REFERENCES providers(id) ON DELETE SET NULL,
  contact_id UUID REFERENCES provider_contacts(id) ON DELETE SET NULL,
  channel TEXT,
  direction TEXT,
  subject TEXT,
  body TEXT,
  interacted_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE signals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL DEFAULT 'edgar',
  external_id TEXT,
  company_name TEXT,
  cik TEXT,
  ticker TEXT,
  form_type TEXT,
  filed_at TIMESTAMPTZ,
  title TEXT,
  snippet TEXT,
  filing_url TEXT,
  keywords_hit TEXT[] NOT NULL DEFAULT '{}',
  sector_guess sector_type,
  stage_guess project_stage,
  ask_type_guess ask_type,
  score NUMERIC(6,3) NOT NULL DEFAULT 0,
  promoted_opportunity_id UUID REFERENCES opportunities(id) ON DELETE SET NULL,
  raw_json JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (source, external_id)
);

CREATE INDEX signals_score_idx ON signals (score DESC, created_at DESC);
CREATE INDEX signals_unpromoted_idx ON signals (created_at DESC)
  WHERE promoted_opportunity_id IS NULL;
