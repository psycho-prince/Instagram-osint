import json
import httpx


def load_cookies(raw_cookie: str | None, cookies_file: str | None) -> dict:
    """
    Load cookies from:
    - raw cookie string (--cookie)
    - cookies.json (--cookies-file)
    Returns a dict suitable for httpx / requests
    """
    cookies = {}

    if raw_cookie:
        parts = raw_cookie.split(";")
        for p in parts:
            if "=" in p:
                k, v = p.strip().split("=", 1)
                cookies[k] = v

    elif cookies_file:
        with open(cookies_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Accept both formats:
        # 1) {"sessionid": "..."}
        # 2) Chrome export list [{name,value}, ...]
        if isinstance(data, dict):
            cookies.update(data)
        elif isinstance(data, list):
            for c in data:
                if "name" in c and "value" in c:
                    cookies[c["name"]] = c["value"]

    return cookies


async def check_cookie_health(cookies: dict, debug: bool = False) -> bool:
    """
    Lightweight check to confirm Instagram accepts the cookie.
    No scraping, no heavy endpoint.
    """
    url = "https://www.instagram.com/accounts/edit/"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 13) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Mobile Safari/537.36"
        ),
        "Accept": "text/html",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(
        headers=headers,
        cookies=cookies,
        follow_redirects=True,
        timeout=15,
    ) as client:
        r = await client.get(url)

    if debug:
        print(f"[DEBUG] Cookie health HTTP {r.status_code}")

    # Logged-in users do NOT get redirected to /login
    return r.status_code == 200 and "login" not in str(r.url)
