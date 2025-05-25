# src/scraper/utils.py
"""
Utility functions for the RSS scraper:
- HTTP client with retries
- Feed parsing helpers
- Logging setup
"""
from typing import Any, Dict

import requests
import feedparser
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .scrape_logger import logger

def get_http_session(retries: int = 3, backoff_factor: float = 0.3) -> requests.Session:
    """
    Returns a requests.Session with retry logic.
    """
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_feed(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetches and parses an RSS feed, returns the parsed structure.
    """
    logger.info(f"Fetching feed: {url}")
    session = get_http_session()
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return {}

    parsed = feedparser.parse(resp.content)
    if parsed.bozo:
        logger.warning(f"Malformed feed at {url}, encountered bozo_exception: {parsed.bozo_exception}")
    return parsed