#!/usr/bin/env python3
"""Step 6: Deduplication of contacts and organizations."""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.config import get_output_dir


def normalize_name(name):
    """Normalize org/person name for dedup comparison."""
    if not name:
        return ""
    n = name.lower().strip()
    # Remove common suffixes
    for suffix in [", inc.", ", inc", " inc.", " inc", ", llc", " llc",
                   ", ltd", " ltd", " corp", " corporation",
                   " foundation", " association"]:
        n = n.replace(suffix, "")
    # Remove punctuation
    n = re.sub(r"[^\w\s]", "", n)
    # Collapse whitespace
    n = re.sub(r"\s+", " ", n).strip()
    return n


def normalize_linkedin(url):
    """Normalize LinkedIn URL for dedup."""
    if not url:
        return ""
    url = url.rstrip("/").lower()
    # Remove query params
    url = url.split("?")[0]
    return url


def dedup_contacts(contacts):
    """Deduplicate contacts by LinkedIn URL, then by name+company."""
    seen_linkedin = {}
    seen_name_company = {}
    unique = []
    dupes = 0

    for c in contacts:
        # Primary dedup: LinkedIn URL
        linkedin = normalize_linkedin(c.get("linkedin_url", ""))
        if linkedin:
            if linkedin in seen_linkedin:
                dupes += 1
                # Keep higher-scored version
                existing = seen_linkedin[linkedin]
                if c.get("weighted_priority", 0) > existing.get("weighted_priority", 0):
                    unique[unique.index(existing)] = c
                    seen_linkedin[linkedin] = c
                continue
            seen_linkedin[linkedin] = c

        # Secondary dedup: name + company
        name = normalize_name(c.get("full_name", ""))
        company = normalize_name(c.get("company_name", ""))
        key = f"{name}|{company}"
        if key and key != "|" and key in seen_name_company:
            dupes += 1
            continue
        if key and key != "|":
            seen_name_company[key] = c

        unique.append(c)

    return unique, dupes


def dedup_orgs(contacts):
    """Identify unique organizations from contacts and assign org_ids."""
    org_map = {}  # normalized_name -> org_id
    org_counter = 0

    for c in contacts:
        company = normalize_name(c.get("company_name", ""))
        if not company:
            c["org_id"] = "ORG_UNKNOWN"
            continue

        if company not in org_map:
            org_counter += 1
            org_map[company] = f"ORG_{org_counter:04d}"

        c["org_id"] = org_map[company]

    return org_map


def main(metro_key="houston"):
    output_dir = get_output_dir(metro_key)
    scored_file = output_dir / "scored_contacts.json"
    deduped_file = output_dir / "deduped_contacts.json"

    if not scored_file.exists():
        print(f"Error: Run step 5 first. Missing {scored_file}")
        sys.exit(1)

    contacts = json.loads(scored_file.read_text())
    print(f"Loaded {len(contacts)} scored contacts")

    # Dedup contacts
    unique, dupes = dedup_contacts(contacts)
    print(f"Contacts: {len(contacts)} -> {len(unique)} (removed {dupes} duplicates)")

    # Assign org IDs
    org_map = dedup_orgs(unique)
    print(f"Unique organizations: {len(org_map)}")

    # Re-sort by priority
    unique.sort(key=lambda c: c.get("weighted_priority", 0), reverse=True)

    # Save
    deduped_file.write_text(json.dumps(unique, indent=2, default=str))
    print(f"Saved to {deduped_file}")

    # Save org summary
    org_summary = {}
    for c in unique:
        oid = c.get("org_id", "")
        if oid not in org_summary:
            org_summary[oid] = {
                "org_id": oid,
                "name": c.get("company_name", ""),
                "org_type": c.get("org_type", ""),
                "referral_category": c.get("referral_category", ""),
                "contact_count": 0,
                "top_contact": c.get("full_name", ""),
                "top_priority": c.get("weighted_priority", 0),
            }
        org_summary[oid]["contact_count"] += 1

    org_file = output_dir / "organizations.json"
    org_list = sorted(org_summary.values(), key=lambda o: -o["top_priority"])
    org_file.write_text(json.dumps(org_list, indent=2, default=str))
    print(f"Organizations saved to {org_file}")

    return unique


if __name__ == "__main__":
    metro = sys.argv[1] if len(sys.argv) > 1 else "houston"
    main(metro)
