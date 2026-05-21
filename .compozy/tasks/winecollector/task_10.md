---
status: pending
title: Image normalizer (Pillow → WebP)
type: backend
complexity: low
dependencies:
  - task_01
---

# Task 10: Image normalizer (Pillow → WebP)

## Overview
Implement the helper that turns any image the scraper downloads into a uniform `<uuid>.webp` file on disk. Per ADR-008, every wine image lands as WebP at quality 85 with a 1600px cap, executed off the event loop.

<critical>
- ALWAYS READ the PRD and TechSpec before starting
- REFERENCE TECHSPEC for implementation details — do not duplicate here
- FOCUS ON "WHAT" — describe what needs to be accomplished, not how
- MINIMIZE CODE — show code only to illustrate current structure or problem areas
- TESTS REQUIRED — every task MUST include tests in deliverables
</critical>

<requirements>
- `save_image_as_webp(content: bytes, dest_dir: Path) -> Path` MUST live at `src/winecollector/services/scraping/images.py`.
- The function MUST write the file as `<uuid>.webp` and return the resulting `Path`.
- Conversion MUST use Pillow with `format="WEBP"`, `quality=85`, `method=4`.
- Images larger than 1600px on the longer edge MUST be resized down preserving aspect ratio.
- RGBA inputs MUST be converted to RGB before WebP encoding.
- `Pillow.Image.MAX_IMAGE_PIXELS` MUST be set to a safe limit (e.g., 24 megapixels) before opening the image.
- The function MUST be safe to call from an async context via `await asyncio.to_thread(...)` — no event loop work inside.
- Invalid image bytes MUST raise `ValueError` (not a generic `Exception`).
</requirements>

## Subtasks
- [ ] 10.1 Implement `src/winecollector/services/scraping/images.py` with `save_image_as_webp`.
- [ ] 10.2 Set the `MAX_IMAGE_PIXELS` guard module-side.
- [ ] 10.3 Add small in-memory test fixtures (a 10×10 JPEG and a 10×10 PNG with alpha) generated in `conftest.py`.
- [ ] 10.4 Verify the function returns a relative path under `dest_dir`.

## Implementation Details
See TechSpec section "Integration Points" → image conversion and ADR-008 for the conversion parameters. The function is intentionally synchronous — the async wrapper is the responsibility of the scraper (task_11) via `asyncio.to_thread`.

### Relevant Files
- `src/winecollector/services/scraping/images.py` — to be created.

### Dependent Files
- `src/winecollector/services/scraping/scraper.py` (task_11) — calls this helper for every successful scrape.

### Related ADRs
- [ADR-008: Convert Wine Images to WebP via Pillow on Download](adrs/adr-008.md) — drives every parameter choice in this task.

## Deliverables
- A working synchronous WebP converter.
- Unit tests with 80%+ coverage **(REQUIRED)**.
- No integration tests required (pure file I/O against a tmp directory).

## Tests
- Unit tests:
  - [ ] `tests/unit/test_image_normalizer.py::test_jpeg_input_produces_webp_file` — a JPEG byte string produces a `.webp` file on disk with WebP magic bytes.
  - [ ] `tests/unit/test_image_normalizer.py::test_png_with_alpha_is_converted_to_rgb` — RGBA input does not raise; output is RGB WebP.
  - [ ] `tests/unit/test_image_normalizer.py::test_oversized_image_is_resized` — a 2000×3000 input is resized so the longer edge is ≤ 1600px.
  - [ ] `tests/unit/test_image_normalizer.py::test_small_image_is_not_resized` — a 100×100 input is saved at original dimensions.
  - [ ] `tests/unit/test_image_normalizer.py::test_invalid_bytes_raise_value_error` — `b"not an image"` raises `ValueError`.
  - [ ] `tests/unit/test_image_normalizer.py::test_path_is_under_dest_dir` — returned path's parent equals the dest dir.
- Integration tests: not applicable.
- Test coverage target: >=80%
- All tests must pass

## Success Criteria
- All tests passing
- Test coverage >=80%
- The function is callable from an `await asyncio.to_thread(...)` without blocking the loop.
