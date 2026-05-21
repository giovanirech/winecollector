<!-- Scope: **/scraper*.py — httpx + BeautifulSoup, wine.com.br, WineScrapedData schema -->

# Scraper — wine.com.br

## Core Rules
- Scraping is **on-demand only** — triggered by the user when adding a wine or manually refreshing it
- Always return a `WineScrapedData` object, even on failure — never raise uncaught exceptions to the router
- Set `scrape_status` to `"success"`, `"failed"`, or `"partial"` (some fields scraped, others missing)
- Log every failure with the URL, HTTP status, and exception message

## httpx Setup
```python
import httpx

SCRAPER_HEADERS = {
    "User-Agent": "Adega/1.0 (personal wine cellar manager; github.com/youruser/adega)",
    "Accept-Language": "pt-BR,pt;q=0.9",
}
SCRAPER_TIMEOUT = 15.0  # seconds

async def fetch_page(url: str) -> str | None:
    """Fetch raw HTML from a URL. Returns None on any error."""
    try:
        async with httpx.AsyncClient(
            timeout=SCRAPER_TIMEOUT,
            headers=SCRAPER_HEADERS,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as exc:
        logger.warning("HTTP %s for URL %s", exc.response.status_code, url)
        return None
    except httpx.RequestError as exc:
        logger.warning("Request error for URL %s: %s", url, exc)
        return None
```

## BeautifulSoup Parsing
- Always use `"html.parser"` (stdlib, no extra deps) unless lxml is justified
- Wrap every `.find()` / `.find_all()` access in a helper that returns `None` gracefully — don't assume the element exists
- If a field is missing, set it to `None` and flag `scrape_status = "partial"`

```python
from bs4 import BeautifulSoup

def parse_wine_page(html: str) -> WineScrapedData:
    soup = BeautifulSoup(html, "html.parser")

    return WineScrapedData(
        name=_safe_text(soup, "h1.product-name"),
        winery=_safe_text(soup, "[data-testid='winery']"),
        vintage=_safe_int(soup, "[data-testid='vintage']"),
        region=_safe_text(soup, "[data-testid='region']"),
        # ... other fields
        scrape_status="success",
    )

def _safe_text(soup: BeautifulSoup, selector: str) -> str | None:
    el = soup.select_one(selector)
    return el.get_text(strip=True) if el else None

def _safe_int(soup: BeautifulSoup, selector: str) -> int | None:
    text = _safe_text(soup, selector)
    try:
        return int(text) if text else None
    except ValueError:
        return None
```

## Image Scraping
- Download the product image URL found in the page
- Save to `data/images/<uuid>.webp` (or original extension if not webp)
- Store the local path in `Wine.image_path` and the original URL in `Wine.image_url`
- If image download fails, log a warning but don't fail the whole scrape

```python
async def download_image(image_url: str, dest_dir: Path) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(image_url)
            response.raise_for_status()
        filename = f"{uuid.uuid4()}.webp"
        filepath = dest_dir / filename
        filepath.write_bytes(response.content)
        return str(filepath)
    except Exception as exc:
        logger.warning("Could not download image %s: %s", image_url, exc)
        return None
```

## WineScrapedData Schema
```python
from pydantic import BaseModel

class WineScrapedData(BaseModel):
    name: str | None = None
    winery: str | None = None
    vintage: int | None = None
    region: str | None = None
    country: str | None = None
    grape_varieties: list[str] = []
    aging: str | None = None
    aging_potential: str | None = None
    tasting_notes: str | None = None
    image_url: str | None = None
    image_path: str | None = None          # local path after download
    scrape_status: str = "failed"          # "success" | "partial" | "failed"
```

## What to Expose in the UI
When `scrape_status == "failed"`:
- Show a visible warning banner: "Não foi possível obter os dados do site. Preencha manualmente."
- Pre-fill whatever fields were scraped (`"partial"`)
- Offer a "Tentar novamente" button that re-triggers scraping with the same URL
- Offer a "Usar outra URL" field
