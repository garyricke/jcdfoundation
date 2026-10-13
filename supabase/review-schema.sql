-- JCD Foundation — application review tool storage
-- Run once in the Supabase SQL editor (Dashboard → SQL → New query → Run).
-- Safe to re-run: every statement is "if not exists".
--
-- Same security model as schema.sql: the Netlify Function (netlify/functions/
-- review.mjs) uses the service_role key, which bypasses RLS. RLS is enabled
-- with NO policies, so the anon/public key can't read or write anything here.
-- Applicant data is about minors — keep it that way.
--
-- Sample data: every sample row has is_sample = true (applications and
-- reviewers). Notes, recommendations, letters and flag overrides cascade from
-- their application, so the go-live cleanup is:
--
--   delete from public.review_applications where is_sample;
--   delete from public.review_reviewers    where is_sample;
--   delete from public.review_audit        where is_sample;

create extension if not exists "pgcrypto";

-- People who can use the tool. role: 'final' (Bob), 'admin' (Gary), 'reviewer'.
create table if not exists public.review_reviewers (
  id          text primary key,                -- short slug, e.g. 'bob'
  name        text not null,
  role        text not null check (role in ('final', 'admin', 'reviewer')),
  focus_area  text,                            -- a reviewer's home field, optional
  label       text,                            -- e.g. 'Nurse · Health Sciences'
  is_sample   boolean not null default false,
  created_at  timestamptz not null default now()
);

-- One row per submitted application. Key fields are columns (for filtering);
-- the complete submission is kept verbatim in `data`.
create table if not exists public.review_applications (
  id                   text primary key,       -- app_id from /apply, e.g. JCD-27-AB12CD
  submitted_at         timestamptz not null,
  first_name           text,
  last_name            text,
  email                text,
  phone                text,
  addr1                text,
  city                 text,
  zip                  text,
  school               text,
  homeschool_area      text,
  grad_date            text,
  focus_area           text,                   -- Health Sciences / Advanced Manufacturing / Building Trades
  profession           text,
  study_level          text,
  institution          text,
  annual_cost          numeric,
  data                 jsonb not null default '{}'::jsonb,
  transcript_received  boolean not null default false,
  cost_estimate_received boolean not null default false,
  urgent               boolean not null default false,
  urgent_note          text,
  ai_flag              text check (ai_flag in ('read_first', 'standard', 'human_look')),
  ai_reasons           jsonb not null default '[]'::jsonb,   -- [{ "reason": "...", "quote": "..." }]
  ai_model             text,                   -- which model + instructions version produced the flag
  final_decision       text check (final_decision in ('fund', 'fund_tier2', 'decline', 'hold')),
  award_amount         numeric,
  payee                text,                   -- institution or employer
  decided_by           text references public.review_reviewers(id),
  decided_at           timestamptz,
  is_sample            boolean not null default false,
  created_at           timestamptz not null default now()
);

-- Recommendation letters, matched to the application by its ID.
create table if not exists public.review_letters (
  id           uuid primary key default gen_random_uuid(),
  app_id       text not null references public.review_applications(id) on delete cascade,
  rec_name     text,
  rec_role     text,
  rec_org      text,
  body         text,
  received_at  timestamptz not null default now()
);

-- Each reviewer's own recommendation on an application (one per person).
create table if not exists public.review_recommendations (
  app_id          text not null references public.review_applications(id) on delete cascade,
  reviewer_id     text not null references public.review_reviewers(id) on delete cascade,
  recommendation  text not null check (recommendation in ('reviewed', 'tier1', 'tier2', 'decline')),
  updated_at      timestamptz not null default now(),
  primary key (app_id, reviewer_id)
);

-- Timestamped, signed reviewer notes.
create table if not exists public.review_notes (
  id           uuid primary key default gen_random_uuid(),
  app_id       text not null references public.review_applications(id) on delete cascade,
  reviewer_id  text not null references public.review_reviewers(id) on delete cascade,
  body         text not null,
  created_at   timestamptz not null default now()
);

-- "I disagree with the AI flag" — logged so the pilot can measure flag quality.
create table if not exists public.review_flag_overrides (
  id           uuid primary key default gen_random_uuid(),
  app_id       text not null references public.review_applications(id) on delete cascade,
  reviewer_id  text not null references public.review_reviewers(id) on delete cascade,
  reason       text,
  created_at   timestamptz not null default now()
);

-- Who changed what, when. Never updated or deleted by the tool.
create table if not exists public.review_audit (
  id          bigserial primary key,
  at          timestamptz not null default now(),
  actor       text,
  app_id      text,
  action      text not null,
  detail      jsonb not null default '{}'::jsonb,
  is_sample   boolean not null default false
);

-- Small key/value settings, e.g. the core/edge ZIP lists for distance tiers.
create table if not exists public.review_settings (
  key         text primary key,
  value       jsonb not null,
  updated_at  timestamptz not null default now()
);

create index if not exists review_apps_zip_idx      on public.review_applications (zip);
create index if not exists review_apps_school_idx   on public.review_applications (school);
create index if not exists review_apps_focus_idx    on public.review_applications (focus_area);
create index if not exists review_letters_app_idx   on public.review_letters (app_id);
create index if not exists review_notes_app_idx     on public.review_notes (app_id);
create index if not exists review_overrides_app_idx on public.review_flag_overrides (app_id);
create index if not exists review_audit_app_idx     on public.review_audit (app_id);

alter table public.review_reviewers       enable row level security;
alter table public.review_applications    enable row level security;
alter table public.review_letters         enable row level security;
alter table public.review_recommendations enable row level security;
alter table public.review_notes           enable row level security;
alter table public.review_flag_overrides  enable row level security;
alter table public.review_audit           enable row level security;
alter table public.review_settings        enable row level security;
