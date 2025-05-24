# lm-info-agent

A prototype Python project to periodically fetch, store, and process RSS feeds from key stakeholders in the German labor market. The system is organized into modular components for scraping, storage, orchestration, and content writing.

## Project Structure

```
lm-info-agent/                      # Root directory
├── README.md                        # Project overview & setup instructions
├── LICENSE                          # Project license
├── pyproject.toml                   # Python dependencies & build config
├── feeds_list.csv                   # CSV of RSS feed URLs with metadata
├── info_agent/                      # Source code modules
│   ├── info_agent/                  # Central orchestrator
│   │   ├── __init__.py
│   │   ├── main.py                  # Entry point for scheduling workflows
│   │   └── utils.py                 # Logging, configuration
│   ├── scraper/                     # RSS feed fetching
│   │   ├── __init__.py
│   │   ├── main.py                  # Fetch and parse RSS feeds
│   │   └── utils.py                 # HTTP client, retry logic, parser helpers
│   ├── storage/                     # Persistence layer
│   │   ├── __init__.py
│   │   ├── main.py                  # Save and query entries (e.g., SQLite)
│   │   └── utils.py                 # Schema definitions, migrations
│   └── writer/                      # Report and summary generation
│       ├── __init__.py
│       ├── main.py                  # Generate summaries and export results
│       └── utils.py                 # Template rendering, export helpers
└── tests/                           # Unit tests for each component
    ├── test_info_agent.py
    ├── test_scraper.py
    ├── test_storage.py
    └── test_writer.py
```

## Getting Started

1. **Clone the repository**

   ```bash
   git clone <repo-url> lm-info-agent
   cd lm-info-agent
   ```

2. **Set up the environment**

   ```bash
   flox activate
   ```

## Next Steps

* Implement incremental fetching in `scraper` to skip already-seen entries.
* Define database schema and migrations in `storage` module.
* Add detailed logging and error handling across all subsystems.
* Write unit tests for edge cases and failure scenarios.
* Integrate scheduling (e.g., cron or APScheduler) in `info_agent/main.py`.
