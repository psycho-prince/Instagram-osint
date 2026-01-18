# enrich/usernames.py
import httpx


# -----------------------------
# PUBLIC API
# -----------------------------

def generate_variants(username: str) -> list[str]:
    base = username.strip("_").replace(".", "")
    variants = {
        username,
        base,
        f"_{base}_",
        f"__{base}__",
        f"{base}_",
        f"_{base}",
        username.replace(".", ""),
        username.replace("_", ""),
    }
    return sorted(variants)


async def check_username_presence(username: str, debug: bool = False) -> dict:
    platforms = {
        "github": f"https://github.com/{username}",
        "twitter": f"https://x.com/{username}",
        "reddit": f"https://www.reddit.com/user/{username}",
        "tiktok": f"https://www.tiktok.com/@{username}",
        "medium": f"https://medium.com/@{username}",
        "devto": f"https://dev.to/{username}",
    }

    results = {}

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
        for name, url in platforms.items():
            try:
                r = await c.get(url)
                exists = r.status_code in (200, 301, 302)
                results[name] = {
                    "exists": exists,
                    "status": r.status_code,
                    "url": url,
                }
            except Exception as e:
                results[name] = {
                    "exists": False,
                    "status": "error",
                    "error": str(e),
                    "url": url,
                }

    if debug:
        print("[DEBUG] Username presence checked")

    return results
