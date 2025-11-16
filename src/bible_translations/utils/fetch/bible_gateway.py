from typing import Optional

import aiohttp
from bs4 import BeautifulSoup

from bible_translations.constants import BIBLE_GATEWAY_BASE_URL
from bible_translations.utils.logger import logger


class BibleGatewayClient:
    """Async client for fetching pages from BibleGateway."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def fetch(self, query: str) -> BeautifulSoup:
        """Fetch and parse the HTML for a passage."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        url = f"{BIBLE_GATEWAY_BASE_URL}?search={query}"
        logger.debug(f"URL: {url}")
        async with self.session.get(url) as resp:
            if resp.status != 200:
                raise RuntimeError(f"HTTP {resp.status} when fetching: {url}")
            html = await resp.text()
            return BeautifulSoup(html, "html.parser")
