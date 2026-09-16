# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `python -m prompt2box` runs the CLI, for environments where the console
  script is not on `PATH`.
- End-to-end CLI tests (JSON output, annotated image, exit codes) using a fake
  detector, so the command-line path is covered without network access.

### Changed
- The project now lives under the Hebula Labs organization; all repository
  links, badges, and packaging metadata point at
  `github.com/hebula-labs/Prompt2Box`.
- Packaging metadata: PEP 639 license expression, full Python-version and
  `Typing :: Typed` classifiers, and a `Changelog` project URL.

### Fixed
- The upload MIME type is taken from the format Pillow actually decoded rather
  than the file extension, so a misnamed file (a JPEG saved as `.png`) is sent
  with the correct type.
- `Detection.crop()` now opens HEIC/HEIF sources, registering the HEIF opener
  the same way `detect()` and `save_annotated()` do.
- The CLI closes its Gemini client after detection instead of leaving the
  connection pool to be garbage-collected.

### Tooling
- CI: least-privilege token permissions, cancellation of superseded runs, pip
  caching, macOS and Windows runs, coverage reporting, a package build with a
  clean-environment wheel smoke test, and a single `CI passed` status check for
  branch protection.
- Tag-driven `Release` workflow that re-runs the quality gate, verifies the tag
  matches `pyproject.toml`, and attaches the sdist and wheel to a GitHub
  Release. PyPI publishing is opt-in via the `PUBLISH_TO_PYPI` repository
  variable and Trusted Publishing.
- CodeQL scanning, Dependabot (pip and GitHub Actions, grouped weekly), YAML
  issue forms, a pull request template, `CODEOWNERS`, `SECURITY.md`,
  `CODE_OF_CONDUCT.md`, and `.editorconfig`.
- Pre-commit hooks updated (ruff 0.16, pre-commit-hooks 6.0) and extended with
  JSON, merge-conflict, and private-key checks.
- `ruff` and `mypy` are pinned to exact versions in the `dev` extra, and
  Markdown files are excluded from ruff, so formatter upgrades land as
  Dependabot PRs rather than failing CI unannounced.

## [0.1.0] - 2026-06-27

### Added
- `detect()` one-shot API and reusable `Detector` class.
- `Detection` / `DetectionResult` result objects (crop, filter, to_json,
  save_annotated, list-like access).
- Two auth backends: Gemini Developer API key and Vertex AI (`--vertex`).
- `Detector.detect_batch()` for concurrent multi-image detection.
- CLI: `prompt2box` with `--classes`, `--prompt`, `--vertex`, `--json-out`.
- Friendly error guidance when an AI Studio `AQ.` auth key is used (currently
  rejected by the Developer API).
- Mocked test suite + golden-response test; ruff lint; CI matrix.
- Dev tooling: pre-commit (ruff + ruff-format), `examples/detect.py`,
  and `CITATION.cff`.
- Automatic downscaling of large images before upload (`max_image_size` /
  `--max-size`) - cuts cost/latency without affecting accuracy.
- HEIC/HEIF support via the optional `[heic]` extra (`pillow-heif`), with a
  clear error when it's missing.
- IoU evaluation harness in `eval/` (precision / recall / mean-IoU) plus
  unit tests, and an opt-in real-API integration test.
- `refine()` / `detect(refine=...)` / `RefineConfig`: deterministically drop
  whole-image catch-all boxes, near-duplicates, and (optionally) tiny/blocklisted
  ones, recording why each was dropped in `.dropped`.
- CLI `.env` loading (current directory; real env vars take precedence).
- Any Gemini vision model works via `model=` / `-m`; a non-Gemini model id warns
  (box_2d detection is Gemini-specific).

### Hardening (production-readiness pass)
- Structured output: detection sends a `response_schema` and reads the SDK's
  schema-validated `response.parsed` (the text parser stays as a backstop).
- `Detector` is a context manager with `close()`; the one-shot `detect()` closes
  its client automatically, so no connection pool leaks.
- Retries now key off the SDK's typed HTTP status code instead of string-matching
  the error message (no false positives on a coincidental "503").
- Safety blocks / truncation surface a real reason (`finish_reason`,
  `block_reason`) instead of a bare "empty response".
- `detect_batch()` builds a `genai.Client` per worker thread and closes them
  afterward (no shared client, no leaked connections).
- A per-request timeout is configured (no indefinite stalls).
- `Detection` is now an immutable (frozen) value object; `box_normalized` is an
  ordered 4-tuple.
- Large PNGs stay lossless when downscaled (JPEG only for photographic formats,
  alpha kept only when present).
- Annotated-output and HEIC handling no longer crash on `.heic`/`.gif` inputs;
  HEIF registration is thread-safe.
- CLI `.env` parsing tolerates `export ` and inline comments.
- Typed (`py.typed`) and type-checked (mypy in CI); CI also enforces
  `ruff format` and runs on Python 3.10-3.13.

[Unreleased]: https://github.com/hebula-labs/Prompt2Box/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hebula-labs/Prompt2Box/releases/tag/v0.1.0
