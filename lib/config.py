"""Configuration - API keys, metro configs, constants."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.expanduser("~/.env"))

# API keys
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
AI_ARK_API_KEY = os.getenv("AI_ARK_API_KEY")
BLITZ_API_KEY = os.getenv("BLITZ_API_KEY")
LEADMAGIC_API_KEY = os.getenv("LEADMAGIC_API_KEY")
PROSPEO_API_KEY = os.getenv("PROSPEO_API_KEY")
MILLIONVERIFIER_API_KEY = os.getenv("MILLIONVERIFIER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# API base URLs
AI_ARK_BASE = "https://api.ai-ark.com/api/developer-portal/v1"
BLITZ_BASE = "https://api.blitz-api.ai/v2"
MV_BASE = "https://api.millionverifier.com/api/v3"
LEADMAGIC_URL = "https://api.leadmagic.io/v1/people/mobile-finder"
PROSPEO_URL = "https://api.prospeo.io/enrich-person"
SERPER_URL = "https://google.serper.dev/search"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"

# Rate limits
BLITZ_SEMAPHORE = 3       # ~2.5 req/s (hard limit 5 req/s)
BLITZ_DELAY = 0.4
MV_SEMAPHORE = 50         # MV allows 160 req/s
LEADMAGIC_SEMAPHORE = 20  # ceiling ~60-80 req/s
PROSPEO_SEMAPHORE = 20    # max 20 workers for mobile endpoint (429s at 100+)
AI_ARK_BATCH_SIZE = 3     # orgs per AI Ark query
LLM_BATCH_SIZE = 10       # contacts per LLM classification call

# Project paths
PROJECT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_DIR / "output"

# Metro configurations
METROS = {
    "houston": {
        "city": "Houston",
        "state": "Texas",
        "county": "Harris County",
        "surrounding": [
            "sugar land", "pasadena", "baytown", "pearland",
            "league city", "missouri city", "katy", "spring",
            "the woodlands", "cypress", "humble", "conroe",
            "galveston", "texas city", "friendswood", "richmond",
            "rosenberg", "stafford", "bellaire", "west university",
        ],
    },
    "dallas": {
        "city": "Dallas",
        "state": "Texas",
        "county": "Dallas County",
        "surrounding": [
            "fort worth", "arlington", "plano", "irving",
            "garland", "frisco", "mckinney", "denton",
            "richardson", "carrollton", "lewisville", "mesquite",
            "grand prairie", "allen", "flower mound", "cedar hill",
        ],
    },
    "atlanta": {
        "city": "Atlanta",
        "state": "Georgia",
        "county": "Fulton County",
        "surrounding": [
            "decatur", "marietta", "sandy springs", "roswell",
            "alpharetta", "smyrna", "kennesaw", "lawrenceville",
            "duluth", "norcross", "stone mountain", "east point",
            "college park", "union city", "jonesboro", "morrow",
        ],
    },
}


def get_metro(metro_key):
    """Get metro config by key. Raises KeyError if not found."""
    key = metro_key.lower().replace(" ", "_").replace(",", "")
    # Try direct match
    if key in METROS:
        return METROS[key]
    # Try matching city name
    for k, v in METROS.items():
        if v["city"].lower() == key or key.startswith(k):
            return v
    raise KeyError(f"Unknown metro: {metro_key}. Available: {list(METROS.keys())}")


def get_output_dir(metro_key):
    """Get or create output directory for a metro run."""
    from datetime import date
    metro = get_metro(metro_key)
    city_slug = metro["city"].lower().replace(" ", "_")
    run_dir = OUTPUT_DIR / f"{city_slug}_{date.today().isoformat()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir
