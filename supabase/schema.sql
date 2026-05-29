-- JCD Foundation — annotation/comment storage
-- Run once in the Supabase SQL editor (Dashboard → SQL → New query → Run).
-- The Netlify Function uses the service_role key, which bypasses RLS, so the
-- browser never touches these tables directly. RLS is enabled with NO public
-- policies, meaning the anon/public key cannot read or write them.

create extension if not exists "pgcrypto";

-- A highlight + its text-quote anchor.
create table if not exists public.annotations (
  id           uuid primary key default gen_random_uuid(),
  page         text not null,                 -- e.g. 'status', 'content-outline'
  quote        text not null,                 -- the highlighted text
  prefix       text,                          -- context before (for re-anchoring)
  suffix       text,                          -- context after
  start_offset integer,                       -- char offset fallback
  color        text default 'gold',
  author       text,
  created_at   timestamptz not null default now()
);

-- A message attached to a highlight. Flat thread (multiple comments per highlight).
create table if not exists public.comments (
  id            uuid primary key default gen_random_uuid(),
  annotation_id uuid not null references public.annotations(id) on delete cascade,
  author        text,
  body          text not null,
  created_at    timestamptz not null default now()
);

create index if not exists annotations_page_idx on public.annotations (page);
create index if not exists comments_annotation_idx on public.comments (annotation_id);

-- Lock both tables: only the service_role key (used by the Netlify Function)
-- can touch them. No anon/public policies are created on purpose.
alter table public.annotations enable row level security;
alter table public.comments    enable row level security;
