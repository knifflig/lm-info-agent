import requests
from urllib.parse import urlparse, urljoin
import logging
from typing import Set

from rss_discovery.utils.common_feed_paths import COMMON_FEED_PATHS
from rss_discovery.utils.html_parser import parse_html_for_feeds
from rss_discovery.utils.rules import apply_feed_rules
from rss_discovery.utils.url_normalizer import normalize_to_base_url
from rss_discovery.utils.site_map_loader import extract_rss_from_sitemap
from rss_discovery.utils.rss_feed_search import extract_rss_with_search
from rss_discovery.utils.rss_dicovery_logger import logger

class RSSDiscoveryError(Exception):
    """Custom exception for errors during RSS discovery."""

def discover_rss_feeds(raw_url: str) -> Set[str]:
    """
    Discover RSS/Atom feeds for a given URL using multiple strategies.
    Returns a set of discovered feed URLs.
    """
    discovered_feeds: Set[str] = set()
    session = requests.Session()
    session.headers.update({"User-Agent": "rss_discovery/1.0"})

    # Normalize the input URL
    try:
        base_url = normalize_to_base_url(raw_url)
        logger.info("Normalized URL '%s' to '%s'", raw_url, base_url)
    except Exception as e:
        logger.exception("Failed to normalize URL: %s", raw_url)
        raise RSSDiscoveryError(f"URL normalization failed for '{raw_url}'") from e

    # 1. Try common feed paths
    logger.debug("Checking common feed paths")
    for path in COMMON_FEED_PATHS:
        full_url = urljoin(base_url, path)
        try:
            resp = session.get(full_url, timeout=5)
            resp.raise_for_status()
            ct = resp.headers.get("Content-Type", "")
            if any(keyword in ct for keyword in ("xml", "rss", "atom")):
                discovered_feeds.add(resp.url)
                logger.info("Found feed via common path: %s", resp.url)
        except requests.RequestException as e:
            logger.debug("Common path check failed for %s: %s", full_url, e)
        except Exception as e:
            logger.exception("Unexpected error checking path %s", full_url)

    # 2. Parse HTML <link> tags
    logger.debug("Parsing HTML <link> tags at %s", base_url)
    try:
        resp = session.get(base_url, timeout=5)
        resp.raise_for_status()
        feeds = parse_html_for_feeds(resp.text, base_url)
        for feed in feeds:
            discovered_feeds.add(feed)
            logger.info("Found feed via HTML link tag: %s", feed)
    except requests.RequestException as e:
        logger.warning("Failed to fetch base URL for HTML parsing: %s", e)
    except Exception as e:
        logger.exception("Error during HTML feed parsing")

    # 3. Apply domain-specific rules
    try:
        hostname = urlparse(base_url).hostname or ""
        logger.debug("Applying domain-specific rules for hostname: %s", hostname)
        feeds = apply_feed_rules(base_url, hostname)
        for feed in feeds:
            discovered_feeds.add(feed)
            logger.info("Found feed via domain rule: %s", feed)
    except Exception as e:
        logger.exception("Error applying domain-specific rules")

    # 4. Fallback: sitemap discovery
    if not discovered_feeds:
        logger.debug("No feeds found; attempting sitemap fallback")
        try:
            feeds = extract_rss_from_sitemap(raw_url)
            for feed in feeds:
                discovered_feeds.add(feed)
                logger.info("Found feed via sitemap: %s", feed)
        except Exception as e:
            logger.exception("Error during sitemap fallback")

    # 5. Fallback: search API
    if not discovered_feeds:
        logger.debug("No feeds found; attempting search API fallback")
        try:
            feeds = extract_rss_with_search(raw_url)
            for feed in feeds:
                discovered_feeds.add(feed)
                logger.info("Found feed via search API: %s", feed)
        except Exception as e:
            logger.exception("Error during search API fallback")

    if not discovered_feeds:
        logger.error("No RSS feeds discovered for URL: %s", raw_url)

    return discovered_feeds

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        logger.error("Usage: python main.py <domain_or_url>")
        sys.exit(1)

    input_url = sys.argv[1]
    try:
        feeds = discover_rss_feeds(input_url)
        if feeds:
            print(f"Discovered feeds for {input_url}:")
            for feed in sorted(feeds):
                print(" -", feed)
        else:
            logger.error("No feeds found for %s", input_url)
            sys.exit(1)
    except RSSDiscoveryError as e:
        logger.error("RSS discovery failed: %s", e)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error in main execution")
        sys.exit(1)
