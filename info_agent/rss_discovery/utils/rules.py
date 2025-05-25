
def apply_feed_rules(url, hostname):
    feed_urls = set()
    if 'reddit.com' in hostname:
        if url.endswith('/'):
            feed_urls.add(url + '.rss')
        else:
            feed_urls.add(url + '/.rss')
    elif 'youtube.com' in hostname:
        if '/channel/' in url:
            channel_id = url.split('/channel/')[1].split('/')[0]
            feed_urls.add(f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}')
    elif 'github.com' in hostname:
        parts = url.strip('/').split('/')
        if len(parts) >= 2:
            base = f'https://github.com/{parts[0]}/{parts[1]}'
            feed_urls.update({
                base + '/commits.atom',
                base + '/releases.atom',
                base + '/tags.atom'
            })
    return feed_urls
