#!/usr/bin/env python3
"""Step 3: Async email enrichment via BlitzAPI + MillionVerifier."""

import asyncio
import json
import sys
import time
from pathlib import Path

import aiohttp

sys.path.insert(0, str(Path(__file__).parent))
from lib.config import (
    BLITZ_API_KEY, BLITZ_BASE, BLITZ_DELAY, BLITZ_SEMAPHORE,
    MILLIONVERIFIER_API_KEY, MV_BASE, MV_SEMAPHORE,
    get_output_dir,
)

stats = {"emails": 0, "verified": 0, "done": 0, "total": 0}


async def find_email(session, linkedin_url, sem):
    """BlitzAPI email finder.
    CRITICAL: Endpoint is /enrichment/email with person_linkedin_url param.
    """
    async with sem:
        try:
            async with session.post(
                f"{BLITZ_BASE}/enrichment/email",
                headers={"x-api-key": BLITZ_API_KEY, "Content-Type": "application/json"},
                json={"person_linkedin_url": linkedin_url},
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("found") and data.get("email"):
                        return data["email"]
                    all_emails = data.get("all_emails", [])
                    if all_emails:
                        e = all_emails[0]
                        return e.get("email") if isinstance(e, dict) else e
                elif resp.status == 429:
                    await asyncio.sleep(5)
                return None
        except Exception:
            return None
        finally:
            await asyncio.sleep(BLITZ_DELAY)


async def verify_email(session, email, sem):
    """MillionVerifier. Codes: 1=valid, 2=catch_all (keep both)."""
    async with sem:
        try:
            async with session.get(
                MV_BASE,
                params={"api": MILLIONVERIFIER_API_KEY, "email": email, "timeout": 20},
                headers={"User-Agent": "ReadyRooms-Verifier/1.0"},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    code = data.get("resultcode")
                    return code in [1, 2], data.get("result", "unknown")
                return False, "error"
        except Exception:
            return False, "error"


async def process_contact(session, contact, blitz_sem, mv_sem):
    """Enrich a single contact with email + verification."""
    # Skip if already enriched
    if contact.get("direct_email"):
        stats["done"] += 1
        return contact

    linkedin = contact.get("linkedin_url", "")
    email, verified, status = None, False, "none"

    if linkedin:
        email = await find_email(session, linkedin, blitz_sem)
        if email:
            stats["emails"] += 1
            verified, status = await verify_email(session, email, mv_sem)
            if verified:
                stats["verified"] += 1

    stats["done"] += 1
    if stats["done"] % 20 == 0:
        pct = stats["done"] / stats["total"] * 100
        print(
            f"  {stats['done']}/{stats['total']} ({pct:.0f}%) | "
            f"{stats['emails']} emails, {stats['verified']} verified"
        )

    contact["direct_email"] = email or ""
    contact["email_verified"] = verified
    contact["email_status"] = status
    return contact


async def run(contacts, output_file):
    """Run async email enrichment on all contacts."""
    stats["total"] = len(contacts)
    blitz_sem = asyncio.Semaphore(BLITZ_SEMAPHORE)
    mv_sem = asyncio.Semaphore(MV_SEMAPHORE)

    print(f"Enriching {len(contacts)} contacts... (~{len(contacts)*BLITZ_DELAY/60:.1f} min)")
    start = time.time()

    async with aiohttp.ClientSession() as session:
        # Process in chunks of 10 for incremental saves
        for i in range(0, len(contacts), 10):
            batch = contacts[i : i + 10]
            await asyncio.gather(
                *[process_contact(session, c, blitz_sem, mv_sem) for c in batch]
            )
            # Incremental save
            output_file.write_text(json.dumps(contacts, indent=2, default=str))

    elapsed = time.time() - start
    w_email = sum(1 for c in contacts if c.get("direct_email"))
    w_ver = sum(1 for c in contacts if c.get("email_verified"))
    print(f"\nDone in {elapsed:.0f}s | {w_email} emails ({w_email/len(contacts)*100:.0f}%), {w_ver} verified")
    return contacts


def main(metro_key="houston"):
    output_dir = get_output_dir(metro_key)
    contacts_file = output_dir / "raw_contacts.json"

    if not contacts_file.exists():
        print(f"Error: Run step 2 first. Missing {contacts_file}")
        sys.exit(1)

    contacts = json.loads(contacts_file.read_text())
    print(f"Loaded {len(contacts)} contacts from {contacts_file}")

    asyncio.run(run(contacts, contacts_file))
    print(f"Updated {contacts_file}")


if __name__ == "__main__":
    metro = sys.argv[1] if len(sys.argv) > 1 else "houston"
    main(metro)
