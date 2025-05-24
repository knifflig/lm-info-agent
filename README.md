# RSS-Feed-Scraper für Arbeitsmarkt‑DEU

Dieses Python‑Projekt stellt einen ersten Prototypen dar, um automatisch RSS‑Feeds von Stakeholdern im deutschen Arbeitsmarkt abzurufen und die neuesten Beiträge systematisch zu laden.

## Projektstruktur

```
rss_scraper/                      # Wurzelverzeichnis\│
├── README.md                     # Projektbeschreibung & Setup
├── requirements.txt              # Python-Abhängigkeiten
├── feeds_list.csv                # Liste der RSS-Feed-URLs mit Metadaten
├── src/                          # Quellcode
│   ├── __init__.py
│   ├── scraper.py                # Hauptskript zum Abruf und Speichern der Feeds
│   ├── storage.py                # Module zur Persistenz (z.B. SQLite)
│   └── utils.py                  # Hilfsfunktionen (Logging, Config)
└── tests/                        # Unit-Tests für einzelne Module
    ├── test_scraper.py
    └── test_storage.py
```

## Erste Schritte

1. Klonen des Repositories und Wechsel ins Projektverzeichnis:

   ```bash
   git clone <repo-url> rss_scraper
   cd rss_scraper
   ```

2. Installation der Abhängigkeiten:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Ausführen des Scrapers:

   ```bash
   python -m src.scraper
   ```

## Nächste Meilensteine

* Implementierung von `scraper.py`:

  * Einlesen von `feeds_list.csv`
  * Abrufen aller Feeds mit `feedparser`
  * Filtern und Speichern nur neuer Einträge (z.B. anhand `id` und `published`)
* Aufbau einer Speicherschicht in `storage.py` (z.B. SQLite)
* Logging und Error-Handling in `utils.py`
* Erste Unit-Tests im Verzeichnis `tests/`

„Möchtest du eine Review‑Runde für *README.md* starten?“
