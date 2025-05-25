# src/scraper/fetch_rss.py
"""
Main entrypoint for the RSS scraper.
Reads feeds_list.csv, parses feed_entries into JSON keyed by code,
then fetches each feed via a dedicated function and logs entry counts.
"""
import csv
import os
import json
from typing import Dict, Any, List, Optional

from scraper.utils import fetch_feed
from scraper.utils.scrape_logger import logger

# Default path to feed list
FEEDS_CSV = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'feeds_list.csv')


def load_rss_sources(path: str = FEEDS_CSV) -> Dict[str, Dict[str, Any]]:
    """
    Load and parse feed configurations from a CSV file with composite header.
    Expected header: prefix;branch;sub;code;name;description;rss_link
    Returns a dict keyed by code with metadata.
    """
    rss_entry: Dict[str, Dict[str, Any]] = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=';')
        header = next(reader)
        expected = ['prefix','branch','sub','code','name','description','rss_link']
        if [h.strip() for h in header] != expected:
            logger.error(f"Unexpected header format: {header}")
            raise ValueError("feeds_list.csv header must be: 'prefix;branch;sub;code;name;description;rss_link'")
        for row in reader:
            if len(row) < len(expected):
                logger.warning(f"Skipping malformed row: {row}")
                continue
            entry = dict(zip(expected, [col.strip() for col in row]))
            rss_entry[entry['code']] = entry
    logger.debug(f"Parsed {len(rss_entry)} rss entry from {path}")
    return rss_entry


def fetch_rss_feed(rss_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Fetches and returns entries for a given feed code.
    Logs errors and returns empty list on failure.
    """
    rss_code = rss_entry.get('code')
    rss_link = rss_entry.get('rss_link')
    if not rss_link:
        logger.warning(f"No RSS link provided for code {rss_link}")
        raise ValueError

    parsed = fetch_feed(rss_link)
    entries = parsed.get('entries', []) or []
    logger.info(f"[{rss_code}] Retrieved {len(entries)} entries from {rss_link}")

    feed_list = []
    for feed_entry in entries:
        article_link = feed_entry.get('link')
        feed = {
            'rss_code': rss_code,
            'rss_prefix': rss_entry.get('prefix'),
            'rss_branch': rss_entry.get('branch'),
            'rss_sub': rss_entry.get('sub'),
            'rss_link': rss_link,
            'article_id': feed_entry.get('id', article_link),
            'article_published_date': feed_entry.get('published'),
            'article_link': article_link,
            'article_summary': feed_entry.get('summary'),
        }
        feed_list.append(feed)

    return feed_list
