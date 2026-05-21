<!-- Scope: docker-compose*.yml, Dockerfile — Docker Compose setup and commands -->

# Docker & Infrastructure Conventions

## docker-compose.yml Structure
```yaml
# docker-compose.yml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-adega}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-adega}
      POSTGRES_DB: ${POSTGRES_DB:-adega}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U adega"]
      interval: 5s
      timeout: 5s
      retries: 5

  app:
    build: .
    restart: unless-stopped
    command: uvicorn adega.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
      - ./data/images:/app/data/images
    ports:
      - "8000:8000"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy
```

## Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry --no-cache-dir
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root --no-interaction

COPY . .
RUN poetry install --no-interaction

CMD ["uvicorn", "adega.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Common Commands
```bash
# Start the full stack (DB + app)
docker compose up

# Start only the database (run app locally with uvicorn)
docker compose up db

# Apply Alembic migrations inside the container
docker compose exec app alembic upgrade head

# Open a psql shell
docker compose exec db psql -U adega

# Rebuild after dependency changes
docker compose build app
```

## .env.example (keep this updated)
```env
# Database
POSTGRES_USER=adega
POSTGRES_PASSWORD=changeme
POSTGRES_DB=adega
DATABASE_URL=postgresql+asyncpg://adega:changeme@localhost:5432/adega

# Auth (generate with: openssl rand -hex 32)
SECRET_KEY=changeme-use-openssl-rand-hex-32

# App
IMAGES_DIR=data/images
```

## Volumes
- `./data/postgres` — Postgres data; **never commit this directory**
- `./data/images` — Wine bottle images; back up with rclone to Google Drive

## Local vs Cloud
- Local: `docker compose up` with Postgres on `localhost:5432`
- Cloud migration path: change `DATABASE_URL` to point to managed Postgres (Supabase, Railway, Render); image storage moves to S3/R2
- No app code changes needed — only env vars change
