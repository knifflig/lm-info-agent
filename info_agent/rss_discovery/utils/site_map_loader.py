from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import requests
import gzip
from io import BytesIO

from rss_discovery.utils.url_normalizer import normalize_to_base_url
from rss_discovery.utils.common_feed_paths import filter_rss_links

def extract_sitemaps_from_robots(raw_url: str) -> list[str]:
    """Fetch and parse /robots.txt to extract sitemap URLs."""
    base_url = normalize_to_base_url(raw_url)
    robots_url = base_url.rstrip('/') + '/robots.txt'
    sitemaps = []

    try:
        r = requests.get(robots_url, timeout=5)
        lines = r.text.splitlines()
        for line in lines:
            if line.lower().startswith("sitemap:"):
                _, sitemap_url = line.split(":", 1)
                sitemaps.append(sitemap_url.strip())
    except Exception as e:
        print(f"Error fetching robots.txt: {e}")

    return sitemaps


def decompress_gzip_content(response: requests.Response) -> bytes | None:
    """Attempt to decompress a .gz-compressed HTTP response."""
    try:
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
            return gz.read()
    except Exception as e:
        print(f"Error decompressing gzip content from {response.url}: {e}")
        return None


def extract_links_from_sitemap(sitemap_url: str, recursive: bool = True, depth: int = 1) -> list[str]:
    """
    Parse sitemap or sitemap index and return all <loc> URLs.
    Supports .gz files by delegating decompression to decompress_gzip_content().
    """
    links = []
    try:
        r = requests.get(sitemap_url, timeout=10)
        content_type = r.headers.get('Content-Type', '')

        # Decompress if it's a .gz file
        if sitemap_url.endswith('.gz') or 'application/x-gzip' in content_type:
            content = decompress_gzip_content(r)
            if not content:
                return links
        else:
            content = r.content

        soup = BeautifulSoup(content, 'xml')
        loc_tags = soup.find_all('loc')

        for loc in loc_tags:
            url = loc.text.strip()
            if recursive and depth > 0 and (url.endswith('.xml') or url.endswith('.xml.gz')):
                nested = extract_links_from_sitemap(url, recursive=True, depth=depth - 1)
                links.extend(nested)
            else:
                links.append(url)

    except Exception as e:
        print(f"Error processing sitemap {sitemap_url}: {e}")

    return links

def extract_all_sitemap_links(domain_or_url: str, depth: int = 1) -> list[str]:
    """
    Combines all links found in all sitemaps discovered via robots.txt into one deduplicated list.
    Recursively follows nested sitemaps up to `depth` levels.
    """
    all_links = set()
    base_url = normalize_to_base_url(domain_or_url)
    sitemaps = extract_sitemaps_from_robots(base_url)

    for sitemap_url in sitemaps:
        links = extract_links_from_sitemap(sitemap_url, recursive=True, depth=depth)
        all_links.update(links)

    return sorted(all_links)

def extract_rss_from_sitemap(domain_or_url: str, depth: int = 10) -> list[str]:
    base_url = normalize_to_base_url(domain_or_url)
    sitemap_urls = extract_all_sitemap_links(base_url, depth = depth)
    return filter_rss_links(sitemap_urls)
