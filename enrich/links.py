import re
import httpx
from bs4 import BeautifulSoup

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

async def extract_emails_from_url(url):
    found = set()
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.get(url)
        soup = BeautifulSoup(r.text, "html.parser")
        text = soup.get_text(" ")
        for m in EMAIL_RE.findall(text):
            found.add(m.lower())
    return list(found)
