#!/usr/bin/env python3
"""Step 3: Combined async email + phone enrichment.

Runs BlitzAPI (email) and Prospeo (phone) concurrently per contact.
Phone enrichment happens during BlitzAPI rate limit waits, so total
time is ~same as email-only (~5 min for 700 contacts).
"""

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
    PROSPEO_API_KEY, PROSPEO_URL, PROSPEO_SEMAPHORE,
    get_output_dir,
)

stats = {"emails": 0, "verified": 0, "phones": 0, "done": 0, "total": 0, "errors": 0}


async def find_email(session, linkedin_url, sem):
    """BlitzAPI email finder."""
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


async def find_phone(session, linkedin_url, sem):
    """Prospeo mobile enrichment."""
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
                    person = data.get("person", {})
                    mobile_obj = person.get("mobile", {}) or {}
                    mobile = mobile_obj.get("mobile") or mobile_obj.get("mobile_international")
                    if mobile and mobile_obj.get("revealed"):
                        s = str(mobile).strip().replace(" ", "").replace("-", "")
                        return f"+{s}" if s and not s.startswith("+") else s
                elif resp.status == 400:
                    pass  # NO_MATCH
                elif resp.status == 429:
                    stats["errors"] += 1
                    await asyncio.sleep(3)
                else:
                    stats["errors"] += 1
                return None
        except Exception:
            stats["errors"] += 1
            return None


async def process_contact(session, contact, blitz_sem, mv_sem, prospeo_sem):
    """Enrich a single contact with email + phone concurrently."""
    if contact.get("direct_email") and contact.get("direct_phone"):
        stats["done"] += 1
        return contact

    linkedin = contact.get("linkedin_url", "")
    if not linkedin:
        stats["done"] += 1
        return contact

    # Fire email + phone requests concurrently
    tasks = []
    need_email = not contact.get("direct_email")
    need_phone = not contact.get("direct_phone")

    if need_email:
        tasks.append(find_email(session, linkedin, blitz_sem))
    if need_phone:
        tasks.append(find_phone(session, linkedin, prospeo_sem))

    results = await asyncio.gather(*tasks)

    idx = 0
    if need_email:
        email = results[idx]
        idx += 1
        if email:
            stats["emails"] += 1
            verified, status = await verify_email(session, email, mv_sem)
            if verified:
                stats["verified"] += 1
            contact["direct_email"] = email
            contact["email_verified"] = verified
            contact["email_status"] = status
        else:
            contact.setdefault("direct_email", "")
            contact.setdefault("email_verified", False)
            contact.setdefault("email_status", "none")

    if need_phone:
        phone = results[idx]
        if phone:
            stats["phones"] += 1
            contact["direct_phone"] = phone
        else:
            contact.setdefault("direct_phone", "")

    stats["done"] += 1
    if stats["done"] % 20 == 0:
        pct = stats["done"] / stats["total"] * 100
        print(
            f"  {stats['done']}/{stats['total']} ({pct:.0f}%) | "
            f"{stats['emails']} emails, {stats['verified']} verified | "
            f"{stats['phones']} phones | {stats['errors']} errors"
        )

    return contact


async def run(contacts, output_file):
    """Run combined enrichment on all contacts."""
    stats["total"] = len(contacts)
    blitz_sem = asyncio.Semaphore(BLITZ_SEMAPHORE)
    mv_sem = asyncio.Semaphore(MV_SEMAPHORE)
    prospeo_sem = asyncio.Semaphore(PROSPEO_SEMAPHORE)

    est_min = len(contacts) * BLITZ_DELAY / 60
    print(f"Enriching {len(contacts)} contacts (email + phone parallel) (~{est_min:.1f} min)")
    start = time.time()

    async with aiohttp.ClientSession() as session:
        for i in range(0, len(contacts), 20):
            batch = contacts[i : i + 20]
            await asyncio.gather(
                *[process_contact(session, c, blitz_sem, mv_sem, prospeo_sem) for c in batch]
            )
            output_file.write_text(json.dumps(contacts, indent=2, default=str))

    elapsed = time.time() - start
    w_email = sum(1 for c in contacts if c.get("direct_email"))
    w_ver = sum(1 for c in contacts if c.get("email_verified"))
    w_phone = sum(1 for c in contacts if c.get("direct_phone"))
    print(
        f"\nDone in {elapsed:.0f}s | "
        f"{w_email} emails ({w_email/len(contacts)*100:.0f}%), {w_ver} verified | "
        f"{w_phone} phones ({w_phone/len(contacts)*100:.0f}%) | "
        f"{stats['errors']} errors"
    )
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
