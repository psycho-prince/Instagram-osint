# utils/risk.py

def calculate_risk(report: dict) -> tuple[str, str]:
    """
    Convert confidence score into human-readable risk level.
    """

    confidence = report.get("confidence", 0.0)

    if confidence >= 0.75:
        return (
            "HIGH",
            "Strong identity correlation across platforms and signals"
        )

    if confidence >= 0.45:
        return (
            "MEDIUM",
            "Partial correlation across platforms"
        )

    return (
        "LOW",
        "Minimal public correlation found"
    )
