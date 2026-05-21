# AGENTS.md — Adega Pessoal

> Arquivo de contexto principal para qualquer agente de IA (Claude Code, Cursor, Copilot)
> que trabalhar neste repositório. **Leia este arquivo antes de qualquer alteração.**

---

## 1. Project Overview

**Adega Pessoal** é uma aplicação web pessoal para catalogar vinhos comprados na loja
[wine.com.br](https://wine.com.br). O catálogo público da loja remove informações dos
vinhos quando saem de linha — o objetivo do projeto é **preservar localmente** os dados
de cada garrafa adquirida (vinícola, safra, uvas, região, amadurecimento, potencial de
guarda, características organolépticas e imagem) antes que isso aconteça.

Além de catalogar, a aplicação serve como caderno de degustação: para cada vinho é
possível registrar a **quantidade em estoque**, **notas sensoriais** e **memórias** —
um campo narrativo com a ocasião em que a garrafa foi aberta. A coleta de dados é
automática via scraping da página do vinho no wine.com.br; quando o scraping falha
(página removida, layout alterado), a UI permite preenchimento manual e oferece
re-disparo do scraping com a URL original ou uma nova.

O usuário-alvo é o próprio dono da adega. A autenticação é single-user no MVP, mas a
arquitetura (fastapi-users + JWT) já está preparada para multi-user. O front-end é
mobile-first — o uso típico é consultar a adega pelo celular antes de abrir uma
garrafa ou registrar uma degustação logo depois.

---

## 2. Tech Stack

| Camada                    | Tecnologia                              | Observação                                                |
|---------------------------|-----------------------------------------|-----------------------------------------------------------|
| Linguagem                 | Python 3.12+                            | Async-first em toda a stack                               |
| Gerenciador de versão     | pyenv                                   | `.python-version` fixa a versão exata                     |
| Gerenciador de pacotes    | Poetry                                  | `pyproject.toml` como fonte de verdade                    |
| Web framework             | FastAPI (async)                         | Roteamento, validação, OpenAPI                            |
| ORM                       | SQLAlchemy 2.0 (declarativo, async)     | Estilo `Mapped[T]` + `mapped_column()`                    |
| Migrations                | Alembic                                 | Autogenerate a partir dos models                          |
| Autenticação              | fastapi-users                           | Login/senha + JWT (BearerTransport)                       |
| Validação                 | Pydantic v2                             | Schemas separados em `schemas/`                           |
| Templates                 | Jinja2                                  | Server-side rendering                                     |
| CSS                       | Tailwind CSS                            | Mobile-first; CDN Play no MVP                             |
| Interatividade frontend   | HTMX                                    | Sem JS manual; Alpine.js só se necessário                 |
| Scraping HTTP             | httpx (async)                           | `timeout=15s`, User-Agent descritivo                      |
| Scraping HTML             | BeautifulSoup4                          | Parser `html.parser` (stdlib)                             |
| Banco de dados            | PostgreSQL 16                           | Local via Docker Compose                                  |
| Driver async              | asyncpg                                 | `postgresql+asyncpg://...`                                |
| Storage de imagens        | Filesystem em `./data/images/`          | Caminho UUID salvo no banco                               |
| Containerização           | Docker Compose                          | Postgres isolado; app opcional via compose                |
| Backup                    | rclone                                  | Sync com Google Drive                                     |
| Linting / formatação      | ruff                                    | `ruff check . --fix && ruff format .`                     |
| Testes                    | pytest + pytest-asyncio + pytest-cov    | `asyncio_mode = "auto"`; cobertura ≥ 80%                  |

---

## 3. Architecture Decisions

### Por que FastAPI + HTMX (e não Reflex/Streamlit/Django)
- **FastAPI** é a escolha padrão para Python async moderno: type hints como contrato,
  validação via Pydantic, OpenAPI grátis, e um modelo de routers/services que separa
  cleanly HTTP de lógica de negócio.
- **HTMX** elimina a necessidade de uma SPA: o servidor devolve fragmentos HTML
  (`partials/`) e o DOM é atualizado por atributos `hx-*`. Resultado: zero build step,
  nada de bundler, e o stack Python permanece coeso. Reflex/Streamlit foram descartados
  por acoplarem demais UI e lógica e por dificultarem o controle fino do scraping
  assíncrono. Django seria síncrono por padrão e exigiria mais cerimônia para o que é
  uma aplicação pequena.

### Por que PostgreSQL local via Docker (e não SQLite)
- O caminho de migração para nuvem (Supabase, Railway, Render) precisa ser uma troca
  de `DATABASE_URL` — nada mais. SQLite tornaria essa transição uma reescrita.
- Postgres em Docker isola completamente o banco da máquina do desenvolvedor; o volume
  fica em `./data/postgres/` (gitignored) e pode ser destruído sem cerimônia.
- Recursos como tipos JSONB, full-text search e índices parciais ficam disponíveis
  desde o dia um — útil caso o catálogo cresça.

### Por que imagens em disco (e não no banco / S3)
- Imagens de vinho são **recuperáveis**: se o arquivo local for perdido, basta
  re-disparar o scraping. Não há valor em pagar o custo de bytea no Postgres.
- O backup via rclone trata `./data/images/` como um diretório qualquer — sincronia
  com Google Drive sem nenhuma camada extra.
- Migração futura para S3/R2 é trivial: trocar o `image_path` por uma URL pública.

### Separação routers / services
- **Routers** (`src/adega/routers/`) tratam **apenas HTTP**: parsing de input, chamada
  ao service, conversão do retorno para `Response`/`HTMLResponse`. Nenhuma query
  SQL deve aparecer em um router.
- **Services** (`src/adega/services/`) contêm a lógica de negócio. Recebem um
  `AsyncSession` por parâmetro e levantam exceções de domínio. Quem traduz exceção
  para HTTP é o router.
- Essa separação mantém a lógica testável sem subir o app inteiro — `tests/unit/`
  testa services em isolamento, `tests/integration/` exercita o stack via
  `httpx.AsyncClient + ASGITransport`.

### Local-first, cloud-ready
- A única variável que muda entre local e cloud é `DATABASE_URL` (e eventualmente
  o storage de imagens). Nenhum acoplamento a SDKs proprietários no MVP.

---

## 4. Development Setup

```bash
# 1. Pré-requisitos — instalar a versão correta do Python
pyenv install 3.12.7
pyenv local 3.12.7

# 2. Instalar dependências do projeto
poetry install

# 3. Variáveis de ambiente
cp .env.example .env
# Edite .env com os valores corretos. Gere a SECRET_KEY com:
#   openssl rand -hex 32

# 4. Subir o banco de dados (apenas o Postgres)
docker compose up db -d

# 5. Rodar as migrations
poetry run alembic upgrade head

# 6. Iniciar a aplicação em modo desenvolvimento
poetry run uvicorn adega.main:app --reload --host 0.0.0.0 --port 8000

# --- ALTERNATIVA: subir tudo via Docker Compose ---
docker compose up
```

A primeira execução cria automaticamente os diretórios `data/images/` e
`data/postgres/` (ambos ignorados pelo Git). Após o `alembic upgrade head`,
acesse http://localhost:8000 para a UI e http://localhost:8000/docs para o Swagger.

---

## 5. Services & Ports

| Serviço                 | Porta | URL                              |
|-------------------------|-------|----------------------------------|
| Aplicação web (FastAPI) | 8000  | http://localhost:8000            |
| PostgreSQL              | 5432  | localhost:5432                   |
| Docs API (Swagger)      | 8000  | http://localhost:8000/docs       |
| Docs API (Redoc)        | 8000  | http://localhost:8000/redoc      |

---

## 6. Common Commands

```bash
# === Testes ===
poetry run pytest                                          # todos os testes
poetry run pytest --cov=src/adega --cov-report=term-missing  # com cobertura
poetry run pytest tests/unit/                              # apenas unit (rápido)
poetry run pytest tests/integration/                       # apenas integration
poetry run pytest -k "scraper"                             # filtra por nome

# === Linting e formatação ===
poetry run ruff check . --fix                              # corrige issues automáticos
poetry run ruff format .                                   # formata o código

# === Migrations (Alembic) ===
poetry run alembic revision --autogenerate -m "descrição"  # gera nova migration
poetry run alembic upgrade head                            # aplica todas
poetry run alembic downgrade -1                            # desfaz a última
poetry run alembic history                                 # histórico

# === Docker ===
docker compose up                                          # tudo (db + app)
docker compose up db -d                                    # só o banco
docker compose exec db psql -U adega                       # shell psql
docker compose exec app alembic upgrade head               # migrations dentro do container
docker compose logs -f app                                 # follow logs
docker compose down                                        # para tudo (mantém volumes)

# === Backup com rclone (configure remote 'gdrive' antes) ===
rclone sync ./data/postgres gdrive:adega-backup/postgres
rclone sync ./data/images   gdrive:adega-backup/images

# === Geração de chave para JWT ===
openssl rand -hex 32
```

---

## 7. Project Structure

```
adega/
├── src/
│   └── adega/                    # Pacote principal (src-layout)
│       ├── main.py               # FastAPI app factory + montagem de routers
│       ├── config.py             # Settings via pydantic-settings (lê .env)
│       ├── database.py           # Async engine + session + get_session()
│       ├── models/               # SQLAlchemy declarativo (Mapped[T])
│       │   ├── wine.py           #   Wine — entidade central da adega
│       │   └── tasting.py        #   WineTasting — degustações + memórias
│       ├── schemas/              # Pydantic v2 — request/response separados dos models
│       │   ├── wine.py
│       │   └── tasting.py
│       ├── routers/              # FastAPI routers (HTTP only — sem SQL)
│       │   ├── wines.py
│       │   ├── tastings.py
│       │   └── auth.py
│       ├── services/             # Lógica de negócio (recebe AsyncSession)
│       │   ├── wine_service.py
│       │   └── scraper.py        #   Scraping do wine.com.br
│       ├── templates/            # Jinja2 — server-side rendering
│       │   ├── base.html
│       │   ├── partials/         #   Fragmentos HTML para respostas HTMX
│       │   ├── wines/
│       │   └── tastings/
│       └── static/               # CSS, JS, ícones servidos pelo FastAPI
│           ├── css/
│           └── js/
├── data/                         # Dados locais — gitignored, mas existem na árvore
│   ├── images/                   #   Imagens dos vinhos (UUID.webp)
│   └── postgres/                 #   Volume do container Postgres
├── migrations/                   # Alembic
│   └── versions/                 #   Arquivos de migration (autogenerate)
├── tests/
│   ├── conftest.py               # Fixtures: engine, db_session, client async
│   ├── unit/                     # Testa services e parsers (sem DB / sem HTTP real)
│   └── integration/              # httpx.AsyncClient + ASGITransport contra o app
├── scripts/                      # Utilitários: seed, backup manual, etc.
├── .agents/
│   ├── rules/                    # Convenções por escopo (Python, scraper, frontend…)
│   └── skills/                   # Skills referenciadas pelos agentes (Compozy etc.)
├── docker-compose.yml            # db + app
├── Dockerfile                    # Python 3.12-slim + Poetry
├── pyproject.toml                # Deps + ruff + pytest + coverage
├── alembic.ini                   # DB URL via env var
├── .env.example                  # Template; .env real fica fora do Git
├── AGENTS.md                     # Este arquivo
└── README.md
```

---

## 8. Rules & Skills Index

### Rules

Arquivos em `.agents/rules/` — consultados automaticamente pelo editor de IA conforme
o contexto do arquivo aberto. **Sempre leia a rule aplicável antes de editar.**

| Arquivo                                                    | Escopo                  | Descrição                                                                                          |
|------------------------------------------------------------|-------------------------|----------------------------------------------------------------------------------------------------|
| [project.md](.agents/rules/project.md)                     | sempre ativo            | Visão geral, stack, estrutura de pastas, modelo de domínio e convenções gerais do projeto          |
| [python-style.md](.agents/rules/python-style.md)           | `**/*.py`               | PEP 8, type hints, padrões async, FastAPI (routers/services), SQLAlchemy 2.0 (`Mapped[T]`), Pydantic v2 |
| [testing.md](.agents/rules/testing.md)                     | `tests/**/*.py`         | pytest-asyncio, fixtures (engine/session/client), `httpx.AsyncClient` + `ASGITransport`, mocks do scraper |
| [security.md](.agents/rules/security.md)                   | `**/*.py`               | Secrets via pydantic-settings, fastapi-users + JWT, scraping seguro (timeouts, UA), sanitização de imagens |
| [scraper.md](.agents/rules/scraper.md)                     | `**/scraper*.py`        | httpx async + BeautifulSoup, parsing tolerante a falha, schema `WineScrapedData`, valores de `scrape_status` |
| [frontend.md](.agents/rules/frontend.md)                   | `templates/**`          | Jinja2 + Tailwind mobile-first, padrões HTMX (`hx-get`/`hx-post`/`hx-target`), Alpine.js apenas em último caso |
| [docker.md](.agents/rules/docker.md)                       | `docker-compose*.yml`   | Estrutura do `docker-compose.yml`, Dockerfile, healthchecks, volumes, comandos úteis               |
| [git.md](.agents/rules/git.md)                             | manual (`@git`)         | Conventional Commits (`feat`, `fix`, `scraper`, `db`, `ui`, `auth`, `chore`), naming de branches, `.gitignore` |

### Skills

Arquivos em `.agents/skills/` — instruções operacionais que o agente deve consultar
**antes de executar** a tarefa correspondente. Cada skill vive em sua própria pasta
com um `SKILL.md` (e opcional `references/`).

| Skill                                                                          | Quando usar                                                                                                |
|--------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------|
| [compozy](.agents/skills/compozy/SKILL.md)                                     | Referência do Compozy CLI — capacidades, pipeline de workflow, configuração e como os skills `cy-*` se encaixam. Consultar quando o usuário perguntar "como funciona o Compozy" ou "quais comandos existem". |
| [cy-create-prd](.agents/skills/cy-create-prd/SKILL.md)                         | Criar um **Product Requirements Document** via brainstorming interativo com pesquisa em paralelo de codebase e web. Usar ao iniciar uma nova feature ou produto.           |
| [cy-create-techspec](.agents/skills/cy-create-techspec/SKILL.md)               | Traduzir um PRD existente em uma **Technical Specification** com decisões arquiteturais documentadas (ADRs). |
| [cy-create-tasks](.agents/skills/cy-create-tasks/SKILL.md)                     | Decompor PRD + TechSpec em **arquivos de task** independentes e executáveis (`task_01.md`, `task_02.md`, …) com enriquecimento por exploração do codebase. |
| [cy-execute-task](.agents/skills/cy-execute-task/SKILL.md)                     | Executar **uma task de PRD** de ponta a ponta: exploração, implementação, validação e atualização do tracking. |
| [cy-review-round](.agents/skills/cy-review-round/SKILL.md)                     | Realizar uma **rodada de code review** estruturada sobre uma implementação de PRD e gerar arquivos de issue compatíveis com `cy-fix-reviews`. |
| [cy-fix-reviews](.agents/skills/cy-fix-reviews/SKILL.md)                       | **Remediar PR reviews** em lote a partir dos arquivos de issue gerados por `cy-review-round` (ou exports de providers externos). |
| [cy-final-verify](.agents/skills/cy-final-verify/SKILL.md)                     | **Gate de verificação obrigatório** antes de qualquer alegação de conclusão, commit ou abertura de PR — exige evidência fresca de teste executado. |
| [cy-workflow-memory](.agents/skills/cy-workflow-memory/SKILL.md)               | Manter a **memória do workflow** (`shared.md` + `current_task.md`) entre execuções de tasks dentro de um mesmo PRD. |

> **Observação:** as skills `cy-*` fazem parte do pipeline Compozy
> (PRD → TechSpec → Tasks → Execute → Review → Fix Reviews → Final Verify).
> Para fluxos pontuais — bug fix isolado, refactor curto — o pipeline completo é
> opcional; basta seguir as rules em `.agents/rules/`.

---

## 9. Scraping Notes

### Alvo
- Site: **wine.com.br**
- Páginas de produto, ex.: `https://www.wine.com.br/vinhos/casillero-del-diablo-reserva-cabernet-sauvignon/prod16104.html`

### URL de exemplo para testes
Mantenha um HTML real congelado em `tests/fixtures/html/wine_page.html` para os
testes unitários do parser — assim a suite não depende de conexão e não polui
o servidor da loja.

### Campo `scrape_status` — valores possíveis

| Valor       | Significado                                                                 |
|-------------|-----------------------------------------------------------------------------|
| `success`   | Todos os campos esperados foram extraídos com sucesso                       |
| `partial`   | A requisição HTTP funcionou, mas algum campo essencial está ausente (None)  |
| `failed`    | Erro de HTTP (4xx/5xx), timeout, conexão recusada, ou parsing inviável      |
| `manual`    | O vinho foi cadastrado **sem scraping** — usuário preencheu tudo à mão      |

### Comportamento esperado quando o scraping falha
1. `scrape_status` é gravado como `"failed"` no `Wine` (jamais lança exceção
   ao router — sempre retorna um `WineScrapedData`).
2. A UI exibe um banner: **"Não foi possível obter os dados do site. Preencha
   manualmente."**
3. Quaisquer campos que **tenham sido** extraídos são pré-preenchidos no formulário
   (caso de `partial`).
4. Dois botões aparecem:
   - **"Tentar novamente"** — re-dispara o scraping com a mesma URL.
   - **"Usar outra URL"** — campo de input para uma URL alternativa do mesmo vinho.
5. Toda falha é logada via `logger.exception()` com a URL e o status HTTP — sem
   logar headers ou cookies.

### Boa cidadania
- `User-Agent`: `"Adega/1.0 (personal wine cellar manager; github.com/<user>/adega)"`
- `timeout`: 15 segundos
- `follow_redirects`: `True`
- **Nunca** `verify=False`
- Scraping é **on-demand apenas** — disparado pelo usuário; não há job em background
  varrendo o catálogo.

---

## 10. Environment Variables Reference

Todas carregadas em `src/adega/config.py` via `pydantic-settings`, a partir de
`.env` na raiz do projeto. **`.env` nunca é commitado**; mantenha `.env.example`
sempre atualizado.

| Variável                       | Tipo  | Padrão                                                    | Descrição                                                                            |
|--------------------------------|-------|-----------------------------------------------------------|--------------------------------------------------------------------------------------|
| `POSTGRES_USER`                | str   | `adega`                                                   | Usuário do Postgres (consumido pelo container do banco)                              |
| `POSTGRES_PASSWORD`            | str   | `changeme`                                                | Senha do Postgres — **trocar antes de qualquer deploy**                              |
| `POSTGRES_DB`                  | str   | `adega`                                                   | Nome do database criado pelo container na primeira execução                          |
| `DATABASE_URL`                 | str   | `postgresql+asyncpg://adega:changeme@localhost:5432/adega` | URL completa consumida pelo SQLAlchemy/Alembic. Trocar para apontar para Postgres gerenciado em produção. |
| `SECRET_KEY`                   | str   | *(obrigatório)*                                           | Chave de assinatura dos JWTs do fastapi-users. Gere com `openssl rand -hex 32` — mín. 32 chars. |
| `ALGORITHM`                    | str   | `HS256`                                                   | Algoritmo de assinatura do JWT                                                       |
| `ACCESS_TOKEN_EXPIRE_MINUTES`  | int   | `60`                                                      | Tempo de expiração do access token em minutos                                        |
| `IMAGES_DIR`                   | str   | `data/images`                                             | Diretório onde as imagens scrapped são salvas (`<uuid>.webp`)                        |
| `SCRAPER_TIMEOUT`              | float | `15.0`                                                    | Timeout em segundos das requisições do scraper (httpx)                               |
| `SCRAPER_USER_AGENT`           | str   | `Adega/1.0 (personal wine cellar manager)`                | Header `User-Agent` usado em todas as requisições de scraping                        |
| `ENVIRONMENT`                  | str   | `development`                                             | `development` \| `production` — controla nível de log e modo de erro do FastAPI       |

> **Nota:** ajustes em variáveis de ambiente que afetam a inicialização do app
> (DB URL, SECRET_KEY) exigem reinício do `uvicorn`. O `--reload` apenas observa
> mudanças no código-fonte.
