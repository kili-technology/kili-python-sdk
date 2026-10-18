<!--
    Review: 22/09/2026

    Rules for this file (Anthropic guidance):
    - keep it under 200 lines
    - `/doctor` trims anything Claude can derive from the code
    - every line must answer "would removing this make Claude get it wrong?"
    - no architecture summaries, no dependency lists, no file-by-file map (Claude reads those faster than we maintain them)
-->

# kili-python-sdk

The public Python client. `CONTRIBUTING.md` covers the environment, the tests and the PR convention.

## Gotchas

- There are **two public surfaces**: `kili.client_domain.Kili` (namespaces — `assets.list(...)`), the default, most of whose methods wrap a legacy method through `self._client`, and the deprecated `kili.client.Kili` (mixins — `count_assets(...)`), which warns when a user builds it — the domain client builds its own (`legacy_client`) without the warning. Neither picks up the other's additions: a method added only to a mixin is missing from the namespaces and documented only under "Legacy Reference (deprecated)".
- The test job enforces `--cov-fail-under=75`: a change that adds uncovered code fails CI on coverage, not on a failing test.
- `tests/e2e/` holds notebooks only — there is no Python e2e suite any more, and CI's `--ignore tests/e2e/` is vestigial.
- Releasing is **two deliberate human steps**: dispatch `pre_release.yml` (bump2version, tag, draft) against `main` for SaaS or `release/XX.Y` for an LTS — where only `patch` is allowed — then publish the GitHub Release, which is what uploads to PyPI. Merging to `main` publishes nothing.
- The floor is Python **3.10** (`requires-python`, and ruff, pyright and pylint all target it). Pyright in CI is what catches newer syntax.
- CI lints through pre-commit, whose pinned ruff runs `--fix-only` (only an autofixable finding fails), plus pylint and pyright on `src/kili` alone: a bare `ruff check` or `pyright` reports a backlog CI ignores. Check a change with `pre-commit run --files <changed files>`, `pylint --rcfile=.pylintrc src/kili` and `pyright src/kili`.
- pre-commit's docformatter and ruff undo each other on a docstring made only of a summary wrapped onto a second line, so the hook never passes: keep a docstring's summary on one line.
- CI's `doc-build-test` fails on any `WARNING` that `mkdocs build` prints, not only on a failed build — e.g. a docstring `Args:` entry for a parameter the signature lacks: check a docstring change with `mkdocs build 2>&1 | grep WARNING`.
- `mkdocs.yml` filters out only dunder members, so a `_private` method with a docstring on a class the reference pages render is published with the public API: give such a helper a comment, not a docstring.
- A field added to a GraphQL input (`ProjectWhere`, `ProjectData`, …) must be sent only when the caller sets it: the client drops `None` keys from `where` / `data`, but sends `False`, `[]` or any other default, and an older on-premise backend rejects an input field it does not know. Default new input fields to `None`.
- A domain namespace holds its client through a `weakref`: in a unit test, create the mock client in its own fixture, never inline in the namespace's constructor, or `_client` raises `ReferenceError … garbage collected` — with a `MagicMock` only once the garbage collector runs, so the test fails intermittently.
- The SDK's end-to-end tests live in `e2e-tests-docker-app`: its nightly API leg clones this repo's `main` and runs `api/e2e/` plus a listed set of `recipes/*.ipynb` against a full stack; nothing in this repo executes the recipes. A change to what a public method accepts or returns, or a renamed recipe, is grepped there, and the companion MR lands the same day.
