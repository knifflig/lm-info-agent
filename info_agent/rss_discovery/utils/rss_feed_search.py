
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv

from rss_discovery.utils.url_normalizer import normalize_to_base_url
from rss_discovery.utils.common_feed_paths import filter_rss_links

load_dotenv()
BRAVE_SEARCH_API_KEY = os.getenv("BRAVE_SEARCH_API_KEY")


def brave_search_rss_pages(raw_url: str, limit: int = 10) -> list[str]:
    base_url = normalize_to_base_url(raw_url)
    domain = base_url.replace("https://", "").replace("http://", "").strip("/")

    query = f"site:{domain} intitle:RSS"
    url = "https://api.search.brave.com/res/v1/web/search"

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_SEARCH_API_KEY
    }
    params = {
        "q": query,
        "count": limit
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        results = response.json()
        return [item["url"] for item in results.get("web", {}).get("results", [])]
    except Exception as e:
        print(f"Brave API error: {e}")
        return []


def extract_feed_links_from_body(url: str) -> list[str]:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        html = r.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(html, 'html.parser')
    candidates = set()
    feed_keywords = ['rss', 'feed', '.xml', 'atom']

    for a in soup.find_all('a', href=True):
        href = a['href']
        href_lower = href.lower()
        if any(keyword in href_lower for keyword in feed_keywords):
            full_url = urljoin(url, href)
            candidates.add(full_url)

    return list(candidates)


def extract_rss_with_search(raw_url: str, limit: int = 10,
                            valid_endings: list[str] = ['/rss.xml', '/feed.xml', '/atom.xml', '/index.xml', 'rss.xml']
                           ) -> list[str]:
    rss_pages = brave_search_rss_pages(raw_url, limit)
    rss_all_links = []

    for url in rss_pages:
        rss_feed_links = extract_feed_links_from_body(url)
        rss_all_links.extend(rss_feed_links)

    rss_like_urls = filter_rss_links(rss_all_links, valid_endings=valid_endings)
    return rss_like_urls
