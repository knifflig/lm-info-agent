
from urllib.parse import urlparse

def apply_feed_rules(url, hostname):
    feed_urls = set()

    if 'reddit.com' in hostname:
        # example: https://reddit.com/r/python
        feed_urls.add(url.rstrip('/') + '.rss')

    elif 'youtube.com' in hostname:
        # example: https://www.youtube.com/channel/UC12345
        if 'channel/' in url:
            channel_id = url.split('channel/')[1].split('/')[0]
            feed_urls.add(f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}")

    elif 'github.com' in hostname:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) >= 2:
            user, repo = path_parts[0], path_parts[1]
            base = f"{parsed.scheme}://{parsed.netloc}/{user}/{repo}"
            feed_urls.update({
                f"{base}/commits.atom",
                f"{base}/releases.atom",
                f"{base}/tags.atom",
            })

    return feed_urls
