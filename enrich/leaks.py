# enrich/leaks.py
import httpx
from bs4 import BeautifulSoup

SEARCH_QUERIES = [
    "site:pastebin.com {u}",  # Direct Pastebin search
    "site:ghostbin.com {u}",  # Direct Ghostbin search
    "site:github.com {u}",
    "site:reddit.com {u}",
    "\"{u}\" \"password\"",
    "\"{u}\" \"leak\"",
]

SENSITIVE_KEYWORDS = ["password", "email", "secret", "token", "api_key", "泄漏"]


async def _search_bing(query: str, debug: bool = False) -> list[str]:
    """
    Searches Bing for the given query and extracts URLs.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 13) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Mobile Safari/537.36"
        )
    }
    url = "https://www.bing.com/search?q=" + query.replace(" ", "+")
    found_urls = []

    async with httpx.AsyncClient(
        headers=headers,
        follow_redirects=True,
        timeout=15,
    ) as client:
        try:
            r = await client.get(url)
            if debug:
                print(f"[DEBUG] Bing search for '{query}' HTTP {r.status_code}")

            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                # Bing search results usually have links under <a> tags with specific classes
                # This might need adjustment if Bing's HTML structure changes
                for link in soup.find_all("a", href=True):
                    href = link["href"]
                    # Filter for actual search result links, not internal Bing links
                    if href.startswith("http") and "bing.com/videos" not in href and "bing.com/images" not in href and "microsoft.com" not in href:
                        found_urls.append(href)
        except Exception as e:
            if debug:
                print(f"[DEBUG] Bing search error for '{query}': {e}")
    return found_urls


async def _analyze_pastebin_content(url: str, username: str, debug: bool = False) -> dict | None:
    """
    Fetches content from a Pastebin-like URL and analyzes it for sensitive keywords.
    """
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
        timeout=10,
    ) as client:
        try:
            r = await client.get(url)
            if debug:
                print(f"[DEBUG] Fetching Pastebin content from '{url}' HTTP {r.status_code}")

            if r.status_code == 200:
                # Pastebin raw content is usually at /raw/PASTE_ID
                # Or it's directly in the <pre> tag on the page
                content = ""
                if "/raw/" in url:
                    content = r.text
                else:
                    soup = BeautifulSoup(r.text, "html.parser")
                    pre_tag = soup.find("pre", class_="source")
                    if pre_tag:
                        content = pre_tag.get_text()
                    else: # Fallback for other structures
                        content = r.text # If no specific pre tag, just get all text
                        
                found_keywords = [kw for kw in SENSITIVE_KEYWORDS if kw in content.lower()]
                if found_keywords or username.lower() in content.lower():
                    return {
                        "url": url,
                        "found_username": username.lower() in content.lower(),
                        "found_keywords": found_keywords,
                        "snippet": content[:500], # Store a snippet for context
                    }
        except Exception as e:
            if debug:
                print(f"[DEBUG] Error fetching/analyzing Pastebin content from '{url}': {e}")
    return None


async def check_leak_signals(username: str, debug: bool = False) -> dict:
    """
    Leak signal detection, including Pastebin searches.
    """
    leaks = {
        "bing_signals": [],
        "pastebin_leaks": [],
    }

    # Perform general Bing searches for leak signals
    for q in SEARCH_QUERIES:
        query = q.format(u=username)
        
        # Special handling for Pastebin/Ghostbin queries to extract URLs
        if "site:pastebin.com" in q or "site:ghostbin.com" in q:
            bing_urls = await _search_bing(query, debug)
            for url in bing_urls:
                if "pastebin.com" in url or "ghostbin.com" in url: # Double check the domain
                    # Try to get raw version of pastebin link if not already raw
                    if "pastebin.com/" in url and not "pastebin.com/raw/" in url:
                        paste_id = url.split("pastebin.com/")[-1]
                        if len(paste_id) > 0: # Ensure paste ID exists
                           url = f"https://pastebin.com/raw/{paste_id}"
                    
                    paste_data = await _analyze_pastebin_content(url, username, debug)
                    if paste_data:
                        leaks["pastebin_leaks"].append(paste_data)
        else:
            # Original logic for general signals
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 13) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/121.0.0.0 Mobile Safari/537.36"
                )
            }
            async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15) as client:
                try:
                    r = await client.get("https://www.bing.com/search?q=" + query.replace(" ", "+"))
                    if r.status_code == 200 and username.lower() in r.text.lower():
                        leaks["bing_signals"].append({
                            "query": query,
                            "engine": "bing",
                        })
                except Exception as e:
                    if debug:
                        print(f"[DEBUG] Leak query failed: {query} → {e}")

    if debug:
        print(f"[DEBUG] Total leak signals found (Bing): {len(leaks['bing_signals'])}")
        print(f"[DEBUG] Total Pastebin leaks found: {len(leaks['pastebin_leaks'])}")

    return leaks
