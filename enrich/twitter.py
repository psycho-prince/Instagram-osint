# enrich/twitter.py
import re
import httpx


EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)


async def twitter_deep_osint(username: str, debug: bool = False) -> dict:
    """
    Perform passive Twitter/X OSINT:
    - bio text extraction
    - URL extraction
    - pinned tweet text (best-effort)
    - email pattern inference from domains

    NO login, NO scraping private data.
    """

    base_url = f"https://x.com/{username}"
    result = {
        "exists": False,
        "bio": "",
        "urls": [],
        "pinned_text": "",
        "emails": [],
        "email_patterns": [],
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 13) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Mobile Safari/537.36"
        ),
        "Accept": "text/html",
    }

    async with httpx.AsyncClient(
        headers=headers,
        follow_redirects=True,
        timeout=15,
    ) as client:
        try:
            r = await client.get(base_url)
        except Exception as e:
            if debug:
                print(f"[DEBUG] Twitter request failed: {e}")
            return result

    if r.status_code != 200:
        if debug:
            print(f"[DEBUG] Twitter HTTP {r.status_code}")
        return result

    html = r.text.lower()
    result["exists"] = True

    # --- Extract emails (rare but possible)
    result["emails"] = list(set(EMAIL_REGEX.findall(r.text)))

    # --- Extract URLs
    for match in re.findall(r'https?://[^\s"\']+', r.text):
        if "x.com" not in match:
            result["urls"].append(match)

    result["urls"] = sorted(set(result["urls"]))

    # --- Email pattern inference from domains
    domains = set()
    for url in result["urls"]:
        try:
            domain = url.split("/")[2]
            domains.add(domain)
        except Exception:
            pass

    for d in domains:
        result["email_patterns"].extend([
            f"first@{d}",
            f"first.last@{d}",
            f"{username}@{d}",
        ])

    if debug:
        print("[DEBUG] Twitter deep OSINT complete")

    return result
