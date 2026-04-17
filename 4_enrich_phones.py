#!/usr/bin/env python3
"""Step 4: Async phone enrichment via Prospeo mobile enrichment."""

import asyncio
import json
import sys
import time
from pathlib import Path

import aiohttp

sys.path.insert(0, str(Path(__file__).parent))
from lib.config import PROSPEO_API_KEY, PROSPEO_URL, PROSPEO_SEMAPHORE, get_output_dir

stats = {"found": 0, "done": 0, "total": 0, "errors": 0}


async def find_phone(session, linkedin_url, sem):
    """Prospeo mobile enrichment.
    Uses /enrich-person with enrich_mobile: true.
    Costs 10 credits per hit. 20 workers max (429s at 100+).
    """
    async with sem:
        try:
            async with session.post(
                PROSPEO_URL,
                headers={"X-KEY": PROSPEO_API_KEY, "Content-Type": "application/json"},
                json={
                    "data": {"linkedin_url": linkedin_url},
                    "enrich_mobile": True,
                    "only_verified_email": False,
                },
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Prospeo nests mobile under person.mobile.mobile
                    person = data.get("person", {})
                    mobile_obj = person.get("mobile", {}) or {}
                    mobile = mobile_obj.get("mobile") or mobile_obj.get("mobile_international")
                    if mobile and mobile_obj.get("revealed"):
                        s = str(mobile).strip().replace(" ", "").replace("-", "")
                        return f"+{s}" if s and not s.startswith("+") else s
                elif resp.status == 400:
                    pass  # NO_MATCH - no charge
                elif resp.status == 429:
                    stats["errors"] += 1
                    await asyncio.sleep(3)
                else:
                    stats["errors"] += 1
                return None
        except Exception:
            stats["errors"] += 1
            return None


async def process_contact(session, contact, sem):
    """Enrich a single contact with phone number."""
    if contact.get("direct_phone"):
        stats["done"] += 1
        return contact

    linkedin = contact.get("linkedin_url", "")
    phone = None
    if linkedin:
        phone = await find_phone(session, linkedin, sem)

    stats["done"] += 1
    if phone:
        stats["found"] += 1
    if stats["done"] % 30 == 0:
        pct = stats["done"] / stats["total"] * 100
        print(f"  {stats['done']}/{stats['total']} ({pct:.0f}%) | {stats['found']} phones | {stats['errors']} errors")

    contact["direct_phone"] = phone or ""
    return contact


async def run(contacts, output_file):
    """Run async phone enrichment on all contacts."""
    stats["total"] = len(contacts)
    sem = asyncio.Semaphore(PROSPEO_SEMAPHORE)

    print(f"Finding phones for {len(contacts)} contacts via Prospeo (~{len(contacts)/PROSPEO_SEMAPHORE:.0f}s)")
    start = time.time()

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(contacts), 20):
            batch = contacts[i : i + 20]
            await asyncio.gather(
                *[process_contact(session, c, sem) for c in batch]
            )
            output_file.write_text(json.dumps(contacts, indent=2, default=str))

    elapsed = time.time() - start
    w_phone = sum(1 for c in contacts if c.get("direct_phone"))
    print(f"\nDone in {elapsed:.0f}s | {w_phone} phones ({w_phone/len(contacts)*100:.0f}%) | {stats['errors']} errors")
    return contacts


def main(metro_key="houston"):
    output_dir = get_output_dir(metro_key)
    contacts_file = output_dir / "raw_contacts.json"

    if not contacts_file.exists():
        print(f"Error: Run step 3 first. Missing {contacts_file}")
        sys.exit(1)

    contacts = json.loads(contacts_file.read_text())
    print(f"Loaded {len(contacts)} contacts from {contacts_file}")

    asyncio.run(run(contacts, contacts_file))
    print(f"Updated {contacts_file}")


if __name__ == "__main__":
    metro = sys.argv[1] if len(sys.argv) > 1 else "houston"
    main(metro)
