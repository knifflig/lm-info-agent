# lm-info-agent: RSS Discovery Submodule

A submodule within the `lm-info-agent` monorepo for robust discovery of RSS/Atom feeds from arbitrary websites. This component integrates a multi-stage pipeline—combining path guessing, HTML parsing, domain-specific heuristics, sitemap crawling, and search API fallbacks—to reliably locate real-world feed URLs as part of our labor-market information agent.

---

## Table of Contents

- [lm-info-agent: RSS Discovery Submodule](#lm-info-agent-rss-discovery-submodule)
  - [Table of Contents](#table-of-contents)
  - [Context \& Placement](#context--placement)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [Command-Line Interface (CLI)](#command-line-interface-cli)
    - [Python API](#python-api)
  - [Submodule Structure](#submodule-structure)
  - [Logging \& Error Handling](#logging--error-handling)
  - [Contributing \& Testing](#contributing--testing)

---

## Context & Placement

This is **not** a standalone library, but a submodule of the `lm-info-agent` monorepo, located at:

```
lm-info-agent/
├── info_agent/
│   ├── rss_discovery/          ← this submodule
│   └── ...other components...
└── ...root-level files...
```

Integration points:

* Imported by the main crawler orchestrator to enrich feed discovery.
* Shares root-level virtual environment and dependencies.

---

## Configuration

1. Ensure you have the monorepo dependencies installed in your root environment:

   ```bash
   cd lm-info-agent
   pip install -r requirements.txt
   ```
2. Add your Brave Search API key to the root `.env` file:

   ```ini
   BRAVE_SEARCH_API_KEY=your_api_key_here
   ```

---

## Usage

### Command-Line Interface (CLI)

Navigate into the submodule and run the main script:

```bash
cd info_agent/rss_discovery
python main.py https://www.example.com
```

**Example:**

```
$ python main.py www.bundesregierung.de
Discovered feeds for www.bundesregierung.de:
 - https://www.bundesregierung.de/service/rss/breg-de/1151242/feed.xml
```

### Python API

Within any part of the `info_agent` package, import and call:

```python
from info_agent.rss_discovery.main import discover_rss_feeds

feeds = discover_rss_feeds("https://www.example.com")
for url in feeds:
    print(url)
```

---

## Submodule Structure

```
info_agent/rss_discovery/
├── main.py                # Orchestrator with five-stage discovery pipeline
├── utils/                 # Helper modules
│   ├── url_normalizer.py  # normalize_to_base_url()
│   ├── common_feed_paths.py  # COMMON_FEED_PATHS & filter_rss_links()
│   ├── html_parser.py     # parse_html_for_feeds()
│   ├── rules.py           # apply_feed_rules()
│   ├── site_map_loader.py # sitemap parsing & feed filtering
│   └── rss_feed_search.py # Brave Search API integration
└── tests/                 # Unit tests for each discovery component
```

**Discovery Steps in `discover_rss_feeds()`:**

1. Scan common feed paths
2. Parse HTML `<link>` tags
3. Apply domain heuristics
4. Fallback: sitemap discovery
5. Fallback: search API discovery

---

## Logging & Error Handling

* Uses a named logger (`scraper`) configured at `INFO` level by default.
* Detailed `logger.debug`, `info`, `warning`, `error`, and `exception` calls.
* Distinguishes between HTTP errors (`requests.RequestException`) and unexpected exceptions.
* Propagates irrecoverable failures via `RSSDiscoveryError`.

---

## Contributing & Testing

* **Testing:**

  * Unit tests live under `info_agent/rss_discovery/tests/`.
  * Run with:

    ```bash
    pytest info_agent/rss_discovery/tests
    ```

* **Contributing:**

  1. Fork the monorepo, create a feature branch.
  2. Implement & test improvements in `rss_discovery/`.
  3. Submit a pull request referencing relevant issue(s).

---

*This submodule empowers the labor-market information agent with comprehensive feed discovery capabilities, ensuring no relevant source is missed.*
