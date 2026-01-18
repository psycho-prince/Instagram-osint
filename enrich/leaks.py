# enrich/leaks.py
import httpx

SEARCH_QUERIES = [
    "site:pastebin.com {u}",
    "site:ghostbin.com {u}",
    "site:github.com {u}",
    "site:reddit.com {u}",
    "\"{u}\" \"password\"\"",
    "\"{u}\" \"leak\"\"",
]


async def check_leak_signals(username: str, debug: bool = False) -> list:
    """
    Passive leak signal detection.
    DOES NOT scrape dumps or paid databases.
    Only checks public mention surfaces.

    Returns:
        List of dicts with query + source
    """

    signals = []

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 13) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Mobile Safari/537.36"
        )
    }

    async with httpx.AsyncClient(
        headers=headers,
        follow_redirects=True,
        timeout=15,
    ) as client:

        for q in SEARCH_QUERIES:
            query = q.format(u=username)
            url = "https://www.bing.com/search?q=" + query.replace(" ", "+")

            try:
                r = await client.get(url)
            except Exception as e:
                if debug:
                    print(f"[DEBUG] Leak query failed: {query} → {e}")
                continue

            if r.status_code != 200:
                continue

            if username.lower() in r.text.lower():
                signals.append({
                    "query": query,
                    "engine": "bing",
                })

    if debug:
        print(f"[DEBUG] Leak signals found: {len(signals)}")

    return signals
