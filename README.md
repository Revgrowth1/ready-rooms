# Ready Rooms - Referral Source Discovery Pipeline

Automated pipeline for discovering, enriching, classifying, and scoring referral contacts at transitional housing organizations.

Finds case managers, discharge planners, housing navigators, and social workers at nonprofits, hospitals, treatment centers, shelters, and government agencies who can refer individuals with guaranteed income (SSI, SSDI, veterans benefits) to transitional and supportive housing.

## Pipeline

```
Step 1: Research orgs        (Serper - city + ZIP search)
Step 2: Discover contacts    (AI Ark - people at those orgs)
Step 3: Enrich email + phone (BlitzAPI + Prospeo + MillionVerifier, concurrent)
Step 4: Classify + score     (rule-based, 5 weighted dimensions)
Step 5: Dedup + export       (JSON + CSV + Google Sheets)
```

## Quick Start

```bash
# Install dependencies
pip install aiohttp requests python-dotenv

# Run full pipeline for Houston
python referral_discover.py houston

# Run a specific step
python referral_discover.py houston --step 3

# Resume from step 4
python referral_discover.py houston --from 4

# List available metros
python referral_discover.py --list-metros
```

## Required API Keys

Set these in `~/.env`:

| Key | Service | Purpose |
|-----|---------|---------|
| `SERPER_API_KEY` | Serper | Web search for org discovery |
| `AI_ARK_API_KEY` | AI Ark | People discovery by company |
| `BLITZ_API_KEY` | BlitzAPI | LinkedIn to email |
| `PROSPEO_API_KEY` | Prospeo | LinkedIn to mobile number |
| `MILLIONVERIFIER_API_KEY` | MillionVerifier | Email verification |

## Classification

Each contact is classified across:

- **16 referral categories** (parole/reentry, hospital discharge, behavioral health, veteran services, etc.)
- **14 contact roles** (discharge planner, housing navigator, case manager, program director, etc.)
- **8 target populations** (reentry, seniors with fixed income, homeless veterans, IDD clients, etc.)

## Scoring

5 weighted dimensions produce a priority tier:

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Referral Relevance | 30% | How likely the org sends housing referrals |
| Population Match | 25% | Overlap with target populations |
| Decision Maker | 25% | Whether this person makes placement decisions |
| Contactability | 15% | Data completeness (email, phone, LinkedIn) |
| Funding Influence | 5% | Ability to influence placement funding |

**Tier A** (70+) = highest-value referral contacts. **Tier B** (45-69) = strong leads. **Tier C** (<45) = low priority.

## Available Metros

- Houston, TX (97 ZIP codes)
- Dallas, TX
- Atlanta, GA

## Output

Each run creates a dated directory in `output/` with:

- `orgs.json` - discovered organizations
- `raw_contacts.json` - contacts with enrichment data
- `scored_contacts.json` - classified and scored
- `deduped_contacts.json` - final deduplicated set
- `contacts_export.csv` - flat CSV
- `referral_sources.json` - structured JSON export
- Google Sheet with 3 tabs (All Contacts, Priority Contacts, Organizations)

## Houston Test Results

| Metric | Result |
|--------|--------|
| Organizations | 211 |
| Contacts | 699 (after dedup) |
| Emails | 178 (25%), 113 verified |
| Phones | 266 (38%) |
| Pipeline time | 5.4 minutes |
