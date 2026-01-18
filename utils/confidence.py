# utils/confidence.py

def calculate_confidence(report: dict) -> float:
    """
    Calculate confidence score (0.0 – 1.0)
    based on OSINT correlation strength.
    """

    score = 0.0

    # Core identity signals
    if report.get("user_id"):
        score += 0.25

    platforms = report.get("platforms", {})
    if platforms.get("twitter", {}).get("exists"):
        score += 0.20

    if report.get("timeline_consistency") == "consistent":
        score += 0.10

    if report.get("username_variants"):
        score += 0.05

    if report.get("avatar_changed") is False:
        score += 0.10

    if report.get("external_url"):
        score += 0.10

    if report.get("emails"):
        score += 0.10

    return round(min(score, 1.0), 2)
