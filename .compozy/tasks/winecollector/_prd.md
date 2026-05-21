# PRD: WineCollector

## Overview

WineCollector is a personal wine cellar manager for buyers of [wine.com.br](https://wine.com.br), Brazil's largest online wine retailer. The product solves a specific recurring loss: when a wine goes out of stock on wine.com.br, the retailer removes the product page — taking with it the winery details, vintage, grape varieties, region, aging potential, organoleptic notes, and bottle image that the buyer relied on to remember and value the wine.

The user is a private collector who buys wines through wine.com.br (direct purchases and subscription clubs like Clube Wine / WineBox) and wants a personal archive of every bottle they own, immune to the retailer deleting it later. The product captures wine data on demand by scraping the product URL the user provides, stores it locally, and exposes it through a mobile-first interface that the user consults from the phone before opening a bottle.

The differentiator — and the reason WineCollector exists alongside mass-market apps like Vivino or CellarTracker — is the explicit framing of "your personal archive of wines you actually own, that no retailer can delete." This positioning is currently underserved: existing wine apps assume their own central database is the source of truth; none of them addresses the failure mode of a retailer scrubbing discontinued SKUs that the user has already bought.

## Goals

- **Cover 100% of the cellar**: every wine the user buys from wine.com.br can be archived in WineCollector within minutes of purchase, with metadata and image preserved even if the source page is later removed.
- **Make the archive credibly portable**: the user can export the full cellar to JSON and CSV at any time, demonstrating that the data is not locked into the app.
- **Resilient scraping with graceful fallback**: when the wine.com.br page is unreachable, removed, or its layout changed, the user can still record the wine manually and retry scraping later with the same or a different URL.
- **Mobile-first consultation**: the user can look up any wine on the phone in under 10 seconds before opening a bottle.
- **Foundation for tasting and drinking-window features**: the V1 data model and UX patterns are designed so that Phase 2 (tasting notes) and Phase 3 (drinking window) can be added without rework.

## User Stories

### Primary persona — The Personal Collector

This is the single user the MVP is built for: a buyer of wine.com.br who keeps a modest-to-medium personal cellar (typically tens to a few hundred bottles), values the wines they own, and wants a digital record they control.

- As a personal collector, I want to **add a wine by pasting its wine.com.br URL** so that I do not have to retype the name, vintage, grapes, region, aging notes, and image by hand.
- As a personal collector, I want the app to **scrape the wine.com.br page automatically** so that the data and image are preserved locally before the retailer takes the page down.
- As a personal collector, I want a **clear warning when scraping fails** along with the option to fill in the missing fields manually so that I never lose the chance to archive a wine just because of a server error.
- As a personal collector, I want to **retry scraping** later with the same URL or a different URL for the same wine, so that I can recover from transient failures or relocated pages.
- As a personal collector, when I buy the **same wine twice**, I want the app to detect it and offer to **increment my stock by +1** instead of creating a duplicate.
- As a personal collector, I want to **see my cellar at a glance** on my phone, with a search box and filters by grape, type, and stock availability, so that I can find a specific wine in seconds before opening it.
- As a personal collector, I want to **decrement stock by -1** when I open a bottle, so that the app reflects what is actually in the cellar.
- As a personal collector, I want to **export my entire cellar** to JSON and CSV with one click, so that I can keep an off-app backup and prove that the data is mine.
- As a personal collector, I want **all UI text in Portuguese (pt-BR)** so that the interface feels native to my buying context.

### Secondary persona — The Future Collaborator (deferred to Phase 4+)

Multi-user is out of scope for the MVP but the architecture is built single-user-with-auth so that future household sharing remains possible without rewrite.

## Core Features

### Feature 1: Wine catalog with on-demand scraping (P0)

The user pastes a wine.com.br product URL into the "Add Wine" screen. The app fetches the page, parses every available field, downloads the bottle image, and stores everything in the local cellar. The user sees the parsed result and can confirm or adjust before saving.

**Fields captured (all optional — wine.com.br pages do not always include every field; missing ones are stored as blank and remain editable):**

Identidade:
- **Nome do vinho** — full product name.
- **Imagem do vinho** — bottle image, downloaded locally.
- **URL original** — source page on wine.com.br (system field; not user-editable on the wine detail page beyond the re-scrape flow).

Ficha técnica:
- **Uvas** — grape composition as free text to preserve nuance (e.g., "Chardonnay" or "39% Zinfandel, 18% Alicante Bouschet, 14% Petite Sirah, 13% Cabernet Sauvignon, 11% Petit Verdot e 5% Outras uvas").
- **Tipo do vinho** — categorical: tinto, branco, rosé, licoroso, espumante, frisante (and other types as they appear on the source).
- **País** — country of origin.
- **Região** — region/appellation.
- **Classificação** — sugar level: seco, meio seco, suave, doce.
- **Vinícola** — producer.
- **Safra** — vintage year.
- **Amadurecimento** — aging description as free text (e.g., "Em barricas de carvalho francês e americano." or "6 meses em barris de 2º uso de carvalho francês de tosta suave").
- **Teor alcoólico** — alcohol content (text, includes unit).
- **Temperatura de serviço** — serving temperature (text, includes unit).
- **Potencial de guarda (anos)** — aging potential stored as an integer number of years, ready to drive the Phase 3 drinking window calculation. The scraper attempts to extract a numeric value from the source page text using simple heuristics (e.g., "5 anos" → 5; "10 a 15 anos" → 15 — the upper bound; "Até 8 anos" → 8). When the source has no aging potential information, or the phrasing is non-numeric (e.g., "Pronto para beber"), the field is left blank. The user can edit the value manually at any time from the wine detail page.

Características organolépticas:
- **Visual** — appearance notes.
- **Olfativo** — aroma notes.
- **Gustativo** — palate notes.

Outros:
- **Comentário do Sommelier** — sommelier's note shown on some pages.
- **Harmonização** — food pairing suggestions shown on some pages.

System metadata (not user-facing as form fields, but visible on the wine detail page):
- **Status do scraping** — see the `scrape_status` rule below.
- **Estoque** — current stock count (editable via the +/- controls on the wine detail page; initialized at the moment of cadastro).
- **Data de compra** — purchase date (defaults to today on cadastro; editable).

**Scraping status rules:**
- The scraping operation marks each wine with a `scrape_status`: `success` (page reachable and at least the core identity fields — Nome, Vinícola — were parsed), `partial` (page reachable but the core identity fields are missing or several technical fields are blank), `failed` (HTTP error, timeout, or page unparseable) or `manual` (user entered everything without scraping).
- When `scrape_status` is `failed`, the UI shows a banner: "Não foi possível obter os dados do site. Preencha manualmente." with two buttons: "Tentar novamente" (retry same URL) and "Usar outra URL" (input alternative URL).
- When `scrape_status` is `partial`, the form pre-fills the fields that were captured and leaves the rest editable, with a softer banner explaining which fields could not be read.
- The user can always switch to "Inserir manualmente" mode and skip scraping entirely.
- Every field is independently editable after save, so the user can correct or complete data at any time without re-scraping.

### Feature 2: Cellar overview with search and filters (P0)

The home page of the app is the cellar overview — a scrollable list of wine cards optimized for phones.

- Each card shows: bottle image (thumbnail), name, winery, vintage, current stock count.
- Search box for free-text matching on name, winery, and region (substring/contains, case-insensitive).
- Filters: grape variety (multi-select), wine type (red, white, rosé, sparkling), stock availability (toggle: hide wines with stock = 0).
- Sorting: by purchase date (default, newest first) or by vintage.
- Tapping a card opens the wine detail page.

### Feature 3: Wine detail page (P0)

The full ficha of a single wine: large bottle image, all metadata, current stock with +/- buttons, and an "Edit" action for manual corrections.

- Stock controls: "+1" (added a new bottle) and "-1" (opened a bottle) buttons, with current count displayed prominently.
- "Re-scrape this wine" action that re-fetches the original URL (or accepts a new URL) and refreshes the metadata + image.
- "Edit" action that opens a form with all fields editable for manual correction (e.g., fixing a typo from a partial scrape).
- "Delete" action with confirmation — removes the wine and its image file.
- Display of the `scrape_status` as a visible badge (`Completo`, `Parcial`, `Falhou`, `Manual`) so the user understands the provenance of the data.

### Feature 4: Duplicate detection by URL (P0)

When the user submits a URL that matches a wine already in the cellar (after URL normalization — lowercase, no query strings, no trailing slash), the app intercepts the add flow and shows: "Esse vinho já está na sua adega (N garrafas). Adicionar +1?" with primary button "Adicionar +1 ao estoque" and secondary link "Ver ficha do vinho".

- The duplicate detection runs before any scraping HTTP call, so re-adding a known wine is instantaneous and avoids redundant network traffic.
- If the user confirms, the existing wine's stock is incremented by 1 and the user is taken to the wine detail page.

### Feature 5: Export cellar to JSON and CSV (P0)

A menu item "Exportar Adega" generates two downloadable files:

- **`adega.json`**: full dump of every wine record, including all fields, `scrape_status`, image relative path, original URL, purchase date, stock, and a top-level `schema_version` plus `exported_at` timestamp.
- **`adega.csv`**: tabular view of the main fields (nome, vinícola, safra, uvas, região, tipo, estoque, data_compra) — opens cleanly in Excel and Google Sheets.

Both exports are generated on demand and downloaded immediately. Images are referenced by relative path in the JSON; the user backs up the images directory separately (out of scope for the export flow — handled by rclone per AGENTS.md).

### Feature 6: Authentication (P0)

Login/password authentication backed by JWT. Single-user in the MVP — first run creates the user account via a CLI script or first-time signup flow.

- Sessions persist on the phone (no need to re-login on every visit).
- All non-public routes require authentication.

## User Experience

### Key persona and goals

The Personal Collector wants:
- Speed when adding a wine (a typical add via URL paste should take under 30 seconds end-to-end).
- Confidence that the data is captured even when the site fails (clear fallback flows).
- Quick lookup on the phone, ideally while standing in front of the cellar deciding what to open.
- Reassurance that the data is theirs (visible export feature).

### Primary user flows

**Flow 1 — Add a wine by URL (happy path)**
1. User taps "Adicionar Vinho" from the cellar overview.
2. User pastes the wine.com.br URL into the URL field.
3. User taps "Buscar dados do vinho" — a spinner appears.
4. App scrapes the page, downloads the image, returns a pre-filled form with `scrape_status: success`.
5. User reviews the fields (all editable), sets the initial stock count (default 1), confirms purchase date (default today), and taps "Salvar".
6. User lands on the wine detail page with all metadata visible.

**Flow 2 — Add a wine when scraping fails**
1. Steps 1-3 same as Flow 1.
2. App returns `scrape_status: failed`. The form shows a red banner explaining the failure with two buttons: "Tentar novamente" and "Usar outra URL".
3. User can:
   - Retry scraping (button 1), or
   - Provide an alternate URL (button 2), or
   - Switch to "Inserir manualmente" tab and fill the form by hand.
4. User saves the wine. The wine card shows a `Manual` badge.

**Flow 3 — Add a wine that already exists**
1. User pastes a URL into "Adicionar Vinho".
2. App normalizes the URL, finds a match, and intercepts before scraping.
3. Modal: "Esse vinho já está na sua adega (3 garrafas). Adicionar +1?" with primary "Adicionar +1 ao estoque" and secondary "Ver ficha do vinho".
4. User taps "Adicionar +1": stock becomes 4 and user lands on the wine detail page.

**Flow 4 — Decrement stock when opening a bottle**
1. From the cellar, user taps the wine they are about to open.
2. On the wine detail page, user taps "-1".
3. Stock decreases by 1; if it hits 0 the card shows a "consumido" indicator in the cellar overview but the wine record is never deleted automatically.

**Flow 5 — Export the cellar**
1. From the menu, user taps "Exportar Adega".
2. App generates `adega.json` and `adega.csv` and offers them for download.
3. User saves the files locally or to cloud storage.

### UI/UX considerations

- **Mobile-first**: all layouts start from a phone width (~375px) and expand for tablet/desktop. Buttons are thumb-friendly (min 44x44px). Wine bottle images use `object-contain` so tall bottles are not cropped.
- **Portuguese (pt-BR) everywhere**: labels, buttons, error messages, badges.
- **Color palette**: dark wine reds with cream/off-white backgrounds — sophisticated but simple.
- **Loading states**: every scraping action shows a visible spinner with a friendly label ("Buscando dados do vinho...").
- **Error visibility**: failed scrapes are highly visible (red banner, clear next steps); silent failures are not allowed.

### Onboarding and discoverability

- First-time login lands the user on an empty cellar with a single prominent button: "Adicionar seu primeiro vinho".
- The export feature is reachable from the main menu (hamburger or footer) with the label "Exportar Adega" — discoverable without being intrusive.

## High-Level Technical Constraints

- **Personal data only**: the app stores wine metadata for the single logged-in user. No analytics, no telemetry, no third-party trackers.
- **Local-first, cloud-ready**: the application must run end-to-end on the user's machine with a single Docker Compose stack; cloud migration must be possible by changing environment variables only.
- **Good citizenship toward wine.com.br**: scraping is on-demand only (user-triggered), uses a descriptive User-Agent identifying the app, respects timeouts (15s), and never bypasses TLS.
- **Image preservation**: the bottle image is downloaded and stored locally so the user has a copy even if the source URL is later removed.
- **Backup is the user's responsibility**: the app provides JSON/CSV export and stores images in a single directory; long-term backup happens via the user's own rclone configuration to Google Drive.

## Non-Goals (Out of Scope)

The following are explicitly excluded from V1 and from the foreseeable roadmap unless re-prioritized later:

- **Multi-user / household sharing** — single user only in MVP; multi-user is a future possibility but not committed.
- **Tasting notes and tasting history** — deferred to Phase 2.
- **Drinking window / "Para Beber" page** — deferred to Phase 3.
- **Wine recommendations or pairing suggestions** — out of scope; not what this app is for.
- **Social features (sharing, ratings, public profiles)** — out of scope; this is a private archive.
- **Marketplace / purchase integration** — out of scope; the user buys on wine.com.br directly.
- **Barcode/label scanning** — out of scope; URL paste is the primary capture mechanism since the user is buying online.
- **Scraping sources other than wine.com.br** — out of scope for V1; the product is explicitly targeted at this retailer.
- **Background/automated scraping jobs** — scraping is always user-triggered.
- **Price tracking or value estimation** — out of scope; the focus is metadata preservation, not market value.
- **Native mobile apps (iOS/Android)** — out of scope; the responsive web app is the only frontend.
- **Importing data from other apps or CSV files** — out of scope for V1; the export side is one-way.
- **Bulk-add or batch import** — out of scope for V1; each wine is added individually.

## Phased Rollout Plan

### MVP (Phase 1) — Archivist Foundation

**Scope:**
- Authentication (single user, JWT).
- Add wine via URL with on-demand scraping (success / partial / failed / manual paths).
- Wine detail page with full ficha, stock +/- controls, edit, re-scrape, delete.
- Cellar overview with search (free text), filters (grape, type, stock availability), and sorting (purchase date, vintage).
- Duplicate detection by URL with "+1 stock" prompt.
- Export to JSON and CSV.
- Mobile-first responsive UI in Portuguese.

**Success criteria to proceed to Phase 2:**
- User can archive 50+ wines from real wine.com.br URLs without losing any to scraping failures (always reachable via manual fallback).
- Scraping success rate ≥ 80% on the user's actual buying history (the remainder must be recoverable via the partial/manual paths).
- Average time-to-add for a wine via URL is under 30 seconds.
- User can produce a valid `adega.json` and `adega.csv` export at any time.

### Phase 2 — Tasting Notebook

**Scope:**
- `WineTasting` entity 1:N per wine.
- For each tasting: date, structured organoleptic notes (free-form fields for sight, smell, taste, finish — kept simple, not a rigid sommelier rubric), and a "memories" narrative field (occasion, who you drank with, how the bottle was).
- Tasting history view on each wine detail page (timeline).
- "Last tasted" indicator on the cellar overview card.
- Export format extended to include tastings (the JSON `schema_version` bumps to 2).

**Success criteria to proceed to Phase 3:**
- User logs at least 10 tastings within the first month of Phase 2 release.
- Tasting form is usable one-thumbed on a phone (validated by real use, not just unit tests).

### Phase 3 — Drinking Window

**Scope:**
- Dedicated "Para Beber" page listing wines that are currently in their drinking window.
- Heuristic combining `vintage` + `aging potential` text (parsed best-effort) to classify wines as "Beber agora", "No auge", or "Pode esperar".
- Visual badge on the wine detail page and on cellar cards.
- Basic stats: total wines, total bottles, distribution by type/region/vintage.

**Long-term success criteria:**
- User checks the "Para Beber" page before deciding what to open in at least 50% of opening events (self-reported / behavioral signal).
- No wines are forgotten past their peak window (qualitative validation).

## Success Metrics

### Engagement
- **Wines archived per month**: target ≥ 5 (covers a typical Clube Wine subscription cadence).
- **Time to first wine after install**: < 5 minutes.
- **Time-to-add per wine** (URL paste to saved): < 30 seconds for `success` path; < 90 seconds for `failed` path.

### Quality
- **Scraping success rate** on real wine.com.br URLs: ≥ 80% in `success`, ≥ 95% in `success` + `partial` combined.
- **Zero data-loss events**: every wine the user attempts to add ends up in the cellar (via manual fallback if needed).
- **Mobile usability**: every primary action (add, search, +/- stock, export) is reachable in 1-2 taps on a phone.

### Reliability
- **Export integrity**: the JSON export round-trips without loss when re-loaded into a clean instance (validated in Phase 2 when import is built).
- **Image preservation**: 100% of wines with `scrape_status: success` have a locally stored image.

## Risks and Mitigations

### Adoption risks

- **Risk**: scraping is fragile by nature — wine.com.br can change layouts and break parsers.
  - **Mitigation**: manual fallback is a first-class flow, not an afterthought. The user is never blocked from archiving a wine. Parser is built defensively (every field optional, soft failures only).
- **Risk**: user finds the URL paste flow tedious and stops using the app.
  - **Mitigation**: phone clipboard + share-from-browser flow is natural — paste is one tap. If friction proves real in usage, a Phase 2 enhancement could explore browser-extension-driven add (out of scope for V1).

### Competitive risks

- **Risk**: Vivino or CellarTracker add a Brazilian wine.com.br integration and replicate the wedge.
  - **Mitigation**: the local-first / self-owned-data angle is a structural differentiator they cannot match without changing their business model. WineCollector's value proposition holds even if competitors add features.
- **Risk**: wine.com.br itself launches an official cellar feature.
  - **Mitigation**: same as above — the trust angle is "your data lives with you, not with them", which an in-retailer feature cannot offer.

### Timeline and resource constraints

- **Risk**: single developer, personal project — risk of scope creep delaying the MVP.
  - **Mitigation**: ADR-001 commits to "Archivist Primeiro" deliberately to keep the MVP enxuto. Phase 2 (tasting) is held back precisely so that Phase 1 ships.
- **Risk**: the user's own buying cadence outpaces the app — wines accumulate uncatalogued.
  - **Mitigation**: the MVP is small enough to ship quickly. The export feature ensures that even half-cataloged data has value.

### Dependency risks

- **Risk**: wine.com.br adds anti-scraping measures (rate limiting, JS rendering required, CAPTCHA).
  - **Mitigation**: scraping is low-volume (single user, on-demand) and uses a clear User-Agent — unlikely to be aggressive enough to attract countermeasures. If they do, the manual fallback covers the case at the cost of more user effort.
- **Risk**: subscription clubs (WineBox) deliver wines without a direct product URL on wine.com.br.
  - **Mitigation**: manual entry is always available; the wine is archived even when the URL path doesn't exist.

## Architecture Decision Records

- [ADR-001: Faseamento "Arquivista Primeiro"](adrs/adr-001.md) — Adoptamos a abordagem em três fases (cadastro + scraping no MVP, degustação na F2, drinking window na F3) para validar primeiro o pilar central de preservação.
- [ADR-002: Deduplicação por URL com Incremento Automático de Estoque](adrs/adr-002.md) — Cada vinho é único pela URL canônica; cadastros repetidos incrementam estoque sem criar duplicatas.
- [ADR-003: Exportação JSON/CSV Manual no MVP](adrs/adr-003.md) — A exportação in-app entra no MVP para honrar a tese de "você é dono dos seus dados", complementando o backup via rclone.

## Open Questions

- **URL normalization rules**: exact list of transformations to apply before duplicate detection (lowercase, strip query, strip trailing slash, possibly strip tracking parameters). To be finalized during TechSpec.
- **Default values**: should `tipo` (red/white/rosé/sparkling) be inferred from the scraped data, derived from a curated mapping, or always asked manually? Decision deferred to TechSpec / first scraping experiments.
- **Image format normalization**: do we always convert to WebP (per AGENTS.md rules), or store the source format if it is already JPEG/PNG? Affects scraper implementation; to be confirmed in TechSpec.
- **CSV column localization**: keep headers in Portuguese ("nome,vinícola,safra,...") or use neutral English keys? Portuguese is the current default per the user-facing language choice; revisit if a future use case (e.g., third-party tooling) needs English.
- **First-user creation flow**: CLI script (`poetry run create-user`) vs. first-time signup screen in the UI. To be decided in TechSpec.
- **Failure-rate observability**: should `scrape_status` distribution be exposed in a simple admin/stats screen so the user can see how the parser is performing, or remain invisible? Likely a small Phase 2/3 add.
