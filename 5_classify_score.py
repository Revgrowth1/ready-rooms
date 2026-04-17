#!/usr/bin/env python3
"""Step 5: LLM classification + weighted scoring."""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.config import get_output_dir
from lib.classifier import classify_contacts
from lib.scorer import score_contact, tier_from_score


def main(metro_key="houston"):
    output_dir = get_output_dir(metro_key)
    contacts_file = output_dir / "raw_contacts.json"
    scored_file = output_dir / "scored_contacts.json"

    if not contacts_file.exists():
        print(f"Error: Run steps 2-4 first. Missing {contacts_file}")
        sys.exit(1)

    contacts = json.loads(contacts_file.read_text())
    print(f"Loaded {len(contacts)} contacts")

    # Skip already-classified contacts
    unclassified = [c for c in contacts if "role_type" not in c]
    classified = [c for c in contacts if "role_type" in c]
    print(f"  Already classified: {len(classified)}, to classify: {len(unclassified)}")

    if unclassified:
        print(f"\nClassifying {len(unclassified)} contacts via Claude Haiku...")
        classifications = classify_contacts(unclassified)

        for contact, classification in zip(unclassified, classifications):
            # Apply classification
            contact["role_type"] = classification.get("role_type", "Case Manager")
            contact["referral_category"] = classification.get("referral_category", "Nonprofit partner")
            contact["populations_served"] = classification.get("populations", [])

            # Compute scores
            scores = score_contact(contact, classification)
            contact["referral_relevance_score"] = scores["referral_relevance"]
            contact["population_match_score"] = scores["population_match"]
            contact["decision_maker_score"] = scores["decision_maker"]
            contact["funding_influence_score"] = scores["funding_influence"]
            contact["contactability_score"] = scores["contactability"]
            contact["weighted_priority"] = scores["weighted_priority"]
            contact["priority_tier"] = tier_from_score(scores["weighted_priority"])

            # Metadata
            contact["date_found"] = date.today().isoformat()
            contact["verification_status"] = (
                "verified" if contact.get("email_verified") else
                "partial" if contact.get("direct_email") else
                "unverified"
            )

    # Merge back
    all_contacts = classified + unclassified

    # Sort by weighted priority descending
    all_contacts.sort(key=lambda c: c.get("weighted_priority", 0), reverse=True)

    # Save
    scored_file.write_text(json.dumps(all_contacts, indent=2, default=str))

    # Stats
    tiers = {"A": 0, "B": 0, "C": 0}
    for c in all_contacts:
        t = c.get("priority_tier", "C")
        tiers[t] = tiers.get(t, 0) + 1

    print(f"\nScored {len(all_contacts)} contacts")
    print(f"  Tier A (>=70): {tiers.get('A', 0)}")
    print(f"  Tier B (>=45): {tiers.get('B', 0)}")
    print(f"  Tier C (<45):  {tiers.get('C', 0)}")

    # Top 10 preview
    print(f"\nTop 10 by weighted priority:")
    for c in all_contacts[:10]:
        print(
            f"  {c.get('weighted_priority', 0):5.1f} | {c.get('priority_tier', '?')} | "
            f"{c.get('full_name', ''):<25} | {c.get('title', '')[:40]:<40} | "
            f"{c.get('company_name', '')[:30]}"
        )

    print(f"\nSaved to {scored_file}")
    return all_contacts


if __name__ == "__main__":
    metro = sys.argv[1] if len(sys.argv) > 1 else "houston"
    main(metro)
