# Ready Rooms — Full System Architecture & Roadmap

**Date:** 2026-04-24
**Status:** Strategic blueprint. Builds on the v1 web app shipped tonight.
**Audience:** Adam (decision-maker), Yusuf (implementer), future hires

---

## 0. The Honest Picture

We shipped a working v1 tonight: landing page → magic link auth → professional referral form → admin list. That is **roughly 5% of the platform** described in your spec. The other 95% is what makes Ready Rooms a defensible business instead of a contact form.

This doc maps that 95% in three layers:
1. **The full funnel** — six stages, what we have, what leaks
2. **The backend** — twelve services that need to exist for the platform to actually work
3. **The commercial architecture** — how this becomes a sustainable business, not a side project

Every section closes with what to build, in order. The roadmap at the end (§5) sequences the builds across v1.1 → v3 over the next 12 months.

---

## 1. The Full Funnel

A housing placement is a multi-week journey. The platform either supports the full journey or it leaks customers at every stage. Most "platforms" in this space are a form + email — they collapse the funnel into a single black box and lose 60-80% of referrals before placement.

```
AWARENESS  →  INTEREST  →  QUALIFICATION  →  MATCHING  →  CONVERSION  →  RETENTION
   (find)     (capture)      (triage)         (top 3)      (place)      (keep housed)
```

### 1.1 Awareness — How they find Ready Rooms

