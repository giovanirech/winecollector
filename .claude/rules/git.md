<!-- Scope: manual reference — Conventional Commits, branch naming, .gitignore -->

# Git Conventions

## Commit Messages — Conventional Commits
```
<type>(<scope>): <short description>

[optional body]
```

### Types & Scopes for this project
| Type | When to use |
|---|---|
| `feat` | New feature (new field, new page, new route) |
| `fix` | Bug fix |
| `scraper` | Changes to wine.com.br scraping logic |
| `ui` | Frontend template or style changes |
| `db` | New Alembic migration or model change |
| `auth` | Authentication-related changes |
| `docs` | Documentation only |
| `chore` | Dependencies, tooling, Docker config |
| `test` | Adding or fixing tests |

### Examples
```
feat(wines): add stock quantity field to wine model

fix(scraper): handle missing vintage on wine.com.br pages

db: add wine_tastings table migration

ui: add responsive wine detail card with Tailwind

chore(docker): add postgres healthcheck to compose
```

## Branch Naming
```
feature/<short-description>
fix/<short-description>
db/<migration-description>
scraper/<what-changed>
ui/<component-or-page>

# Examples:
feature/tasting-notes
fix/scraper-image-404
db/add-memories-field
ui/wine-detail-page
```

## Workflow
1. Branch off `main`
2. Keep branches short-lived
3. Squash commits before merging to keep `main` history clean
4. Run `pytest` and `ruff check .` before opening a PR

## .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual environments
.venv/
venv/

# Environment
.env
.env.*
!.env.example

# Data (never commit local DB data or images)
data/postgres/
data/images/

# Testing & coverage
.pytest_cache/
.coverage
htmlcov/

# Type checking / linting cache
.mypy_cache/
.ruff_cache/

# IDEs
.vscode/
.idea/
```

## Alembic Migration Commits
Every Alembic migration gets its own commit:
```
db: add scrape_status column to wines table

Generated via: alembic revision --autogenerate -m "add scrape_status"
```
