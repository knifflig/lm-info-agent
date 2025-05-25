
from bs4 import BeautifulSoup
from urllib.parse import urljoin

RSS_MIME_TYPES = {
    'application/rss+xml',
    'application/atom+xml',
    'application/rss&#re;xml',
    'application/atom&#re;xml',
}

def parse_html_for_feeds(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    feed_links = set()
    for link in soup.find_all('link', rel='alternate'):
        if link.get('type', '').lower() in RSS_MIME_TYPES and link.get('href'):
            feed_links.add(urljoin(base_url, link['href']))
    return feed_links
