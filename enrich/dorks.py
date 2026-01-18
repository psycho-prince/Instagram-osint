# enrich/dorks.py

def generate_dorks(report: dict) -> dict:
    username = report.get("username", "")
    variants = report.get("username_variants", [])
    bio = report.get("biography", "")
    user_id = report.get("user_id", "")
    avatars = report.get("avatar_history", [])

    dorks = {
        "google": [],
        "bing": []
    }

    # 1️⃣ Username-based dorks
    for u in set([username] + variants):
        dorks["google"].extend([
            f"\"{u}\" instagram",
            f"\"{u}\" \"instagram profile\"",
            f"site:instagram.com \"{u}\"",
            f"site:dumpor.com \"{u}\"",
            f"site:imginn.com \"{u}\"",
            f"site:picuki.com \"{u}\""
        ])

        dorks["bing"].extend([
            f"{u} instagram profile",
            f"site:dumpor.com {u}",
            f"site:imginn.com {u}"
        ])

    # 2️⃣ Bio text dorks
    if bio:
        dorks["google"].append(f"\"{bio}\" instagram")
        dorks["bing"].append(f"\"{bio}\" instagram")

    # 3️⃣ User ID dorks (rare but valuable)
    if user_id:
        dorks["google"].extend([
            f"\"profilePage_{user_id}\"",
            f"\"{user_id}\" \"instagram\""
        ])

    # 4️⃣ Avatar-based dorks
    for a in avatars:
        url = a.get("url", "")
        if url:
            token = url.split("/")[-1].split("?")[0]
            dorks["google"].append(f"\"{token}\" instagram")
            dorks["bing"].append(f"\"{token}\" instagram")

    # Deduplicate
    dorks["google"] = sorted(set(dorks["google"]))
    dorks["bing"] = sorted(set(dorks["bing"]))

    return dorks
