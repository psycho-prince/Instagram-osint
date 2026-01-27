# core/instagram.py
import hashlib
import httpx


def _headers(web: bool = True) -> dict:
    if web:
        return {
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 13) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Mobile Safari/537.36"
            ),
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "X-IG-App-ID": "936619743392459",
            "Referer": "https://www.instagram.com/",
        }
    return {
        "User-Agent": "Instagram 289.0.0.77.109 Android",
        "Accept": "*/*",
    }


# -----------------------------
# PUBLIC API (used by main.py)
# -----------------------------

async def resolve_user_id(username: str, cookies: dict, debug: bool = False) -> str | None:
    url = (
        "https://www.instagram.com/api/v1/users/web_profile_info/"
        f"?username={username}"
    )

    async with httpx.AsyncClient(
        headers=_headers(web=True),
        cookies=cookies,
        timeout=15,
    ) as c:
        r = await c.get(url)

    if debug:
        print(f"[DEBUG] resolve_user_id HTTP {r.status_code}")

    if r.status_code != 200:
        return None

    try:
        return r.json()["data"]["user"]["id"]
    except Exception:
        return None


async def fetch_profile_info(user_id: str, cookies: dict, debug: bool = False) -> dict:
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"

    async with httpx.AsyncClient(
        headers=_headers(web=False),
        cookies=cookies,
        timeout=15,
    ) as c:
        r = await c.get(url)

    if debug:
        print(f"[DEBUG] fetch_profile_info HTTP {r.status_code}")

    if r.status_code != 200:
        return {}

    u = r.json().get("user", {})
    pic = u.get("profile_pic_url_hd") or u.get("profile_pic_url")

    return {
        "full_name": u.get("full_name", ""),
        "biography": u.get("biography", ""),
        "external_url": u.get("external_url"),
        "followers": u.get("follower_count", 0),
        "following": u.get("following_count", 0),
        "posts": u.get("media_count", 0),
        "verified": u.get("is_verified", False),
        "business": u.get("is_business", False),
        "private": u.get("is_private", False),
        "public_email": u.get("public_email", ""),
        "public_phone": u.get("public_phone_number", ""),
        "profile_pic": pic,
        "profile_pic_hash": hashlib.sha1((pic or "").encode()).hexdigest()[:16],
    }


def infer_timeline_consistency(report: dict) -> str:
    platforms = report.get("platforms", {})
    if platforms.get("twitter", {}).get("exists"):
        return "consistent"
    return "unknown"


async def check_private_content_exposure(user_id: str, username: str, debug: bool = False) -> dict:
    """
    Checks for private content exposure vulnerabilities.
    """
    results = {
        "legacy_json_vulnerable": False,
        "legacy_json_evidence": "",
        "graphql_vulnerable": False,
        "graphql_evidence": "",
    }

    # Test 1: Legacy JSON endpoint
    legacy_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    legacy_headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        async with httpx.AsyncClient(headers=legacy_headers, timeout=15) as c:
            r = await c.get(legacy_url)
            if debug:
                print(f"[DEBUG] check_private_content_exposure (legacy) HTTP {r.status_code}")
            if r.status_code == 200:
                text_content = r.text
                if any(kw in text_content for kw in [
                    "edge_owner_to_timeline_media", "display_url", "video_url", '"edges":[{"node":'
                ]):
                    results["legacy_json_vulnerable"] = True
                    results["legacy_json_evidence"] = "Found media keywords in unauthenticated response."

    except Exception as e:
        if debug:
            print(f"[DEBUG] check_private_content_exposure (legacy) error: {e}")

    # Test 2: GraphQL endpoint
    graphql_url = (
        "https://www.instagram.com/graphql/query/?query_hash=58b6785bea111c67129decbe6a448951"
        f"&variables=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A12%7D"
    )
    graphql_headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }
    try:
        async with httpx.AsyncClient(headers=graphql_headers, timeout=15) as c:
            r = await c.get(graphql_url)
            if debug:
                print(f"[DEBUG] check_private_content_exposure (graphql) HTTP {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                if not data.get("errors"):
                    results["graphql_vulnerable"] = True
                    results["graphql_evidence"] = "GraphQL response did not contain an error, indicating possible data exposure."
    except Exception as e:
        if debug:
            print(f"[DEBUG] check_private_content_exposure (graphql) error: {e}")

    return results
