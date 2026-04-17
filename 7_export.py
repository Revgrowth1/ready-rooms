#!/usr/bin/env python3
"""Step 7: Export to JSON, CSV, and Google Sheets with CRM columns."""

import csv
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib.config import get_metro, get_output_dir


# CSV column order
CONTACT_COLUMNS = [
    # Identity
    "org_id", "full_name", "first_name", "last_name",
    # Role
    "job_title", "role_type", "seniority",
    # Organization
    "company_name", "org_type", "referral_category",
    # Contact info
    "direct_email", "email_verified", "email_status",
    "direct_phone", "linkedin_url",
    # Location
    "city", "state",
    # Classification
    "populations_served", "departments",
    # Scores
    "referral_relevance_score", "population_match_score",
    "decision_maker_score", "funding_influence_score",
    "contactability_score", "weighted_priority", "priority_tier",
    # Metadata
    "date_found", "verification_status",
    # CRM fields (empty - for manual tracking)
    "outreach_status", "first_contact_date", "follow_up_date",
    "lead_temperature", "referral_history", "assigned_to",
    "agreement_status", "next_action", "notes",
]

ORG_COLUMNS = [
    "org_id", "name", "org_type", "referral_category",
    "contact_count", "top_contact", "top_priority",
]


def export_csv(contacts, output_dir):
    """Export contacts to CSV."""
    csv_file = output_dir / "contacts_export.csv"
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CONTACT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for c in contacts:
            # Flatten populations list to string
            row = dict(c)
            row["job_title"] = row.get("title", row.get("job_title", ""))
            pops = row.get("populations_served", [])
            if isinstance(pops, list):
                row["populations_served"] = "; ".join(pops)
            # Initialize empty CRM fields
            for crm_field in ["outreach_status", "first_contact_date", "follow_up_date",
                              "lead_temperature", "referral_history", "assigned_to",
                              "agreement_status", "next_action", "notes"]:
                row.setdefault(crm_field, "")
            writer.writerow(row)
    print(f"CSV exported: {csv_file} ({len(contacts)} rows)")
    return csv_file


def export_json(contacts, orgs_file, output_dir, metro):
    """Export full structured JSON."""
    orgs = []
    if orgs_file.exists():
        orgs = json.loads(orgs_file.read_text())

    export = {
        "metadata": {
            "metro": metro,
            "total_contacts": len(contacts),
            "total_orgs": len(orgs),
            "contacts_with_email": sum(1 for c in contacts if c.get("direct_email")),
            "contacts_verified": sum(1 for c in contacts if c.get("email_verified")),
            "contacts_with_phone": sum(1 for c in contacts if c.get("direct_phone")),
            "tier_a": sum(1 for c in contacts if c.get("priority_tier") == "A"),
            "tier_b": sum(1 for c in contacts if c.get("priority_tier") == "B"),
            "tier_c": sum(1 for c in contacts if c.get("priority_tier") == "C"),
        },
        "organizations": orgs,
        "contacts": contacts,
    }

    json_file = output_dir / "referral_sources.json"
    json_file.write_text(json.dumps(export, indent=2, default=str))
    print(f"JSON exported: {json_file}")
    return json_file


