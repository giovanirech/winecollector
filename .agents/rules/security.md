<!-- Scope: **/*.py — secrets management, auth, scraping safety, image sanitization -->

# Security Best Practices

## Secrets & Configuration
- All secrets (DB URL, secret key, etc.) are loaded via `pydantic-settings` from `.env`
- Never hardcode credentials, tokens, or keys anywhere in source code
- `.env` is in `.gitignore`; `.env.example` is always kept up to date with all required keys

```python
# ✅ Good — pydantic-settings
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str          # Used by fastapi-users for JWT signing
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

settings = Settings()

# ❌ Never do this
SECRET_KEY = "my-secret-key-hardcoded"
DATABASE_URL = "postgresql+asyncpg://postgres:1234@localhost/adega"
```

## Authentication (fastapi-users)
- Use **fastapi-users** with `BearerTransport` + `JWTStrategy`
- The `secret_key` for JWT must be a long random string (≥ 32 chars); generate with `openssl rand -hex 32`
- Set reasonable token expiry (`access_token_expire_minutes = 60`)
- Protect all non-public routes with `current_active_user` dependency

```python
# ✅ Good — protecting a route
from adega.auth import current_active_user
from adega.models.user import User

@router.post("/wines")
async def add_wine(
    payload: WineCreate,
    db: SessionDep,
    user: User = Depends(current_active_user),
) -> WineResponse:
    ...
```

## Database
- Always use SQLAlchemy ORM or parameterized queries — never string-format SQL
- Database credentials are only in `.env`, never in `alembic.ini` directly (use env var interpolation)

```python
# ✅ Good — ORM query
result = await db.execute(select(Wine).where(Wine.id == wine_id))

# ❌ SQL injection risk
await db.execute(f"SELECT * FROM wines WHERE id = {wine_id}")
```

## Web Scraping (wine.com.br)
- Set a `timeout` on all httpx requests (default: 15 seconds)
- Set a descriptive `User-Agent` header to be a good citizen
- Never disable SSL verification (`verify=False` is forbidden)
- Catch `httpx.HTTPStatusError` and `httpx.RequestError` explicitly; set `scrape_status = "failed"` and log the error

```python
# ✅ Good
HEADERS = {"User-Agent": "Adega/1.0 (personal wine cellar manager)"}

async def scrape_wine(url: str) -> WineScrapedData:
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.exception("HTTP error scraping %s: %s", url, exc)
        return WineScrapedData(scrape_status="failed")
    except httpx.RequestError as exc:
        logger.exception("Connection error scraping %s: %s", url, exc)
        return WineScrapedData(scrape_status="failed")
```

## Image Storage
- Sanitize filenames before saving to disk — never use filenames from external sources directly
- Store images only under `./data/images/`; validate the path stays within that directory
- Use a UUID or the wine's DB id as the filename to avoid conflicts and path traversal

```python
# ✅ Good
import uuid
from pathlib import Path

IMAGES_DIR = Path("data/images")

def save_image(image_bytes: bytes, extension: str = "webp") -> str:
    filename = f"{uuid.uuid4()}.{extension}"
    filepath = IMAGES_DIR / filename
    filepath.write_bytes(image_bytes)
    return str(filepath)
```

## Logging
- Never log passwords, tokens, or personally identifiable information
- Use structured logging in production (JSON format)
- Log scraping failures with the URL and status code for debuggability
