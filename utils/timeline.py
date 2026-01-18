def timeline_consistency(insta_followers, twitter_exists):
    """
    Very conservative heuristic.
    """
    if twitter_exists and insta_followers > 300:
        return "consistent"
    if twitter_exists:
        return "partial"
    return "insufficient"
