# src/scraper/scrape_content.py
"""
Fetch and extract main textual content from a news article URL using ProxyCrawl + Readability.
"""
import os
import requests
from readability import Document
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any, List
import warnings
# Suppress SyntaxWarnings from newspaper package internals (invalid escape sequences)
warnings.filterwarnings('ignore', category=SyntaxWarning, module=r'newspaper.*')
from newspaper import Article

# ProxyCrawl RapidAPI configuration
API_URL = "https://proxycrawl-crawling.p.rapidapi.com/"
API_HOST = "proxycrawl-crawling.p.rapidapi.com"
API_KEY = os.getenv("PROXYCRAWL_RAPIDAPI_KEY")


def scrape_content_raw(url: str, render: bool = False, timeout: int = 30) -> Optional[Dict[str, Any]]:
    if not API_KEY:
        raise RuntimeError("Missing PROXYCRAWL_RAPIDAPI_KEY environment variable")

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }
    params: Dict[str, Any] = {"url": url, "format": "json"}
    if render:
        params["render"] = "true"

    response = requests.get(API_URL, headers=headers, params=params, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    return {
        "url": data.get("url"),
        "status": data.get("original_status"),
        "html": data.get("body")
    }


def extract_text(html: str) -> Dict[str, str]:
    doc = Document(html)
    title = doc.title()
    content_html = doc.summary()
    soup = BeautifulSoup(content_html, 'html.parser')
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
    text = "\n\n".join(paragraphs).strip()
    return {"title": title, "text": text}


def scrape_and_extract(feed_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    article_link = feed_item.get('article_link')
    if not article_link:
        print(f"scrape_and_extract: no article link found in rss feed item: {feed_item}")
        return None

    try:
        article = Article(article_link, language='de')
        article.download()
        article.parse()
    except Exception as e:
        print(f"Error processing article at {article_link}: {e}")
        return None

    # Clean the article_summary HTML
    summary_html = feed_item.get('article_summary')
    summary_text = extract_text(summary_html)

    return {
        'article_id': feed_item.get('article_id'),
        'article_title': article.title,
        'article_published_date': feed_item.get('article_published_date'),
        'article_link': article_link,
        'article_summary': summary_text,
        'rss_meta': {
            'rss_code': feed_item.get('rss_code'),
            'rss_prefix': feed_item.get('rss_prefix'),
            'rss_branch': feed_item.get('rss_branch'),
            'rss_sub': feed_item.get('rss_sub'),
        },
        'article_text': article.text
    }


def scrape_rss_content(feed_list: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    aggregated: Dict[str, Dict[str, Any]] = {}
    for entry in feed_list:
        article_link = entry.get('article_link')
        if not article_link:
            raise ValueError
        enriched = scrape_and_extract(entry)
        if enriched:
            aggregated[article_link] = enriched
        else:
            raise ValueError
    return aggregated
