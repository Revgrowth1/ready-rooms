#!/usr/bin/env python3
"""Step 1: Research target organizations via Serper web search."""

import json
import sys
import time
import requests
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.config import SERPER_API_KEY, SERPER_URL, get_metro, get_output_dir
from lib.taxonomy import SEARCH_QUERIES


def serper_search(query, num_results=10):
    """Run a Serper web search. Returns list of organic results."""
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": num_results}
    try:
        resp = requests.post(SERPER_URL, headers=headers, json=payload, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("organic", [])
        else:
            print(f"  Serper error {resp.status_code}: {resp.text[:200]}")
            return []
    except Exception as e:
        print(f"  Serper exception: {e}")
        return []


def extract_org_from_result(result, query, category_hint):
    """Extract org-level data from a Serper search result."""
    return {
        "name": result.get("title", "").split(" - ")[0].split(" | ")[0].strip(),
        "website": result.get("link", ""),
        "snippet": result.get("snippet", ""),
        "source_query": query,
        "category_hint": category_hint,
        "source_url": result.get("link", ""),
    }


def infer_category(query):
    """Infer referral category from the search query template."""
    q = query.lower()
    if "reentry" in q or "prisoner" in q or "ex-offender" in q or "parole" in q:
        return "Parole / reentry"
    if "probation" in q or "court" in q:
        return "Probation / court-related"
    if "hospital" in q or "medical center" in q:
        return "Hospital discharge"
    if "inpatient" in q or "residential treatment" in q:
        return "Treatment discharge"
    if "mental health" in q or "behavioral" in q or "psychiatric" in q:
        return "Behavioral health"
    if "detox" in q or "substance" in q or "sober" in q or "addiction" in q:
        return "Substance abuse / recovery"
    if "veteran" in q or "ssvf" in q or "va " in q:
        return "Veteran services"
    if "senior" in q or "aging" in q:
        return "Senior services"
    if "medicaid" in q or "waiver" in q or "hcbs" in q:
        return "Medicaid / waiver support"
    if "idd" in q or "disability" in q or "independent living" in q:
        return "IDD / disability services"
    if "homeless" in q or "continuum" in q or "rapid rehousing" in q:
        return "Homeless services"
    if "nonprofit" in q or "transitional" in q or "supportive" in q:
        return "Nonprofit partner"
    if "human services" in q or "social services" in q or "housing authority" in q:
        return "Government social services"
    if "funding" in q or "grants" in q:
        return "Funding source"
    if "faith" in q or "church" in q:
        return "Faith-based outreach"
    if "navigation" in q or "shelter" in q or "emergency" in q:
        return "Shelter / navigation center"
    return "Nonprofit partner"


def deduplicate_orgs(orgs):
    """Deduplicate orgs by normalized name + domain."""
    seen_names = {}
    seen_domains = set()
    unique = []
    for org in orgs:
        name_key = org["name"].lower().strip()
        # Skip very short or generic names
        if len(name_key) < 3:
            continue
        # Extract domain from website
        domain = ""
        url = org.get("website", "")
        if url:
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc.replace("www.", "")
            except Exception:
                pass
        # Dedup by domain first (strongest signal)
        if domain and domain in seen_domains:
            # Merge: keep the one with more info
            continue
        # Dedup by name similarity
        if name_key in seen_names:
            continue
        seen_names[name_key] = True
        if domain:
            seen_domains.add(domain)
        unique.append(org)
    return unique


def main(metro_key="houston"):
    metro = get_metro(metro_key)
    output_dir = get_output_dir(metro_key)
    orgs_file = output_dir / "orgs.json"

    # Resume from existing if available
    existing_orgs = []
    searched_queries = set()
    if orgs_file.exists():
        existing_orgs = json.loads(orgs_file.read_text())
        searched_queries = {o.get("source_query", "") for o in existing_orgs}
        print(f"Resuming: {len(existing_orgs)} orgs from {len(searched_queries)} queries")

    city = metro["city"]
    county = metro["county"]

    print(f"Researching referral sources in {city}, {metro['state']}...")
    all_orgs = list(existing_orgs)
    queries_run = 0

    for template in SEARCH_QUERIES:
        query = template.replace("{CITY}", city).replace("{COUNTY}", county)
        if query in searched_queries:
            continue
        category = infer_category(template)
        results = serper_search(query)
        queries_run += 1

        for r in results:
            org = extract_org_from_result(r, query, category)
            if org["name"]:
                all_orgs.append(org)

        if queries_run % 10 == 0:
            print(f"  {queries_run} queries | {len(all_orgs)} raw orgs")
        time.sleep(0.3)  # gentle pace

    # Deduplicate
    unique_orgs = deduplicate_orgs(all_orgs)
    print(f"\nQueries run: {queries_run}")
    print(f"Raw orgs: {len(all_orgs)} -> Deduplicated: {len(unique_orgs)}")

    # Build AI Ark batches (groups of 3 by category)
    from collections import defaultdict
    by_category = defaultdict(list)
    for org in unique_orgs:
        by_category[org["category_hint"]].append(org["name"])

    batches = []
    for cat, names in by_category.items():
        for i in range(0, len(names), 3):
            batch_names = names[i : i + 3]
            batches.append({"names": batch_names, "type": cat})

    # Save
    output = {
        "metro": metro,
        "orgs": unique_orgs,
        "batches": batches,
        "stats": {
            "queries_run": queries_run + len(searched_queries),
            "raw_count": len(all_orgs),
            "unique_count": len(unique_orgs),
            "batch_count": len(batches),
            "categories": {cat: len(names) for cat, names in by_category.items()},
        },
    }
    orgs_file.write_text(json.dumps(output, indent=2, default=str))
    print(f"\nSaved to {orgs_file}")
    print(f"Batches for AI Ark: {len(batches)}")
    for cat, count in sorted(output["stats"]["categories"].items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} orgs")

    return output


if __name__ == "__main__":
    metro = sys.argv[1] if len(sys.argv) > 1 else "houston"
    main(metro)
