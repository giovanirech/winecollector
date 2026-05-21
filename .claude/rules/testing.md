<!-- Scope: tests/**/*.py — pytest-asyncio, fixtures, httpx test client, mock patterns -->

# Testing Standards

## Framework & Tools
- **pytest** as the test runner
- **pytest-asyncio** for async tests (mode: `asyncio_mode = "auto"` in `pyproject.toml`)
- **httpx.AsyncClient** (via `ASGITransport`) for testing FastAPI endpoints — never `TestClient` in async tests
- **pytest-cov** for coverage (target: ≥ 80%)
- **factory_boy** for generating test model instances

## File Structure
Mirror `src/adega/` under `tests/`:
```
tests/
├── conftest.py              # DB session, app client, shared fixtures
├── unit/
│   ├── services/
│   │   ├── test_wine_service.py
│   │   └── test_scraper.py
│   └── models/
│       └── test_wine.py
└── integration/
    ├── test_wines_router.py
    └── test_tastings_router.py
```

## Async Test Setup
```python
# conftest.py
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from adega.main import app
from adega.database import get_session
from adega.models import Base

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/adega_test"

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture()
async def db_session(engine):
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture()
async def client(db_session):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

## Writing Tests
- Follow **Arrange / Act / Assert** with blank lines between sections
- One logical assertion per test
- Use descriptive names: `test_<behaviour>_<condition>_<expected_result>`
- Tests must be **independent** — no shared mutable state

```python
# ✅ Good
@pytest.mark.asyncio
async def test_get_wine_with_valid_id_returns_wine(client: AsyncClient, db_session: AsyncSession) -> None:
    # Arrange
    wine = await WineFactory.create(db_session, name="Château Margaux")

    # Act
    response = await client.get(f"/wines/{wine.id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["name"] == "Château Margaux"


async def test_get_wine_with_invalid_id_returns_404(client: AsyncClient) -> None:
    response = await client.get("/wines/99999")
    assert response.status_code == 404
```

## Testing the Scraper
- Mock `httpx.AsyncClient.get` to avoid real HTTP calls in tests
- Keep fixture HTML files under `tests/fixtures/html/wine_page.html` for realistic parsing tests

```python
async def test_scraper_extracts_wine_name(mocker: MockerFixture) -> None:
    # Arrange
    html = Path("tests/fixtures/html/wine_page.html").read_text()
    mocker.patch("httpx.AsyncClient.get", return_value=MockResponse(200, html))

    # Act
    result = await scrape_wine("https://wine.com.br/produto/fake")

    # Assert
    assert result.name == "Expected Wine Name"
    assert result.scrape_status == "success"
```

## Scraper Failure Tests
Always test the failure path — it's a core feature of this project:
```python
async def test_scraper_sets_failed_status_on_http_error(mocker: MockerFixture) -> None:
    mocker.patch("httpx.AsyncClient.get", side_effect=httpx.HTTPStatusError(...))

    result = await scrape_wine("https://wine.com.br/produto/gone")

    assert result.scrape_status == "failed"
```

## Running Tests
```bash
# All tests
pytest

# With coverage report
pytest --cov=src/adega --cov-report=term-missing

# Unit tests only (fast, no DB)
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

## pyproject.toml config
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.coverage.run]
source = ["src/adega"]
omit = ["*/migrations/*"]
```
