# utils/scoring.py

from utils.confidence import calculate_confidence
from utils.risk import calculate_risk


def score_confidence(report: dict) -> float:
    """
    Public scoring API used by main.py
    """
    return calculate_confidence(report)


def grade_risk(report: dict) -> tuple[str, str]:
    """
    Public risk grading API used by main.py
    """
    return calculate_risk(report)
