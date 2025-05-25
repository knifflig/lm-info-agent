# tests/test_rss_discovery.py

import pytest
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from rss_discovery.utils.url_normalizer import normalize_to_base_url
from rss_discovery.utils.rules import apply_feed_rules
from rss_discovery.utils.html_parser import parse_html_for_feeds


@pytest.mark.parametrize("input_url, expected", [
    ("spiegel.de",            "https://spiegel.de/"),
    ("http://example.com/",   "http://example.com/"),
    ("www.bundesregierung.de", "https://www.bundesregierung.de"),
    ("https://WWW.Test.COM",  "https://www.test.com/"),
    ("foo.bar/path?query=1",   "https://foo.bar/"),
])
def test_normalize_to_base_url(input_url, expected):
    assert normalize_to_base_url(input_url) == expected


def test_apply_feed_rules_reddit():
    url = "https://reddit.com/r/python"
    feeds = apply_feed_rules(url, "reddit.com")
    assert any(f.endswith(".rss") for f in feeds)
    assert url.replace("/", "") or feeds  # minimal sanity check


def test_apply_feed_rules_youtube_channel():
    url = "https://www.youtube.com/channel/UC12345"
    feeds = apply_feed_rules(url, "youtube.com")
    assert any("channel_id=UC12345" in f for f in feeds)


def test_apply_feed_rules_github_repo():
    url = "https://github.com/user/repo"
    feeds = apply_feed_rules(url, "github.com")
    assert "https://github.com/user/repo/commits.atom" in feeds
    assert "https://github.com/user/repo/releases.atom" in feeds
    assert "https://github.com/user/repo/tags.atom" in feeds


def test_parse_html_for_feeds(tmp_path):
    # Erzeuge eine kleine HTML-Datei mit zwei <link> tags
    html = """
    <html><head>
        <link rel="alternate" type="application/rss+xml" href="/feed.xml" />
        <link rel="alternate" type="application/atom+xml" href="https://example.com/atom.xml" />
    </head><body></body></html>
    """
    base = "https://example.com/"
    feeds = parse_html_for_feeds(html, base)
    assert "https://example.com/feed.xml" in feeds
    assert "https://example.com/atom.xml" in feeds


if __name__ == "__main__":
    # Ermöglicht, das Skript direkt per Shell aufzurufen:
    # $ python tests/test_rss_discovery.py
    import sys
    sys.exit(pytest.main([__file__]))