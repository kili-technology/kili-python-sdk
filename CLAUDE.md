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

- There are **two public surfaces over the same use cases**: `kili.client_domain.Kili` (namespaced — `assets.list(...)`, `labels.create_default(...)`) and the legacy `kili.client.Kili` (mixins — `count_assets(...)`). Neither delegates to the other, and `client_domain` appears in no README or documentation page, so a capability added to one is simply absent from the other.
- The test job enforces `--cov-fail-under=75`: a change that adds uncovered code fails CI on coverage, not on a failing test.
- `tests/e2e/` holds notebooks only — there is no Python e2e suite any more, and CI's `--ignore tests/e2e/` is vestigial.
- Releasing is **two deliberate human steps**: dispatch `pre_release.yml` (bump2version, tag, draft) against `main` for SaaS or `release/XX.Y` for an LTS — where only `patch` is allowed — then publish the GitHub Release, which is what uploads to PyPI. Merging to `main` publishes nothing.
- The floor is Python **3.10** (`requires-python`, and ruff, pyright and pylint all target it). Pyright in CI is what catches newer syntax.
