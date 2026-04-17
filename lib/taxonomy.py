"""Taxonomy enums for referral source classification."""

REFERRAL_CATEGORIES = [
    "Parole / reentry",
    "Probation / court-related",
    "Hospital discharge",
    "Treatment discharge",
    "Behavioral health",
    "Substance abuse / recovery",
    "Veteran services",
    "Senior services",
    "Medicaid / waiver support",
    "IDD / disability services",
    "Homeless services",
    "Nonprofit partner",
    "Government social services",
    "Funding source",
    "Faith-based outreach",
    "Shelter / navigation center",
]

CONTACT_ROLES = [
    "Program Director",
    "Case Manager",
    "Social Worker",
    "Discharge Planner",
    "Housing Navigator",
    "Care Coordinator",
    "Clinical Director",
    "Veteran Coordinator",
    "Reentry Coordinator",
    "Probation or Parole Officer",
    "Intake Coordinator",
    "Outreach Director",
    "Executive Director",
    "Funding Administrator",
]

TARGET_POPULATIONS = [
    "Reentry",
    "Seniors with fixed income",
    "Homeless veterans",
    "Veterans with benefits",
    "Independent IDD clients",
    "Medicaid-supported clients",
    "Behavioral health clients",
    "Substance abuse recovery clients",
]

ORG_TYPES = [
    "nonprofit",
    "government",
    "hospital",
    "treatment_center",
    "veterans_org",
    "faith_based",
    "shelter",
    "private",
    "housing_authority",
]

# Title keywords for AI Ark filtering - expanded for all 14 contact roles
RELEVANT_TITLE_KEYWORDS = [
    # Social work
    "social work", "lcsw", "msw", "bsw",
    # Case management
    "case manag", "case coord",
    # Discharge
    "discharge", "transition",
    # Housing
    "housing", "placement", "navigator", "shelter",
    # Program leadership
    "program director", "program manager", "director of",
    "executive director", "chief operating", "chief executive",
    "vp ", "vice president",
    # Clinical
    "clinical director", "clinical",
    # Intake / outreach
    "intake", "outreach", "community",
    # Specialty coordinators
    "reentry", "parole", "probation", "veteran", "coordinator",
    # Care
    "care coordinator", "care manag", "patient advocate",
    # Services
    "services director", "operations", "residential",
    "supportive", "homeless", "benefits",
    # Funding
    "grant", "funding", "contract",
]

# Search query templates for org discovery
# {CITY} and {COUNTY} are replaced at runtime
SEARCH_QUERIES = [
    # Parole / reentry
    "{CITY} reentry organizations",
    "{CITY} reentry housing programs",
    "{COUNTY} parole office",
    "{CITY} prisoner reentry services",
    "{CITY} ex-offender housing assistance",
    # Probation / court-related
    "{COUNTY} probation department",
    "{CITY} court diversion programs housing",
    # Hospital discharge
    "{CITY} hospital discharge planning housing",
    "{CITY} medical center social work department",
    "{CITY} hospital case management",
    # Treatment discharge
    "{CITY} inpatient rehab discharge planning",
    "{CITY} residential treatment centers",
    # Behavioral health
    "{CITY} community mental health center",
    "{CITY} behavioral health housing programs",
    "{CITY} psychiatric facility discharge",
    # Substance abuse / recovery
    "{CITY} detox centers",
    "{CITY} substance abuse treatment centers",
    "{CITY} sober living placement",
    "{CITY} addiction recovery housing",
    # Veteran services
    "{CITY} SSVF providers",
    "{CITY} VA housing programs",
    "{CITY} veteran housing assistance",
    "{CITY} veteran service organizations",
    # Senior services
    "{CITY} senior housing assistance",
    "{COUNTY} aging services",
    "{CITY} area agency on aging",
    "{CITY} senior placement services",
    # Medicaid / waiver support
    "{CITY} Medicaid waiver housing",
    "{COUNTY} Medicaid managed care housing",
    "{CITY} HCBS waiver providers",
    # IDD / disability services
    "{CITY} IDD services housing",
    "{CITY} independent living center disability",
    "{CITY} disability housing coordinator",
    # Homeless services
    "{CITY} homeless services organizations",
    "{CITY} continuum of care homeless",
    "{CITY} homeless shelter intake",
    "{CITY} rapid rehousing programs",
    # Nonprofit partner
    "{CITY} nonprofit housing placement",
    "{CITY} transitional housing nonprofit",
    "{CITY} supportive housing organizations",
    # Government social services
    "{COUNTY} human services department housing",
    "{COUNTY} social services housing assistance",
    "{CITY} housing authority",
    # Funding source
    "{CITY} housing funding organizations",
    "{COUNTY} housing grants programs",
    # Faith-based outreach
    "{CITY} faith-based housing assistance",
    "{CITY} church homeless housing programs",
    # Shelter / navigation center
    "{CITY} navigation center homeless",
    "{CITY} emergency shelter services",
    "{CITY} shelter housing referral",
]

# ZIP-based search queries - higher coverage for neighborhood-level orgs
# {ZIP} is replaced at runtime with each ZIP code
ZIP_SEARCH_QUERIES = [
    "{ZIP} transitional housing",
    "{ZIP} homeless services nonprofit",
    "{ZIP} group home placement",
    "{ZIP} supportive housing",
    "{ZIP} sober living recovery housing",
    "{ZIP} disability housing services",
    "{ZIP} veteran housing assistance",
    "{ZIP} reentry housing program",
]
