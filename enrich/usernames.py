# enrich/usernames.py
import httpx
from bs4 import BeautifulSoup


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

async def check_username_presence_advanced(username: str, full_name: str, debug: bool = False) -> dict:
    platforms = {
        "github": {
            "url": f"https://github.com/{username}",
            "parser": _parse_github_profile,
        },
        "reddit": {
            "url": f"https://www.reddit.com/user/{username}",
            "parser": _parse_reddit_profile,
        },
        "medium": {
            "url": f"https://medium.com/@{username}",
            "parser": _parse_medium_profile,
        },
    }

    results = {}

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as c:
        for name, config in platforms.items():
            url = config["url"]
            parser = config["parser"]
            try:
                r = await c.get(url)
                if r.status_code == 200:
                    results[name] = await parser(r.text, username, full_name)
                else:
                    results[name] = {"exists": False, "status": r.status_code}
            except Exception as e:
                results[name] = {
                    "exists": False,
                    "status": "error",
                    "error": str(e),
                }

    if debug:
        print("[DEBUG] Advanced username presence checked")

    return results

async def _parse_github_profile(html: str, username: str, full_name: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = {"exists": True, "url": f"https://github.com/{username}", "confidence": 0.0, "matches": []}

    # Check for username in title
    if soup.title and username.lower() in soup.title.string.lower():
        result["confidence"] += 0.3
        result["matches"].append("Username in title")

    # Check for full name
    page_full_name_element = soup.find("span", {"itemprop": "name"})
    if page_full_name_element:
        page_full_name = page_full_name_element.text.strip()
        if page_full_name:
            result["extracted_full_name"] = page_full_name
            if full_name and (full_name.lower() in page_full_name.lower() or page_full_name.lower() in full_name.lower()):
                result["confidence"] += 0.4
                result["matches"].append("Full name match")

    # Check for bio
    bio_element = soup.find("div", {"class": "p-note user-profile-bio"})
    if bio_element and bio_element.text:
        result["extracted_bio"] = bio_element.text.strip()
        result["confidence"] += 0.1 # Add a small amount of confidence for having a bio

    result["confidence"] = round(result["confidence"], 2)
    return result

async def _parse_reddit_profile(html: str, username: str, full_name: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = {"exists": True, "url": f"https://www.reddit.com/user/{username}", "confidence": 0.0, "matches": []}

    if soup.title and username.lower() in soup.title.string.lower():
        result["confidence"] += 0.3
        result["matches"].append("Username in title")

    # Reddit doesn't have a reliable full name field, but we can check the profile description
    description_element = soup.find("div", {"class": "_3_b2x7T8Y9i2sEN9iKZg1o"})
    if description_element and description_element.text:
        result["extracted_bio"] = description_element.text.strip()
        if full_name and full_name.lower() in result["extracted_bio"].lower():
            result["confidence"] += 0.2
            result["matches"].append("Full name in bio")

    result["confidence"] = round(result["confidence"], 2)
    return result

async def _parse_medium_profile(html: str, username: str, full_name: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    result = {"exists": True, "url": f"https://medium.com/@{username}", "confidence": 0.0, "matches": []}

    if soup.title and username.lower() in soup.title.string.lower():
        result["confidence"] += 0.3
        result["matches"].append("Username in title")

    page_full_name_element = soup.find("h1")
    if page_full_name_element:
        page_full_name = page_full_name_element.text.strip()
        if page_full_name:
            result["extracted_full_name"] = page_full_name
            if full_name and (full_name.lower() in page_full_name.lower() or page_full_name.lower() in full_name.lower()):
                result["confidence"] += 0.4
                result["matches"].append("Full name match")

    result["confidence"] = round(result["confidence"], 2)
    return result
