-- Ready Rooms v1 schema
-- Tables: profiles, intakes
-- Auth: magic link via Supabase Auth (auth.users)
-- Compliance posture: design-for-HIPAA
--   - No SSN stored
--   - DOB stored as year only (client_dob_year), not full date
--   - All sensitive fields protected by RLS
--   - Auditing deferred to v1.1

-- ============================================================================
-- profiles
-- ============================================================================
-- Extends auth.users with role + org context.
-- Auto-created via trigger on auth.users INSERT.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  full_name text,
  org_name text,
  role text not null default 'case_manager' check (role in ('admin', 'case_manager')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_profiles_role on public.profiles (role);

-- Auto-update updated_at
create or replace function public.touch_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_profiles_touch on public.profiles;
create trigger trg_profiles_touch
  before update on public.profiles
  for each row execute function public.touch_updated_at();

-- Auto-create profile when a user signs up via Supabase Auth
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email, full_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', '')
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists trg_on_auth_user_created on auth.users;
create trigger trg_on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ============================================================================
-- intakes
-- ============================================================================
-- Referral submissions from case managers.

create table if not exists public.intakes (
  id uuid primary key default gen_random_uuid(),
  case_manager_id uuid not null references auth.users(id) on delete restrict,

  -- Client identity (minimum necessary)
  client_first_name text not null,
  client_last_name text not null,
  client_dob_year integer check (client_dob_year between 1900 and 2100),
  client_phone text,
  client_email text,

  -- Referral source context
  referral_source_org text not null,
  referral_source_role text,

  -- Placement preferences
  preferred_city text not null,
  preferred_state text not null,
  urgency text not null default 'this_week' check (
    urgency in ('immediate', 'this_week', 'this_month', 'flexible')
  ),

  -- Funding
  funding_source text not null default 'other' check (
    funding_source in ('ssi', 'ssdi', 'va', 'medicaid', 'private_pay', 'nonprofit_sponsorship', 'other')
  ),
  monthly_income_cents integer check (monthly_income_cents >= 0),

  -- Triage
  housing_need text not null default 'triage_needed' check (
    housing_need in ('independent_shared', 'assisted_living', 'higher_support', 'triage_needed')
  ),

  notes text,

  status text not null default 'new' check (
    status in ('new', 'reviewing', 'matched', 'placed', 'closed')
  ),

  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_intakes_case_manager on public.intakes (case_manager_id);
create index if not exists idx_intakes_status on public.intakes (status);
create index if not exists idx_intakes_created_at on public.intakes (created_at desc);

drop trigger if exists trg_intakes_touch on public.intakes;
create trigger trg_intakes_touch
  before update on public.intakes
  for each row execute function public.touch_updated_at();

-- ============================================================================
-- RLS
-- ============================================================================

alter table public.profiles enable row level security;
alter table public.intakes enable row level security;

-- profiles: users can read + update their own row
drop policy if exists "profiles_self_read" on public.profiles;
create policy "profiles_self_read"
  on public.profiles for select
  using (auth.uid() = id);

drop policy if exists "profiles_self_update" on public.profiles;
create policy "profiles_self_update"
  on public.profiles for update
  using (auth.uid() = id);

-- profiles: admins can read all profiles
drop policy if exists "profiles_admin_read" on public.profiles;
create policy "profiles_admin_read"
  on public.profiles for select
  using (
    exists (
      select 1 from public.profiles p
      where p.id = auth.uid() and p.role = 'admin'
    )
  );

-- intakes: case managers can read/insert their own; case_manager_id auto-set via insert default check
drop policy if exists "intakes_self_read" on public.intakes;
create policy "intakes_self_read"
  on public.intakes for select
  using (case_manager_id = auth.uid());

drop policy if exists "intakes_self_insert" on public.intakes;
create policy "intakes_self_insert"
  on public.intakes for insert
  with check (case_manager_id = auth.uid());

-- intakes: admins can read + update all
drop policy if exists "intakes_admin_read" on public.intakes;
create policy "intakes_admin_read"
  on public.intakes for select
  using (
    exists (
      select 1 from public.profiles p
      where p.id = auth.uid() and p.role = 'admin'
    )
  );

drop policy if exists "intakes_admin_update" on public.intakes;
create policy "intakes_admin_update"
  on public.intakes for update
  using (
    exists (
      select 1 from public.profiles p
      where p.id = auth.uid() and p.role = 'admin'
    )
  );
