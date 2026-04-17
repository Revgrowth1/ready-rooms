"""Classification of contacts and organizations - rule-based with LLM upgrade path."""

import json
import os
import re
import time
import requests
from .config import ANTHROPIC_API_KEY, ANTHROPIC_URL, LLM_BATCH_SIZE
from .taxonomy import REFERRAL_CATEGORIES, CONTACT_ROLES, TARGET_POPULATIONS


# Rule-based classification maps
TITLE_TO_ROLE = {
    "social work": "Social Worker",
    "lcsw": "Social Worker",
    "msw": "Social Worker",
    "bsw": "Social Worker",
    "case manag": "Case Manager",
    "case coord": "Case Manager",
    "discharge": "Discharge Planner",
    "housing nav": "Housing Navigator",
    "housing coord": "Housing Navigator",
    "housing spec": "Housing Navigator",
    "program director": "Program Director",
    "program manager": "Program Director",
    "executive director": "Executive Director",
    "chief executive": "Executive Director",
    "chief operating": "Executive Director",
    "vp ": "Executive Director",
    "vice president": "Executive Director",
    "clinical director": "Clinical Director",
    "clinical": "Clinical Director",
    "intake": "Intake Coordinator",
    "outreach": "Outreach Director",
    "community": "Outreach Director",
    "reentry": "Reentry Coordinator",
    "re-entry": "Reentry Coordinator",
    "parole": "Probation or Parole Officer",
    "probation": "Probation or Parole Officer",
    "veteran": "Veteran Coordinator",
    "care coord": "Care Coordinator",
    "care manag": "Care Coordinator",
    "patient advocate": "Care Coordinator",
    "navigator": "Housing Navigator",
    "coordinator": "Care Coordinator",
    "grant": "Funding Administrator",
    "funding": "Funding Administrator",
    "contract": "Funding Administrator",
    "director of": "Program Director",
    "services director": "Program Director",
    "shelter": "Intake Coordinator",
    "residential": "Program Director",
    "operations": "Program Director",
    "transition": "Reentry Coordinator",
    "placement": "Housing Navigator",
}

ORG_TYPE_TO_CATEGORY = {
    "Parole / reentry": "Parole / reentry",
    "Probation / court-related": "Probation / court-related",
    "Hospital discharge": "Hospital discharge",
    "Treatment discharge": "Treatment discharge",
    "Behavioral health": "Behavioral health",
    "Substance abuse / recovery": "Substance abuse / recovery",
    "Veteran services": "Veteran services",
    "Senior services": "Senior services",
    "Medicaid / waiver support": "Medicaid / waiver support",
    "IDD / disability services": "IDD / disability services",
    "Homeless services": "Homeless services",
    "Nonprofit partner": "Nonprofit partner",
    "Government social services": "Government social services",
    "Funding source": "Funding source",
    "Faith-based outreach": "Faith-based outreach",
    "Shelter / navigation center": "Shelter / navigation center",
}

CATEGORY_TO_POPULATIONS = {
    "Parole / reentry": ["Reentry"],
    "Probation / court-related": ["Reentry"],
    "Hospital discharge": ["Behavioral health clients", "Seniors with fixed income"],
    "Treatment discharge": ["Substance abuse recovery clients", "Behavioral health clients"],
    "Behavioral health": ["Behavioral health clients", "Medicaid-supported clients"],
    "Substance abuse / recovery": ["Substance abuse recovery clients"],
    "Veteran services": ["Homeless veterans", "Veterans with benefits"],
    "Senior services": ["Seniors with fixed income"],
    "Medicaid / waiver support": ["Medicaid-supported clients", "Independent IDD clients"],
    "IDD / disability services": ["Independent IDD clients", "Medicaid-supported clients"],
    "Homeless services": ["Homeless veterans", "Reentry", "Behavioral health clients"],
    "Nonprofit partner": ["Reentry", "Behavioral health clients"],
    "Government social services": ["Reentry", "Seniors with fixed income", "Medicaid-supported clients"],
    "Funding source": ["Medicaid-supported clients"],
    "Faith-based outreach": ["Reentry", "Substance abuse recovery clients"],
    "Shelter / navigation center": ["Homeless veterans", "Reentry"],
}

# Referral relevance by category
CATEGORY_RELEVANCE = {
    "Homeless services": 90,
    "Shelter / navigation center": 88,
    "Hospital discharge": 85,
    "Treatment discharge": 85,
    "Parole / reentry": 82,
    "Behavioral health": 78,
    "Substance abuse / recovery": 78,
    "Veteran services": 75,
    "Probation / court-related": 72,
    "Nonprofit partner": 65,
    "IDD / disability services": 65,
    "Senior services": 62,
    "Medicaid / waiver support": 60,
    "Government social services": 55,
    "Faith-based outreach": 50,
    "Funding source": 40,
}

# Decision-maker score by role
ROLE_DECISION_SCORE = {
    "Discharge Planner": 90,
    "Housing Navigator": 88,
    "Intake Coordinator": 85,
    "Case Manager": 75,
    "Program Director": 70,
    "Social Worker": 65,
    "Care Coordinator": 65,
    "Reentry Coordinator": 70,
    "Veteran Coordinator": 68,
    "Clinical Director": 55,
    "Probation or Parole Officer": 60,
    "Outreach Director": 50,
    "Executive Director": 45,
    "Funding Administrator": 30,
}

# Funding influence by role + category
ROLE_FUNDING_SCORE = {
    "Funding Administrator": 85,
    "Executive Director": 60,
    "Program Director": 50,
    "Clinical Director": 40,
    "Case Manager": 35,
    "Social Worker": 30,
    "Discharge Planner": 25,
    "Housing Navigator": 20,
    "Intake Coordinator": 15,
    "Care Coordinator": 25,
    "Reentry Coordinator": 20,
    "Veteran Coordinator": 40,
    "Probation or Parole Officer": 15,
    "Outreach Director": 25,
}


def classify_rule_based(contact):
    """Rule-based classification from title keywords and org type."""
    title = (contact.get("title", "") or contact.get("job_title", "") or "").lower()
    headline = (contact.get("headline", "") or "").lower()
    combined = f"{title} {headline}"
    org_type = contact.get("org_type", "")

    # Determine role_type from title
    role_type = "Case Manager"  # default
    for keyword, role in TITLE_TO_ROLE.items():
        if keyword in combined:
            role_type = role
            break

    # Determine referral_category from org_type
    referral_category = ORG_TYPE_TO_CATEGORY.get(org_type, "Nonprofit partner")

    # Determine populations from category
    populations = CATEGORY_TO_POPULATIONS.get(referral_category, [])

    # Score based on role + category
    referral_relevance = CATEGORY_RELEVANCE.get(referral_category, 50)
    decision_maker = ROLE_DECISION_SCORE.get(role_type, 50)
    funding_influence = ROLE_FUNDING_SCORE.get(role_type, 20)

    # Boost funding score for certain categories
    if referral_category in ("Veteran services", "Medicaid / waiver support", "Funding source"):
        funding_influence = min(100, funding_influence + 20)

    return {
        "role_type": role_type,
        "referral_category": referral_category,
        "populations": populations,
        "referral_relevance_score": referral_relevance,
        "decision_maker_score": decision_maker,
        "funding_influence_score": funding_influence,
    }


def classify_contacts(contacts):
    """Classify all contacts using rule-based system.

    Fast, deterministic, no API calls needed.
    """
    print(f"  Rule-based classification for {len(contacts)} contacts...")
    results = []
    for c in contacts:
        results.append(classify_rule_based(c))
    print(f"  Done - classified {len(results)} contacts")
    return results