| Channel | Status | Notes |
|---|---|---|
| Outbound to referral pros | ✅ HAVE (Phase 0 Python pipeline) | Discharge planners, case managers, social workers — finds them, enriches, ready for cold email |
| Cold email engine | ✅ HAVE (Adam's EmailBison infra) | Same one that powers RevGrowth client work — repurpose for Ready Rooms outbound |
| Direct partnerships | ❌ MISSING | Hospital MOUs, treatment center agreements, parole/probation referral channels |
| SEO content | ❌ MISSING | City-specific landing pages: "transitional housing in Houston", "shared housing for veterans Phoenix" — long-tail intent |
| Print/community | ❌ MISSING | Flyers in clinics, courts, shelters, VA centers — physical presence in the workflow |
| Paid (later) | ❌ DEFER | Google Ads on housing-help intent keywords; Meta to families |

**Build next:** Reuse the Phase 0 pipeline + EmailBison stack for outbound to discharge planners. That's the fastest demand-side ramp because the muscle already exists.

### 1.2 Interest — Two front doors (per spec)

| Door | Status | Notes |
|---|---|---|
| Professional referral (case manager) | ✅ HAVE | `/refer` form, auth-gated |
| Self-referral (individual/family) | ⚠️ STUB | `/get-help` page with email contact only — full form deferred to v1.1 |
| Phone-first option | ❌ MISSING | Many users won't fill forms — need a tracked phone number with voicemail-to-text |
| SMS-first option | ❌ MISSING | "Text 'HOUSING' to XXXX" — lowest-friction entry, especially for vulnerable populations |
| Live chat / AI assistant | ❌ DEFER | Smart triage assistant could pre-qualify before human handoff |

**Build next:** Real self-referral form with simpler language + fewer fields + the option to skip and request a callback. Then SMS shortcode in v2.

### 1.3 Qualification — Triage before matching

This is where most platforms fail. A bad placement is worse than no placement.

| Capability | Status | Notes |
|---|---|---|
| Intake captured | ✅ HAVE | Saves to `intakes` table |
| Triage rules engine | ❌ MISSING | Currently `housing_need` defaults to `triage_needed`; no automatic sorting |
| Risk flagging | ❌ MISSING | Sex offender restrictions, behavioral history, medical complexity — must surface before matching |
| Funding eligibility quick-check | ❌ MISSING | Auto-detect "likely SSDI eligible but not yet enrolled" — turns into a funding workflow ticket |
| Specialist review queue | ⚠️ PARTIAL | Admin can see intakes in `/admin` but no review workflow (claim, comment, escalate) |

**Build next:** Triage rules engine (rule-based, ~30 rules). Sorts every new intake into one of 4 buckets: independent_shared, assisted_living, higher_support, emergency_stabilization. Manual override always available.

### 1.4 Matching — Top 3, not 50

| Capability | Status | Notes |
|---|---|---|
| Housing inventory database | ❌ MISSING | The actual homes! Each home: location, capacity, supported populations, funding accepted, vacancy, photos, video tour, house rules, accessibility |
| Match algorithm v1 | ❌ MISSING | Rule-based scoring on geography, population fit, funding overlap, behavioral fit, accessibility. Top 3 returned. |
| Match presentation | ❌ MISSING | Card layout: photo, fit reasons, funding match, move-in window, who it's best for, who it might not fit, next action |
| Provider notification | ❌ MISSING | Housing operator gets a "you have a referral" SMS/email when they're in the top 3 |

**Build next:** Housing inventory CRUD (admin-managed in v1.5, provider-self-managed in v2). Then a dumb scoring algorithm (population + geography + funding) before anything fancier.

### 1.5 Conversion — Match to placement

| Capability | Status | Notes |
|---|---|---|
| Tour/interview scheduling | ❌ MISSING | Calendly-style booking inside the platform; provider availability synced |
| Acceptance/rejection workflow | ❌ MISSING | Resident accepts → triggers move-in coord; rejects → next match offered |
| Move-in coordination | ❌ MISSING | Document checklist, transport arranged, first-night essentials, intake-to-resident handoff |
| Funding paperwork module | ❌ MISSING | SSI/SSDI/VA application status tracker, deadlines, document upload, approval workflow |

**Build next:** Lightweight acceptance flow first (just a button + status change + email to provider). Tour scheduling and funding are v2.

### 1.6 Retention — The actual moat

This is what separates Ready Rooms from "just a referral service." Tracking outcomes turns into impact reporting → grant funding → defensible position.

| Capability | Status | Notes |
|---|---|---|
| Stability tracking | ❌ MISSING | ID obtained, benefits active, healthcare connected, transportation, employment readiness |
| Check-in cadence | ❌ MISSING | 7-day, 30-day, 60-day, 90-day automated check-ins (SMS + human escalation) |
| Outcomes reporting | ❌ MISSING | Housed within 24/48/72h, 30/60/90-day retention, readmission/recidivism rate |
| Funder-grade impact reports | ❌ MISSING | PDF/dashboard for grants, hospital partners, government contracts |

**Build next:** Status timestamps in v1.5 (when did we hit "matched"? "placed"?). Real retention layer in v2-v3.

### Funnel leakage estimate (industry baseline)

If we built the full funnel, target conversion at each stage (assuming healthy partnerships + decent matching):
- Awareness → Interest: ~5-10% of contacted referral pros submit at least one referral within 60 days
- Interest → Qualification: ~85% (some intakes are incomplete or duplicates)
- Qualification → Matching: ~70% (some need higher-care referrals, not our placement)
- Matching → Conversion: ~50-60% (resident accepts, funding approves, move-in happens)
- Conversion → 30-day retention: ~80-85% (good triage + good provider = sticky placement)

**A platform that doesn't track these is operating blind.** The metrics layer (§2.4) is non-optional.

---

## 2. Backend Infrastructure (12+ services)

The web app is 1 of 12 services. Here's the rest, grouped by layer.

### 2.1 Data layer

| Service | Status | Tech | Notes |
|---|---|---|---|
| Postgres | ✅ HAVE | Supabase | Single source of truth |
| Auth | ✅ HAVE | Supabase magic link | Upgrade to Google OAuth in v1.1 for case-manager UX |
| File storage | ❌ MISSING | Supabase Storage or S3 + signed URLs | For ID docs, funding paperwork, house photos |
| Audit log | ❌ MISSING | Postgres trigger + queryable view | HIPAA requires it; today every UPDATE silently overwrites |
| Encryption (app-layer) | ❌ MISSING | libsodium / pgcrypto for `notes` field | Defense in depth beyond Supabase defaults |

### 2.2 Communication layer

| Service | Status | Tech | Notes |
|---|---|---|---|
| Transactional email | ⚠️ PARTIAL | Supabase email today; switch to Resend in v1.1 | Magic link works; need confirm-email + match-notification + check-in templates |
| SMS | ❌ MISSING | Twilio | "Your match is ready" + reminders + the SMS-first intake door |
| Inbound phone | ❌ MISSING | Twilio Voice + transcription | Tracked phone number → voicemail-to-text → intake |
| Voice AI (later) | ❌ DEFER | Vapi or Retell | Spec mentions AI call agent — v3 |
| Slack notifications | ❌ MISSING | Slack webhooks | Staff alerts: new intake, urgent intake, match accepted, retention risk |

### 2.3 Operations layer

| Service | Status | Tech | Notes |
|---|---|---|---|
| Internal CRM | ⚠️ PARTIAL | Custom on Supabase (current admin dashboard) | Need richer: queue management, claim/assign, comments, attachments, status history |
| Provider portal | ❌ MISSING | Same Next.js app, separate role | Housing operators self-manage their inventory: photos, vacancy, rules, eligibility |
| Funding workflow | ❌ MISSING | New Supabase tables + UI module | Per intake: funding sources tagged, app status, deadlines, doc uploads |
| Document review queue | ❌ MISSING | UI on Supabase Storage records | Intake docs, funding paperwork, ID, signed agreements — admin reviews |
| Background jobs | ❌ MISSING | Supabase pg_cron + Resend/Twilio for scheduled sends | Daily retention check-ins, weekly funder reports, SMS reminders |

### 2.4 Intelligence layer

| Service | Status | Tech | Notes |
|---|---|---|---|
| Match scoring engine | ❌ MISSING | Postgres function or Python service | Inputs: intake + housing_units; output: ranked top 3 with score breakdown |
| Triage rules engine | ❌ MISSING | Postgres function or Python service | Same pattern — rules are auditable + overridable |
| Funnel analytics | ❌ MISSING | dbt + a dashboard (Metabase / Hex) | Conversion at each funnel stage, by city, by referral source, by funding type |
| Outcomes/impact reporting | ❌ MISSING | PDF generation (puppeteer or react-pdf) | For grants, hospital partners, government contracts. Defensible asset. |

### 2.5 Acquisition layer (already partially built)

| Service | Status | Tech | Notes |
|---|---|---|---|
| Phase 0 referral discovery | ✅ HAVE | Python pipeline at repo root | Finds discharge planners + case managers via Serper/AI Ark/BlitzAPI/Prospeo/MillionVerifier |
| Outbound email engine | ✅ HAVE | EmailBison (Adam's existing infra) | Reuse for Ready Rooms — own workspace, own senders, own domain |
| Inbound SEO / content | ❌ MISSING | Next.js MDX pages + sitemap | City-specific landing pages, "guide to" content for SEO |
| Partnership tracking | ❌ MISSING | Attio CRM (Adam already uses it) or Supabase view | Hospital systems, treatment centers, government contacts in pipeline |

### 2.6 Compliance posture

This is the moat. Done well, it locks out lighter competitors. Done poorly, it kills the company.

| Requirement | Status | Notes |
|---|---|---|
| Minimum-necessary data collection | ✅ DESIGNED | No SSN; year of birth only |
| RLS on every table | ✅ HAVE | Enforced in v1 schema |
| BAA with Supabase | ❌ NEEDED | Required before any PHI flows; Supabase offers BAA on Pro/Enterprise |
| BAA with Vercel | ❌ NEEDED | Same logic |
| BAA with Twilio + Resend | ❌ NEEDED | When SMS/email lands |
| Audit log | ❌ MISSING | HIPAA Security Rule §164.312(b) |
| 42 CFR Part 2 (SUD) | ⚠️ DESIGN-AWARE | If we touch SUD records: separate encryption + restricted-access workflow |
| ADA / WCAG 2.1 AA | ⚠️ PARTIAL | Tailwind components are accessible by default; need axe DevTools audit before public |
| Tracking pixels banned on PHI pages | ✅ POLICY | No GA, no Hotjar; Vercel Analytics only (privacy-first) |
| State-level housing regs | ❌ UNCHECKED | CA, IL, NY, TX have additional housing/benefits privacy rules |

---

## 3. Commercial Architecture

The platform is 50% of the company. The other 50% is the business model that pays for it.

### 3.1 Revenue model — pick one, design around it

| Model | Pros | Cons | Best for |
|---|---|---|---|
| **Per-placement fee from housing operators** ($X per successful placement) | Aligns revenue with outcome; operators happy to pay for filled beds | Requires lots of operators on platform; long sales cycle to operators | Marketplace path. Most defensible if we own demand. |
| **Subscription from hospital systems / discharge teams** ($Y/year for unlimited referrals + reporting) | Predictable revenue; institutional sales motion | Long enterprise sales cycles; need hospital decision-maker access | Enterprise SaaS path. Higher contract value. |
| **Government contracts** (state/county housing agencies, parole/probation departments) | Mission-aligned; large multi-year contracts | RFP-driven; slow to win first one; political | Public-sector path. Recurring + defensible. |
| **Grant funding** (foundations, federal HUD/SAMHSA grants) | Mission supports it (.org domain, vulnerable population, outcome-driven) | Episodic; not a real moat alone | Hybrid revenue layer. Pairs well with #1 or #2. |

**Recommendation:** Start hybrid: per-placement fee + grants. Per-placement validates economic value; grants buy runway. Revisit subscription path after first 100 placements.

**The unanswered question that shapes everything:** What's the per-placement price target? $150? $500? $1500? That number drives the unit economics, the operator outreach script, the funding sources we'd partner with.

### 3.2 Supply-side strategy (housing operators)

Without operators, no inventory. Without inventory, no matches. Without matches, no platform.

- **City-by-city ramp** — pick 3 metros (Houston, Phoenix, Atlanta? — high SSI/SSDI density + low housing cost) and saturate operator coverage in each before expanding
- **Free for operators** — they earn from placements, no upfront fee; possibly the per-placement fee comes off their first-month rent collected
- **Quality bar** — vetting visit (in-person or video), required photos/video tour, signed house rules, reference check
- **Operator portal** — self-serve inventory management; reduces our ops cost as we scale
- **Operator outbound** — a Phase-0-style pipeline finds independent living + transitional housing operators by city; cold email + phone outreach

### 3.3 Demand-side strategy (referral pros)

This is where Phase 0 + EmailBison shine. We already have the muscle.

- **Hospital discharge planners** — biggest single source; pipeline already finds them
- **Reentry coordinators** — parole/probation departments; underserved channel
- **VA SSVF program offices** — veterans-specific; mission-aligned, easier "yes"
- **Treatment center discharge staff** — recovery population; aligns with sober living operators
- **Faith-based outreach** — large network, often unsophisticated tooling — Ready Rooms looks magical

**The play:** Pipeline produces 500-1000 referral pros/month per metro → outbound 100-200/week → expect 5-10% to submit at least one referral within 60 days → 20-40 active referrers per metro after 60 days → 100+ intakes/month per metro at maturity.

### 3.4 Compliance moat

Most "housing platforms" today are spreadsheets + Facebook groups. They can't touch HIPAA-protected referrals. Our compliance work isn't a tax — it's the wedge that locks us in with hospitals + government partners.

The order: BAAs first → audit log second → SOC 2 in v3 (12-18 months out, gates enterprise contracts).

---

## 4. Phased Roadmap

Sequence matters. Each phase unlocks the next.

### v1 (TONIGHT — SHIPPED) ✅
- Landing page (brand-aligned, two-doors UX)
- Magic link auth
- Professional referral form
- Admin list + status update
- /get-help stub for self-referral path
- Live: https://web-woad-seven-99.vercel.app

### v1.1 (this week — Yusuf) — Operational maturity
- [ ] Real self-referral form at `/get-help` (simpler than `/refer`, no auth required, writes to same `intakes` table with `case_manager_id` = system user OR new `self_intakes` table)
- [ ] Email confirmation on intake submit (Resend, BAA signed)
- [ ] Triage rules engine v0 (5-10 hardcoded rules; auto-set `housing_need`)
- [ ] Audit log table + Postgres trigger on `intakes` UPDATE
- [ ] Sign Supabase BAA (Pro plan) + Vercel BAA + Resend BAA

### v1.5 (next 2 weeks) — Match loop closes
- [ ] Housing inventory CRUD (admin-managed, single `housing_units` table per spec)
- [ ] Match scoring engine v1 (rule-based: geography + population + funding)
- [ ] Match recommendation panel on `/admin/[id]` (top 3 housing units displayed with score breakdown + "match" button)
- [ ] `matches` table + status history
- [ ] Provider notification when matched (email)
- [ ] Document upload (intake docs + ID + funding paperwork) via Supabase Storage with signed URLs

### v2 (next month) — Commercial-ready
- [ ] Provider portal (housing operators self-serve their inventory)
- [ ] Funding workflow module (per-intake funding source tracking + app status + deadlines)
- [ ] Tour/interview scheduling (Calendly-style)
- [ ] Acceptance/rejection flow with status state machine
- [ ] Twilio SMS notifications (intake confirmation + match-ready + reminders)
- [ ] Public marketing pages: `/for-hospitals`, `/for-veterans`, `/for-housing-providers`, `/about`, `/impact`, `/faq`
- [ ] Funnel analytics dashboard (Metabase or Hex pointed at Supabase) — even basic conversion-by-stage view
- [ ] First city launch: pick metro, recruit operators, ramp outbound to referral pros

### v2.5 (month 2-3) — Retention layer
- [ ] Stability tracking module (ID, benefits, healthcare, transportation status per resident)
- [ ] Automated check-in cadence (7d/30d/60d/90d via SMS + email)
- [ ] Retention risk flagging (auto-flag if stability score drops)
- [ ] Outcomes reporting v1 (housed within 24/48/72h, 30/60/90-day retention, by city/source)

### v3 (next quarter+) — Scale & defense
- [ ] AI intake assistant (chat that pre-qualifies before human handoff)
- [ ] AI voice agent (call to refer, transcription → intake)
- [ ] Cross-state expansion playbook (replicating city-by-city ramp)
- [ ] Funder/grant reporting module (PDF impact reports, dashboards for partners)
- [ ] Mobile PWA (case managers in the field)
- [ ] Hospital EHR integration (Epic, Cerner) for direct discharge referrals — gates enterprise revenue
- [ ] SOC 2 audit (gates enterprise contracts)

---

## 5. What Yusuf Should Build Next (Strict Priority)

Sequenced for **maximum learning velocity** — each builds on the last and produces a testable signal.

1. **Self-referral form at `/get-help`** (1-2 days)
   - Validates demand from individuals/families
   - Simpler than `/refer` (5-7 fields vs 12-15), no auth required
   - Writes to `intakes` table with a `source` column: `'professional' | 'self'`
   - Case manager and self-referral show distinctly in admin

2. **Email confirmation on intake** (half day, requires Resend account + BAA)
   - Submitter gets "we received your referral, here's what happens next"
   - Sets the operational tone — this is the difference between "form" and "service"

3. **Housing inventory CRUD** (2-3 days)
   - Admin can add/edit housing units with all the spec fields (location, capacity, populations supported, funding accepted, vacancy date, photos, rules)
   - Without this, we can't ever return real matches

4. **Match recommendation panel** (1-2 days)
   - On `/admin/[id]`, show top 3 housing_units sorted by simple score
   - Admin clicks "Match" → writes to a new `matches` table
   - Closes the loop end-to-end (intake → match → status update)

5. **Status state machine + history log** (1-2 days)
   - Replace freeform status dropdown with a proper state machine
   - History table records every transition (who, when, from, to, optional comment)
   - This is the foundation for retention analytics

After this 5-step sprint (1-2 weeks), Adam decides v2 priority based on what's working. The sprint closes the loop end-to-end and gives us the first real data on conversion rates.

---

## 6. Open Questions for Adam

Locking these answers shapes the rest:

1. **Revenue model commitment** — per-placement fee, hospital subscription, government contracts, grants, or hybrid? Drives unit economics and outreach script.
2. **Per-placement price target** — $150? $500? $1500? Drives operator economics and our take rate.
3. **Geographic scope** — which 3 metros first? (Recommend: high SSI/SSDI density + low housing cost — Houston, Phoenix, Atlanta as defaults.)
4. **Compliance budget** — when do we sign Supabase Pro + BAAs? When does SOC 2 happen?
5. **Day-1 ops team** — who reviews intakes when the first one arrives? You? A part-time hire? Outsourced (Filipino offshore SDR pattern)?
6. **Phase 0 + web app integration** — when an outbound referral pro replies "interested", do they get auto-invited to the web platform with a magic link? (Recommend yes — closes the loop.)
7. **Brand: nonprofit positioning vs for-profit** — `.org` domain implies nonprofit. Are we incorporating as 501(c)(3) (unlocks foundation grants, federal funding) or LLC (faster, more flexible)?

---

## 7. The One-Line Strategic Bet

**Ready Rooms wins by being the only HIPAA-grade, outcome-tracking, multi-sided platform in transitional housing — owning both the referral pipeline AND the operator inventory in 3-5 metros within 12 months.**

Everything else is execution.
