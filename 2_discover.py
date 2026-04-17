#!/usr/bin/env python3
"""Step 2: Discover contacts at target organizations via AI Ark."""

import json
import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.config import AI_ARK_API_KEY, AI_ARK_BASE, get_metro, get_output_dir
from lib.taxonomy import RELEVANT_TITLE_KEYWORDS


def ai_ark_search(company_names, seniority_levels):
    """Search AI Ark for people at specified companies.

    CRITICAL: AI Ark uses nested payload structure.
    - STRICT mode does NOT filter by geography - must filter client-side.
    """
    headers = {"X-TOKEN": AI_ARK_API_KEY, "Content-Type": "application/json"}
    payload = {
        "page": 0,
        "size": 100,
        "account": {
            "name": {
                "any": {
                    "include": {"mode": "STRICT", "content": company_names}
                }
            }
        },
        "contact": {
            "seniority": {
                "any": {
                    "include": seniority_levels
                }
            }
        },
    }

    all_people = []
    try:
        resp = requests.post(
            f"{AI_ARK_BASE}/people", headers=headers, json=payload, timeout=30
        )
        if resp.status_code == 200:
            data = resp.json()
            all_people = data.get("content", [])
            total_pages = data.get("totalPages", 1)
            # Fetch additional pages (up to 5)
            for page in range(1, min(total_pages, 5)):
                time.sleep(0.3)
                payload["page"] = page
                r2 = requests.post(
                    f"{AI_ARK_BASE}/people", headers=headers, json=payload, timeout=30
                )
                if r2.status_code == 200:
                    all_people.extend(r2.json().get("content", []))
            return data.get("totalElements", 0), all_people
        elif resp.status_code == 429:
            print("  Rate limited, waiting 30s...")
            time.sleep(30)
        else:
            print(f"  AI Ark error {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"  AI Ark exception: {e}")
    return 0, []


def extract_person(person, org_type):
    """Extract clean person data from AI Ark response."""
    profile = person.get("profile", {})
    link = person.get("link", {})
    location = person.get("location", {})
    company = person.get("company", {}).get("summary", {})
    department = person.get("department", {})
    return {
        "first_name": profile.get("first_name", ""),
        "last_name": profile.get("last_name", ""),
        "full_name": profile.get("full_name", ""),
        "title": profile.get("title", "") or profile.get("headline", ""),
        "headline": profile.get("headline", ""),
        "company_name": company.get("name", ""),
        "linkedin_url": link.get("linkedin", ""),
        "city": location.get("city", ""),
        "state": location.get("state", ""),
        "seniority": department.get("seniority", ""),
        "departments": ", ".join(department.get("departments", []) or []),
        "sub_departments": ", ".join(department.get("sub_departments", []) or []),
        "org_type": org_type,
    }


def is_in_metro(person_data, metro):
    """Check if person is in target metro area."""
    city = (person_data.get("city", "") or "").lower()
    state = (person_data.get("state", "") or "").lower()
    target_state = metro["state"].lower()
    target_city = metro["city"].lower()
    surrounding = [c.lower() for c in metro.get("surrounding", [])]

    if target_city in city:
        return True
    if state == target_state and any(c in city for c in surrounding):
        return True
    if state == target_state and not city:
        return True  # no city listed, assume metro
    if f"greater {target_city}" in city:
        return True
    return False


def has_relevant_title(person_data):
    """Check if person has a relevant title for housing referrals."""
    title = (person_data.get("title", "") or "").lower()
    headline = (person_data.get("headline", "") or "").lower()
    combined = f"{title} {headline}"
    return any(kw in combined for kw in RELEVANT_TITLE_KEYWORDS)


def main(metro_key="houston"):
    metro = get_metro(metro_key)
    output_dir = get_output_dir(metro_key)
    orgs_file = output_dir / "orgs.json"
    contacts_file = output_dir / "raw_contacts.json"
    state_file = output_dir / "discover_state.json"

    if not orgs_file.exists():
        print(f"Error: Run step 1 first. Missing {orgs_file}")
        sys.exit(1)

    orgs_data = json.loads(orgs_file.read_text())
    batches = orgs_data.get("batches", [])

    # Load state for resume
    state = {}
    if state_file.exists():
        state = json.loads(state_file.read_text())
    searched_batches = set(state.get("searched_batches", []))

    # Load existing contacts
    all_people = []
    if contacts_file.exists():
        all_people = json.loads(contacts_file.read_text())
    seen_linkedin = {p.get("linkedin_url") for p in all_people if p.get("linkedin_url")}

    print(f"Discovering contacts in {metro['city']}, {metro['state']}...")
    print(f"Batches: {len(batches)} | Existing contacts: {len(all_people)}")

    seniority_levels = ["owner", "cxo", "vp", "director", "manager", "senior", "entry"]
    new_count = 0

    for i, batch in enumerate(batches):
        batch_key = "|".join(sorted(batch["names"]))
        if batch_key in searched_batches:
            continue

        print(f"\n[{i+1}/{len(batches)}] {', '.join(batch['names'])}")
        total, raw = ai_ark_search(batch["names"], seniority_levels)
        print(f"  Raw: {total} total, {len(raw)} fetched")

        batch_contacts = []
        for p in raw:
            pd = extract_person(p, batch.get("type", "unknown"))
            if not pd.get("linkedin_url") or pd["linkedin_url"] in seen_linkedin:
                continue
            seen_linkedin.add(pd["linkedin_url"])
            if not is_in_metro(pd, metro):
                continue
            if not has_relevant_title(pd):
                continue
            batch_contacts.append(pd)

        print(f"  Filtered: {len(batch_contacts)}")
        all_people.extend(batch_contacts)
        new_count += len(batch_contacts)

        # Save incrementally
        searched_batches.add(batch_key)
        state["searched_batches"] = list(searched_batches)
        state_file.write_text(json.dumps(state, indent=2))
        contacts_file.write_text(json.dumps(all_people, indent=2, default=str))
        time.sleep(0.5)

    print(f"\nTotal contacts: {len(all_people)} (new this run: {new_count})")
    print(f"Saved to {contacts_file}")

    # Print breakdown by org_type
    from collections import Counter
    type_counts = Counter(p.get("org_type", "unknown") for p in all_people)
    for t, c in type_counts.most_common():
        print(f"  {t}: {c}")

    return all_people


if __name__ == "__main__":
    metro = sys.argv[1] if len(sys.argv) > 1 else "houston"
    main(metro)
