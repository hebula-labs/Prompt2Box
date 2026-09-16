# Contributing to Prompt2Box

Thanks for your interest! Prompt2Box is a small, focused library: a thin,
ergonomic wrapper around Gemini's spatial-understanding mode, maintained by
[Hebula Labs](https://github.com/hebula-labs). Contributions that keep it small
and sharp are very welcome.

By participating you agree to our [Code of Conduct](./CODE_OF_CONDUCT.md).

## Ways to contribute

- **Report a bug** or **request a feature** through the
  [issue templates](https://github.com/hebula-labs/Prompt2Box/issues/new/choose).
  For anything security-related, follow [SECURITY.md](./SECURITY.md) instead.
- **Improve the docs.** Typos, clearer examples, and FAQ entries are always
  welcome and need no prior discussion.
- **Fix a bug or add a feature.** For anything beyond a small fix, open an issue
  first so we can agree on the approach before you invest time in it.

## Dev setup

```bash
git clone https://github.com/hebula-labs/Prompt2Box
cd Prompt2Box
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -e ".[dev]"
pre-commit install   # optional: runs ruff on every commit
```

You do not need a Gemini API key to develop or run the tests. The suite injects
a fake client via `Detector(client=...)`, so it is fast and fully offline. The
one live-API test in `tests/test_integration.py` skips itself unless
`GEMINI_API_KEY` or `GOOGLE_CLOUD_PROJECT` is set.

## Quality gate

Every pull request must pass the same checks CI runs:

```bash
ruff check .                # lint
ruff format --check .       # formatting (run `ruff format .` to fix)
mypy                        # type check the package
pytest -q                   # tests
```

CI runs these on Python 3.10 through 3.13 on Linux, plus one run each on macOS
and Windows, and builds and smoke-installs the wheel. A single `CI passed`
status check summarizes all of it.

Please add or update a test for any behavior change. Tests live in `tests/`
and follow the existing pattern: build a `FakeClient` with the response you
want, run detection, assert on the result.

## Pull request process

1. Fork the repository and create a branch from `main` with a descriptive name
   (`fix/heic-crop`, `docs/vertex-setup`).
2. Make your change, keeping commits focused. Write commit messages in the
   imperative mood ("Add HEIC support to crop()"), with a body explaining *why*
   when it is not obvious.
3. Add a line under **Unreleased** in [`CHANGELOG.md`](./CHANGELOG.md) for any
   user-visible change. Tooling-only changes do not need one.
4. Open the pull request and fill in the template. Link the issue it addresses.
5. A maintainer will review it. We aim to respond within a week. Small, focused
   PRs get merged fastest.

We squash-merge, so the PR title and description become the commit message.
Make them count.

## Scope

Good fits: better parsing robustness, output formats, drawing options, CLI
ergonomics, docs, and test coverage.

Out of scope: turning this into a general agent framework, supporting
non-Gemini models for detection (the `box_2d` output is a Gemini-trained
capability), or adding heavyweight non-optional dependencies. If in doubt, open
an issue first.

## Releasing (maintainers)

Releases are tag-driven. The `Release` workflow re-runs the full quality gate,
checks that the tag matches `pyproject.toml`, builds the sdist and wheel, and
attaches them to a GitHub Release.

1. Bump `version` in `pyproject.toml` and `version` / `date-released` in
   `CITATION.cff`.
2. In `CHANGELOG.md`, rename **Unreleased** to the new version with today's
   date, add a fresh empty **Unreleased** section, and update the comparison
   links at the bottom.
3. Merge to `main`, then tag and push:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

Publishing to PyPI is opt-in: set the repository variable `PUBLISH_TO_PYPI`
to `true` and configure a PyPI Trusted Publisher for this repository. See the
comment at the top of `.github/workflows/release.yml`.
