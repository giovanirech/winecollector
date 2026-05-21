# WineCollector — Task List

## Tasks

| # | Title | Status | Complexity | Dependencies |
|---|-------|--------|------------|--------------|
| 01 | Project skeleton & tooling | completed | low | — |
| 02 | Config & async database wiring | completed | low | task_01 |
| 03 | User model & initial migration | completed | low | task_02 |
| 04 | Authentication backend (cookie JWT) | pending | medium | task_03 |
| 05 | Auth routes, base layout & first-run signup gate | pending | medium | task_04 |
| 06 | Wine model & migration | pending | low | task_03 |
| 07 | WineTasting model & migration | pending | low | task_06 |
| 08 | Pydantic schemas (wine, tasting, export, WineScrapedData) | pending | low | task_07 |
| 09 | URL normalizer & aging-potential parser | pending | low | task_01 |
| 10 | Image normalizer (Pillow → WebP) | pending | low | task_01 |
| 11 | Scraper service (httpx + BeautifulSoup) | pending | medium | task_08, task_09, task_10 |
| 12 | i18n display labels | pending | low | task_08 |
| 13 | Wine service (CRUD, duplicate detection, stock, search) | pending | high | task_08, task_09, task_11 |
| 14 | Cellar overview & wine detail UI | pending | high | task_05, task_12, task_13 |
| 15 | Add/edit wine flow (scrape, duplicate, manual, rescrape) | pending | high | task_14 |
| 16 | Export service & routes (JSON + CSV) | pending | medium | task_12, task_13 |
| 17 | Healthcheck endpoint & structured logging | pending | low | task_02 |
