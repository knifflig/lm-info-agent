import re
from typing import List

RSS_ENDINGS = ['/rss.xml', '/feed.xml', '/atom.xml', '/index.xml', 'rss.xml']

COMMON_FEED_PATHS = [
    '/rss', '/rss/', '/rss.xml',
    '/feed', '/feed/', '/feed.xml',
    '/atom', '/atom.xml',
    '/index.rss', '/index.xml',
    'rss', 'rss/', 'rss.xml',
    'feed', 'feed/', 'feed.xml',
    'atom', 'atom.xml',
    'index.rss', 'index.xml',
]

RSS_FEED_PATTERNS = [
    re.compile(r'\.rss$', re.IGNORECASE),
    re.compile(r'\.xml$', re.IGNORECASE),
    re.compile(r'/feed$', re.IGNORECASE),
    re.compile(r'/rss$', re.IGNORECASE),
    re.compile(r'/rss/', re.IGNORECASE),
    re.compile(r'/rss-[a-z]+\.xml$', re.IGNORECASE),
]



def filter_rss_links(links: List[str], valid_endings: List[str] = RSS_ENDINGS) -> List[str]:
    return [link for link in links if any(link.endswith(ending) for ending in valid_endings)]


