from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import requests
import gzip
from io import BytesIO
import signal
from typing import List

from rss_discovery.utils.url_normalizer import normalize_to_base_url
from rss_discovery.utils.common_feed_paths import filter_rss_links

class TotalTimeoutError(Exception):
    """Raised when extract_rss_from_sitemap exceeds total allowed time."""
    pass

def _total_timeout_handler(signum, frame):
    raise TotalTimeoutError("extract_rss_from_sitemap exceeded total_timeout")


def extract_sitemaps_from_robots(
    raw_url: str,
    timeout: float = 30.0,
) -> list[str]:
    """
    Fetch and parse /robots.txt to extract all 'Sitemap:' entries.
    :param raw_url: A domain or URL to normalize.
    :param timeout: Request timeout in seconds.
    :return: List of sitemap URLs declared in robots.txt.
    """
    base_url = normalize_to_base_url(raw_url)
    robots_url = base_url.rstrip('/') + '/robots.txt'
    sitemaps: list[str] = []

    try:
        r = requests.get(robots_url, timeout=timeout)
        for line in r.text.splitlines():
            if line.lower().startswith("sitemap:"):
                _, sitemap_url = line.split(":", 1)
                sitemaps.append(sitemap_url.strip())
    except Exception as e:
        print(f"Error fetching robots.txt from {robots_url}: {e}")

    return sitemaps


def decompress_gzip_content(response: requests.Response) -> bytes | None:
    """Attempt to decompress a .gz-compressed HTTP response."""
    try:
        with gzip.GzipFile(fileobj=BytesIO(response.content)) as gz:
            return gz.read()
    except Exception as e:
        print(f"Error decompressing gzip content from {response.url}: {e}")
        return None


def extract_links_from_sitemap(
    sitemap_url: str,
    recursive: bool = True,
    depth: int = 1,
    timeout: float = 30.0,
) -> list[str]:
    """
    Parse a sitemap (or sitemap index) and return all <loc> URLs.
    Supports .gz files by delegating decompression to decompress_gzip_content().
    :param sitemap_url: URL of the sitemap or sitemap index.
    :param recursive: Whether to follow nested sitemap files.
    :param depth: How many levels of nested sitemap files to follow.
    :param timeout: Request timeout in seconds.
    :return: List of URLs found in this sitemap (and nested ones, if enabled).
    """
    links: list[str] = []
    try:
        r = requests.get(sitemap_url, timeout=timeout)
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
                nested = extract_links_from_sitemap(
                    url,
                    recursive=True,
                    depth=depth - 1,
                    timeout=timeout,
                )
                links.extend(nested)
            else:
                links.append(url)

    except Exception as e:
        print(f"Error processing sitemap {sitemap_url}: {e}")

    return links

def extract_all_sitemap_links(
    domain_or_url: str,
    depth: int = 1,
    timeout: float = 30.0,
) -> list[str]:
    """
    Combines all links found in all sitemaps discovered via robots.txt into one deduplicated list.
    Recursively follows nested sitemaps up to `depth` levels.

    :param domain_or_url: The site’s domain or URL to normalize.
    :param depth: How many levels of nested sitemap files to follow.
    :param timeout: Request timeout in seconds (passed to downstream sitemap-fetching functions).
    :return: Sorted list of unique URLs found in all sitemaps.
    """
    all_links: set[str] = set()
    base_url = normalize_to_base_url(domain_or_url)

    # Make sure extract_sitemaps_from_robots can accept timeout
    sitemaps = extract_sitemaps_from_robots(base_url, timeout=timeout)

    for sitemap_url in sitemaps:
        # And extract_links_from_sitemap too
        links = extract_links_from_sitemap(
            sitemap_url,
            recursive=True,
            depth=depth,
            timeout=timeout,
        )
        all_links.update(links)

    return sorted(all_links)

def extract_rss_from_sitemap(
    domain_or_url: str,
    depth: int = 10,
    request_timeout: float = 5.0,
    total_timeout: float = 30.0,
) -> List[str]:
    """
    Crawl the sitemap(s) of a domain (or URL) and return only the RSS feed URLs,
    but abort entirely if it takes longer than total_timeout seconds.

    :param domain_or_url: The site’s domain or a full URL to normalize.
    :param depth: How many levels of nested sitemap-index files to follow.
    :param timeout: Per-request timeout in seconds.
    :param total_timeout: Maximum total runtime for this function in seconds.
    :raises TotalTimeoutError: If overall execution exceeds total_timeout.
    :return: List of RSS feed URLs found.
    """
    # Install our alarm handler
    signal.signal(signal.SIGALRM, _total_timeout_handler)
    # Schedule an alarm in total_timeout seconds
    # (for fractional seconds you could use setitimer instead)
    signal.alarm(int(total_timeout))

    try:
        base_url = normalize_to_base_url(domain_or_url)
        sitemap_urls = extract_all_sitemap_links(
            base_url,
            depth=depth,
            timeout=request_timeout,
        )
        rss_links = filter_rss_links(sitemap_urls)
    finally:
        # Always cancel any pending alarm
        signal.alarm(0)

    return rss_links
