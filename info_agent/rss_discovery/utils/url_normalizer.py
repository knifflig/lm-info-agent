import requests
from urllib.parse import urlparse, urljoin, urlunparse
from url_normalize import url_normalize

def normalize_to_base_url(raw_url: str) -> str:
    # Step 1: Normalize overall format
    normalized = url_normalize(raw_url)

    # Step 2: Parse the components
    parsed = urlparse(normalized)

    # Step 3: Build base URL (scheme + netloc)
    base_url = urlunparse((parsed.scheme, parsed.netloc, '/', '', '', ''))

    return base_url