<!-- Scope: templates/**/*.html — Jinja2, Tailwind CSS, HTMX and Alpine.js conventions -->

# Frontend Conventions

## Stack
- **Jinja2** for server-side HTML templates
- **Tailwind CSS** for styling (utility-first, mobile-first)
- **HTMX** for async interactions without writing JavaScript
- **Alpine.js** only when HTMX alone isn't enough (e.g., local UI state like toggles)

## Template Structure
```
templates/
├── base.html              # Main layout: navbar, footer, Tailwind + HTMX scripts
├── partials/              # Reusable fragments returned by HTMX requests
│   ├── wine_card.html
│   ├── scrape_status.html
│   └── flash_message.html
├── wines/
│   ├── index.html         # Wine list / cellar overview
│   ├── detail.html        # Single wine detail page
│   └── form.html          # Add / edit wine form
└── tastings/
    ├── form.html
    └── list.html
```

## Tailwind Rules
- **Mobile-first**: start with base styles for small screens, use `md:` and `lg:` prefixes for larger
- Use Tailwind's color palette consistently: pick a primary color (e.g., `wine` via a custom config, or `rose-800`) and stick to it
- Never use inline `style=""` attributes — everything via Tailwind classes
- For the MVP, load Tailwind via CDN Play: `<script src="https://cdn.tailwindcss.com"></script>`
- Move to the Tailwind CLI before deploying to production

```html
<!-- ✅ Good — mobile-first responsive card -->
<div class="bg-white rounded-xl shadow p-4 flex flex-col gap-3 md:flex-row md:items-center">
  <img class="w-full h-48 object-contain md:w-24 md:h-32" src="{{ wine.image_path }}" alt="{{ wine.name }}">
  <div>
    <h2 class="text-xl font-semibold text-rose-900">{{ wine.name }}</h2>
    <p class="text-sm text-gray-500">{{ wine.winery }} · {{ wine.vintage }}</p>
  </div>
</div>
```

## HTMX Patterns
- Use `hx-get`, `hx-post`, `hx-put`, `hx-delete` to call FastAPI routes
- Return **HTML fragments** (partials) from those routes, not full pages
- Use `hx-target` to specify which DOM element to update
- Use `hx-swap="outerHTML"` or `"innerHTML"` depending on the case
- Use `hx-indicator` to show a loading spinner during requests

```html
<!-- ✅ Good — HTMX scraping trigger -->
<button
  hx-post="/wines/scrape"
  hx-include="#scrape-form"
  hx-target="#scrape-result"
  hx-swap="innerHTML"
  hx-indicator="#spinner"
  class="btn-primary"
>
  Buscar dados do vinho
</button>
<div id="spinner" class="htmx-indicator">Carregando...</div>
<div id="scrape-result"></div>
```

```python
# ✅ Good — FastAPI route returning an HTML partial
@router.post("/wines/scrape")
async def scrape_wine_route(url: str = Form(...), db: SessionDep) -> HTMLResponse:
    result = await scraper.scrape_wine(url)
    html = templates.TemplateResponse(
        "partials/scrape_result.html",
        {"request": request, "result": result}
    )
    return html
```

## Flash Messages
- Use HTMX's `HX-Trigger` response header to trigger toast notifications
- Keep a `partials/flash_message.html` partial for success/error feedback

```python
# In a FastAPI route after a successful action:
from fastapi.responses import HTMLResponse

response = templates.TemplateResponse("partials/wine_card.html", {...})
response.headers["HX-Trigger"] = '{"showToast": {"message": "Vinho adicionado!", "type": "success"}}'
return response
```

## Forms
- All forms use `hx-post` / `hx-put` — no full-page form submissions
- Show validation errors inline without a full page reload
- The add-wine form should have two modes: **Auto (via URL)** and **Manual**; toggle with Alpine.js if needed

```html
<!-- Toggle between auto/manual input -->
<div x-data="{ mode: 'auto' }">
  <div class="flex gap-2 mb-4">
    <button @click="mode = 'auto'" :class="mode === 'auto' ? 'btn-active' : 'btn'">Buscar por URL</button>
    <button @click="mode = 'manual'" :class="mode === 'manual' ? 'btn-active' : 'btn'">Inserir manualmente</button>
  </div>
  <div x-show="mode === 'auto'"><!-- URL input + scrape button --></div>
  <div x-show="mode === 'manual'"><!-- Full manual form --></div>
</div>
```

## Design Principles
- **Sophisticated but simple**: dark wine reds (`rose-900`, `red-950`) with cream/off-white backgrounds
- Large bottle images on detail pages; compact cards on the list
- Consistent spacing using Tailwind's `gap-*`, `p-*`, `m-*` scale
- Use `object-contain` for wine bottle images (tall bottles shouldn't be cropped)

## No Custom JavaScript Rule
- Do **not** add `<script>` blocks with custom JS unless Alpine.js or HTMX cannot handle the interaction
- If you find yourself writing vanilla JS, stop and ask: can HTMX attributes solve this?
