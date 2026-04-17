"""Weighted priority scoring for referral source contacts."""

from .taxonomy import TARGET_POPULATIONS

# Weights - funding lowered because operational roles (discharge planners,
# housing navigators) score low on funding but are our highest-value contacts.
# Decision-maker and contactability boosted to reward actionable leads.
W_REFERRAL = 0.30
W_POPULATION = 0.25
W_DECISION = 0.25
W_FUNDING = 0.05
W_CONTACT = 0.15


def score_contactability(contact):
    """Score based on data completeness. 0-100."""
    score = 0
    if contact.get("direct_email"):
        score += 30
    if contact.get("email_verified"):
        score += 20
    if contact.get("direct_phone"):
        score += 30
    if contact.get("linkedin_url"):
        score += 20
    return score


def score_population_match(populations_served):
    """Score based on overlap with Ready Rooms target populations. 0-100."""
    if not populations_served:
        return 0
    matches = sum(1 for p in populations_served if p in TARGET_POPULATIONS)
    # Scale: 1 match = 30, 2 = 55, 3 = 75, 4+ = 90-100
    if matches == 0:
        return 10  # org was discovered, likely somewhat relevant
    elif matches == 1:
        return 30
    elif matches == 2:
        return 55
    elif matches == 3:
        return 75
    elif matches == 4:
        return 90
    else:
        return 100


def compute_weighted_priority(scores):
    """Compute weighted priority score from individual scores.

    Args:
        scores: dict with keys referral_relevance, population_match,
                decision_maker, funding_influence, contactability

    Returns:
        float 0-100
    """
    return round(
        scores.get("referral_relevance", 0) * W_REFERRAL
        + scores.get("population_match", 0) * W_POPULATION
        + scores.get("decision_maker", 0) * W_DECISION
        + scores.get("funding_influence", 0) * W_FUNDING
        + scores.get("contactability", 0) * W_CONTACT,
        1,
    )


def score_contact(contact, classification):
    """Compute all scores for a contact.

    Args:
        contact: dict with email, phone, linkedin_url, email_verified fields
        classification: dict from LLM with referral_relevance_score,
                       decision_maker_score, funding_influence_score, populations

    Returns:
        dict with all 5 scores + weighted_priority
    """
    scores = {
        "referral_relevance": classification.get("referral_relevance_score", 50),
        "population_match": score_population_match(
            classification.get("populations", [])
        ),
        "decision_maker": classification.get("decision_maker_score", 50),
        "funding_influence": classification.get("funding_influence_score", 20),
        "contactability": score_contactability(contact),
    }
    scores["weighted_priority"] = compute_weighted_priority(scores)
    return scores


def tier_from_score(priority_score):
    """Assign tier based on weighted priority score."""
    if priority_score >= 70:
        return "A"
    elif priority_score >= 45:
        return "B"
    else:
        return "C"