def export_sheets(contacts, orgs, output_dir, metro):
    """Export to Google Sheets with 3 tabs."""
    city = metro["city"]
    sheet_title = f"{city} Referral Sources - Ready Rooms"

    # Create sheet
    try:
        result = subprocess.run(
            ["gog", "sheets", "create", sheet_title,
             "--sheets=All Contacts,Priority Contacts,Organizations",
             "--no-input", "--force"],
            capture_output=True, text=True, timeout=30,
        )
        output = result.stdout + result.stderr
        # Extract sheet ID
        sheet_id = None
        for line in output.split("\n"):
            if "ID:" in line:
                sheet_id = line.split("ID:")[-1].strip().split()[0]
                break
            # Try URL pattern
            if "spreadsheets/d/" in line:
                import re
                m = re.search(r"spreadsheets/d/([a-zA-Z0-9_-]+)", line)
                if m:
                    sheet_id = m.group(1)
                    break
        if not sheet_id:
            print(f"Warning: Could not extract sheet ID from: {output[:200]}")
            print("Skipping Sheets export. CSV and JSON are available.")
            return None
    except Exception as e:
        print(f"Warning: Sheets creation failed: {e}")
        print("Skipping Sheets export. CSV and JSON are available.")
        return None

    print(f"Sheet created: {sheet_id}")

    # Prepare data - All Contacts tab
    headers = CONTACT_COLUMNS
    all_rows = [headers]
    for c in contacts:
        row = []
        for col in headers:
            val = c.get(col, "")
            if col == "job_title":
                val = c.get("title", c.get("job_title", ""))
            if col == "populations_served":
                pops = c.get("populations_served", [])
                val = "; ".join(pops) if isinstance(pops, list) else str(pops)
            if isinstance(val, bool):
                val = str(val)
            row.append(str(val) if val else "")
        all_rows.append(row)

    # Priority Contacts tab (Tier A + B only)
    priority = [c for c in contacts if c.get("priority_tier") in ("A", "B")]
    priority_rows = [headers]
    for c in priority:
        row = []
        for col in headers:
            val = c.get(col, "")
            if col == "job_title":
                val = c.get("title", c.get("job_title", ""))
            if col == "populations_served":
                pops = c.get("populations_served", [])
                val = "; ".join(pops) if isinstance(pops, list) else str(pops)
            if isinstance(val, bool):
                val = str(val)
            row.append(str(val) if val else "")
        priority_rows.append(row)

    # Organizations tab
    org_rows = [ORG_COLUMNS]
    for o in orgs:
        org_rows.append([str(o.get(col, "")) for col in ORG_COLUMNS])

    # Write each tab
    for tab_name, rows in [
        ("All Contacts", all_rows),
        ("Priority Contacts", priority_rows),
        ("Organizations", org_rows),
    ]:
        if len(rows) <= 1:
            continue
        # Write as JSON for gog
        data_file = output_dir / f"_sheet_{tab_name.replace(' ', '_').lower()}.json"
        data_file.write_text(json.dumps(rows))
        n_cols = len(rows[0])
        n_rows = len(rows)
        # Column letter
        col_letter = chr(ord("A") + n_cols - 1) if n_cols <= 26 else "AZ"
        range_str = f"'{tab_name}'!A1:{col_letter}{n_rows}"
        try:
            subprocess.run(
                ["gog", "sheets", "update", sheet_id, range_str,
                 f"--values-json={data_file.read_text()}",
                 "--input=USER_ENTERED", "--no-input", "--force"],
                capture_output=True, text=True, timeout=60,
            )
            print(f"  Wrote {n_rows-1} rows to '{tab_name}'")
        except Exception as e:
            print(f"  Warning: Failed to write {tab_name}: {e}")

    # Format headers (bold white on dark blue)
    for tab_name in ["All Contacts", "Priority Contacts", "Organizations"]:
        try:
            n_cols = len(CONTACT_COLUMNS) if "Contact" in tab_name else len(ORG_COLUMNS)
            col_letter = chr(ord("A") + n_cols - 1) if n_cols <= 26 else "AZ"
            subprocess.run(
                ["gog", "sheets", "format", sheet_id,
                 f"'{tab_name}'!A1:{col_letter}1",
                 '--format-json={"textFormat":{"bold":true,"foregroundColor":{"red":1,"green":1,"blue":1}},"backgroundColor":{"red":0.24,"green":0.31,"blue":0.42}}',
                 "--format-fields=textFormat.bold,textFormat.foregroundColor,backgroundColor",
                 "--no-input", "--force"],
                capture_output=True, text=True, timeout=15,
            )
        except Exception:
            pass

    print(f"\nGoogle Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")
    return sheet_id


def main(metro_key="houston"):
    metro = get_metro(metro_key)
    output_dir = get_output_dir(metro_key)
    deduped_file = output_dir / "deduped_contacts.json"
    orgs_file = output_dir / "organizations.json"

    if not deduped_file.exists():
        print(f"Error: Run step 6 first. Missing {deduped_file}")
        sys.exit(1)

    contacts = json.loads(deduped_file.read_text())
    orgs = json.loads(orgs_file.read_text()) if orgs_file.exists() else []
    print(f"Loaded {len(contacts)} contacts, {len(orgs)} organizations")

    # Export all formats
    export_csv(contacts, output_dir)
    export_json(contacts, orgs_file, output_dir, metro)

    # Google Sheets
    sheet_id = export_sheets(contacts, orgs, output_dir, metro)

    # Summary
    print(f"\n--- Export Summary ---")
    print(f"Metro: {metro['city']}, {metro['state']}")
    print(f"Total contacts: {len(contacts)}")
    print(f"With email: {sum(1 for c in contacts if c.get('direct_email'))}")
    print(f"Verified email: {sum(1 for c in contacts if c.get('email_verified'))}")
    print(f"With phone: {sum(1 for c in contacts if c.get('direct_phone'))}")
    print(f"Tier A: {sum(1 for c in contacts if c.get('priority_tier') == 'A')}")
    print(f"Tier B: {sum(1 for c in contacts if c.get('priority_tier') == 'B')}")
    print(f"Tier C: {sum(1 for c in contacts if c.get('priority_tier') == 'C')}")
    print(f"Organizations: {len(orgs)}")
    print(f"\nFiles:")
    print(f"  CSV:  {output_dir / 'contacts_export.csv'}")
    print(f"  JSON: {output_dir / 'referral_sources.json'}")
    if sheet_id:
        print(f"  Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}")


if __name__ == "__main__":
    metro = sys.argv[1] if len(sys.argv) > 1 else "houston"
    main(metro)
