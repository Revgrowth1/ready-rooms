# Ready Rooms — Web App (v1)

Housing placement and matching platform. Not a listings marketplace.

This is the v1 baseline. It demonstrates the end-to-end flow: case manager signs in → submits referral → admin sees it and updates status. Built so Yusuf can extend confidently.

## Stack

- Next.js 16 (App Router) + TypeScript + Tailwind v4
- Supabase (Postgres + Auth via magic link, RLS-enforced multi-tenant)
- Vercel deploy (subdirectory build from `apps/web`)

## Repo layout

```
ready-rooms/
├── apps/web/              <- you are here
├── 1_research.py ...      <- Phase 0 referral discovery pipeline (untouched)
└── docs/plans/            <- design docs
```

## What's in v1

| Route | Purpose |
|-------|---------|
| `/` | Landing - explains what Ready Rooms is + CTAs to refer or sign in |
| `/login` | Magic link sign-in |
| `/auth/callback` | Supabase auth callback |
| `/refer` | Case manager intake form (8-12 fields, 3 sections) |
| `/refer/success` | Confirmation page |
| `/admin` | Admin-only list of referrals |
| `/admin/[id]` | Admin-only intake detail + status update |

Tables: `profiles` (auth.users extension with role), `intakes`. RLS gates everything.

## What's deferred to v1.1+

- Housing inventory CRUD
- Matching algorithm (rule-based, top 3) + match recommendation panel
- Case status state machine with transitions + history log
- Self-referral flow (currently auth-gated for case managers only)
- SMS notifications (currently email confirmation only via Supabase)
- AI intake assistant / call agent
- Funding workflow module
- Resident stability/retention layer
- HIPAA formal certification (BAAs, app-level encryption, audit log)

## Setup

### 1. Create a Supabase project

1. Go to https://supabase.com/dashboard
2. Create a new project (name suggestion: `ready-rooms-prod`, region: `us-east-1`)
3. Wait for provisioning
4. Settings → API → copy `Project URL` + `anon public` key + `service_role` key

### 2. Apply the schema

In Supabase dashboard → SQL Editor → New query → paste the contents of `supabase/migrations/20260424000000_v1_schema.sql` → Run.

This creates `profiles` + `intakes`, enables RLS, and wires up the auto-create-profile-on-signup trigger.

### 3. Enable email auth

Supabase dashboard → Authentication → Providers → Email → make sure it's enabled.

For magic link to work in production:
- Authentication → URL Configuration → Site URL = your Vercel URL
- Authentication → URL Configuration → Redirect URLs add: `https://YOUR-DOMAIN.vercel.app/auth/callback`

### 4. Local dev

```bash
cd apps/web
cp .env.local.example .env.local
# fill in NEXT_PUBLIC_SUPABASE_URL + NEXT_PUBLIC_SUPABASE_ANON_KEY + SUPABASE_SERVICE_ROLE_KEY
npm install
npm run dev
# open http://localhost:3000
```

### 5. Promote your first admin

After signing in once via magic link, your row exists in `profiles` with role = `case_manager`. To upgrade yourself to admin, in Supabase SQL Editor:

```sql
update public.profiles set role = 'admin' where email = 'you@yourorg.com';
```

Then refresh the app. `/admin` is now accessible.

### 6. Deploy to Vercel

From the `apps/web` directory:

```bash
vercel --yes --prod
```

If asked to link to a project, create a new one named `ready-rooms-web`. Vercel will detect Next.js automatically.

In the Vercel dashboard → Project Settings → Environment Variables, add:
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

Redeploy. Update Supabase Auth URL Configuration with the production URL + `/auth/callback`.

## Compliance posture (design-for-HIPAA, defer formal cert)

What we already do:
- No SSN stored anywhere. Year of birth only (`client_dob_year`), not full DOB.
- RLS on every table - case managers can only see their own intakes.
- All sensitive fields encrypted at rest via Supabase defaults.
- No tracking pixels (no GA, no Hotjar, no Pixel). Vercel Analytics only - and even that is opt-in for v1.1.
- No clinical or substance-use detail in form (notes field warns users).

What's still required for HIPAA cert (v1.x):
- Business Associate Agreement (BAA) with Supabase + Vercel.
- Application-layer encryption for the `notes` field if it contains PHI.
- Audit log table (every UPDATE on `intakes` logs who, what, when, before/after).
- Annual security review + employee training documentation.

## Design decisions worth knowing

- **Server Actions** for form submissions, not REST API routes. Cleaner with App Router + Tailwind 4.
- **Magic link** auth for v0.1. Faster path to working product than OAuth setup. Switch to Google OAuth in v1.1 for case-manager UX.
- **Triage-first** in the schema (`housing_need` defaults to `triage_needed`). Reflects the product principle: don't assume independent shared housing fit until a human reviews.
- **No housing inventory in v1** - matching is a manual review step. v1.1 adds the inventory + rule-based match recommendation panel.

## Next things to build (Yusuf, in order)

1. **Housing inventory CRUD** - admin can create/update housing units with location, capacity, supported populations, funding accepted, vacancy date. Single table `housing_units` + admin pages at `/admin/housing`.
2. **Match recommendation panel** - on `/admin/[id]`, show top 3 housing_units sorted by rule-based score (population match + geography + funding overlap). Admin clicks "Match" → writes to a new `matches` table.
3. **Case status state machine** - replace the freeform status dropdown with a state machine: New → Reviewing → Matched → Offer Sent → Accepted/Declined → Move-in Pending → Placed → Closed. History table.
4. **Email confirmations** - on intake submit, send case manager a confirmation email via Supabase email or Resend. On match, send case manager + housing operator notification.
5. **Self-referral flow** - public form at `/get-help` for individuals/family, simpler language, fewer fields, "need help filling this out" assistance.

## Known issues / nice-to-fixes

- Tailwind v4 deprecated some utilities - if you see lint warnings, prefer the new ones.
- `middleware.ts` should rename to `proxy.ts` per Next.js 16 deprecation. Keeping `middleware` for now since it still works.
- No loading states / pending UI on form submissions yet - `useFormStatus` would polish this.
- No empty/error states on `/admin` for the network-failure path (only "no intakes" empty state).
- Profile `org_name` is captured in schema but no UI to edit it yet.
