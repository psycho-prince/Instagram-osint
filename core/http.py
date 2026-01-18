import httpx
import random
import asyncio

HEADERS = [
    {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; Pixel 6)",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "198387",
    }
]

class AsyncHTTP:
    def __init__(self, debug=False):
        self.debug = debug

    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=random.choice(HEADERS),
            timeout=20,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    async def get(self, url, cookies=None):
        r = await self.client.get(url, cookies=cookies)
        return r
