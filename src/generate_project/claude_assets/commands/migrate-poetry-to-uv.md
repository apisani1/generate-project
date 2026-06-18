---
description: Migrate a Poetry-based generated repo to UV — convert pyproject, swap the lockfile, and re-sync infra files from the UV template
argument-hint: "[version|latest, e.g. 2.1.0 or v2.1.0]"
---

# Migrate Poetry → UV

Migrate the **current repository** from Poetry to UV: convert `pyproject.toml`, switch the lockfile
to `uv.lock`, and re-sync the development-environment files (`run.sh`, `Makefile`, workflows, etc.)
with the UV cookiecutter template from
[`apisani1/generate-project`](https://github.com/apisani1/generate-project), preserving all
project-specific customizations.

The optional argument selects which released UV template version to source the infra files from:
- `2.1.0` or `v2.1.0` — that exact release tag
- `latest` or omitted — the latest **stable** release (pre-releases excluded)

`$ARGUMENTS` holds the requested version (may be empty).

This command relies on the [`migrate-to-uv`](https://github.com/mkniewallner/migrate-to-uv) tool
(run via `uvx`) for the dependency conversion, and reuses the GitHub-fetch + merge mechanics of the
`/update-dev-env` command for the infra files.

---

## Step 0 — Preconditions & safety

1. Confirm the repo is currently **Poetry-based**: `pyproject.toml` has
   `build-backend = "poetry.core.masonry.api"`, or a `[tool.poetry]` table, or a `poetry.lock` file.
   If it already looks like UV (`build-backend = "hatchling.build"` / a `[tool.uv]` table), **stop**
   and report that there is nothing to migrate.
2. Require a **clean git working tree** (`git status --porcelain` is empty). The migration touches
   many files; a clean tree makes the whole change reviewable and revertible via `git diff`.
   - If the tree is dirty, **stop and ask** the user to commit/stash first (or to confirm proceeding
     anyway).
   - Recommend running the migration on a dedicated branch (e.g. `git switch -c migrate-to-uv`).

## Step 1 — Ensure `uv` is installed

Run `uv --version`. If it succeeds, continue.

If `uv` is **not** found:
1. Detect which installers are available on this machine and pick the best option:
   - `brew` available → `brew install uv` (Homebrew-managed location)
   - else `curl` available → Astral standalone installer:
     `curl -LsSf https://astral.sh/uv/install.sh | sh` (installs to `~/.local/bin` by default;
     honor `UV_INSTALL_DIR=<dir>` to choose a different location)
   - else `pipx` available → `pipx install uv`
2. **Ask the user before installing**, telling them the proposed method and the **install location**,
   and let them confirm or change it. Do not install without explicit confirmation.
3. After installing, re-run `uv --version` to verify. `uvx` (used in Step 4) ships with `uv`.

## Step 2 — Detect project values

From the current repo's `pyproject.toml`:
- `project_name` = `[project].name`
- `package_name` = the `include` value in `[tool.poetry].packages`
  (`{ include = "foo", from = "src" }` → `foo`). Fallback: the single directory under `src/`.
- `python_min_version` = `[project].requires-python` (or `[tool.poetry.dependencies].python`) with
  any leading `>=`, `^`, or `~=` stripped.

## Step 3 — Resolve the UV-template version ref

Determine the git ref to fetch the infra files from (same logic as `/update-dev-env`):
1. Normalize the argument: trim whitespace and strip a leading `v`.
2. Empty or `latest` → latest **stable** release:
   ```bash
   gh release view --repo apisani1/generate-project --json tagName -q .tagName
   ```
   GitHub's "latest" already excludes drafts and pre-releases. If `gh` is unavailable, fall back to
   `git ls-remote --tags https://github.com/apisani1/generate-project`, drop tags whose version
   segment matches `rc`, `b`, `beta`, `a`, `alpha`, or `post`, version-sort, and take the highest.
3. Otherwise the ref is `v<version>`; verify it exists
   (`gh api repos/apisani1/generate-project/git/ref/tags/v<version>`). If not, **stop** and report
   recent tags.

**Report the resolved ref to the user** before fetching anything.

### Fetching template files (used in Steps 4 & 5)

Template files live inside a directory literally named `{{cookiecutter.project_name}}`, so its
braces must be percent-encoded (`{{` → `%7B%7B`, `}}` → `%7D%7D`) in the raw URL. For a `<file>`:

```
https://raw.githubusercontent.com/apisani1/generate-project/<ref>/src/generate_project/templates/uv-template/%7B%7Bcookiecutter.project_name%7D%7D/<file>
```

Fetch with `curl -fsSL "<url>"`. After fetching, substitute the cookiecutter variables with the
detected values: `{{ cookiecutter.project_name }}` → `project_name`,
`{{ cookiecutter.package_name }}` → `package_name`,
`{{ cookiecutter.python_min_version }}` → `python_min_version`.

## Step 4 — Convert `pyproject.toml`

1. Run the dependency conversion from the repo root:
   ```bash
   uvx migrate-to-uv
   ```
   This moves `[tool.poetry.dependencies]` into `[project.dependencies]`, each
   `[tool.poetry.group.<name>.dependencies]` into `[dependency-groups].<name>`, converts version
   specifiers (`^1.2` / `~1.2` → PEP 508 ranges), and removes the Poetry tables.
2. Fetch the UV template `pyproject.toml` (Step 3 mechanics) and reconcile, **preserving the
   project's real content**:
   - Ensure `[build-system]` is `requires = ["hatchling"]` / `build-backend = "hatchling.build"`.
   - Ensure `[tool.hatch.build.targets.wheel] packages = ["src/<package_name>"]`.
   - Remove any leftover `[tool.poetry]` tables or `poetry-core` references.
   - **Keep** all migrated project dependencies and dependency groups.
   - **Keep** the project's existing
     `[tool.black|flake8|mypy|pylint|isort|doc8|pytest|semantic_release]` sections (these are shared
     between templates — only add template improvements the current file is missing; never drop
     project-specific tweaks).

## Step 5 — Update infra files from the UV template

Fetch each file below (Step 3 mechanics) and apply the merge strategy. Process **sequentially**:
fetch + substitute variables → read the current file → merge → write.

### Merge Strategies
- **Full Replace** — overwrite the current file entirely with the substituted template.
- **Diff-and-Merge** — apply template improvements while keeping every project-specific addition
  present in the current file.
- **Preserve-First** — the current content takes precedence and is never reduced; the template only
  contributes structure/wording the current file is missing.

| File | Strategy & notes |
|------|------------------|
| `run.sh` | **Diff-and-Merge.** The template version carries the `poetry … → uv …` command swaps and drops the Poetry `python` PATH shim. Preserve project-specific shims, `run:*`/`mcp-*` commands, custom pytest markers, and the `--cov=src/<package_name>` argument. |
| `Makefile` | **Diff-and-Merge.** Preserve custom `run-*`/`test-*` targets and any project-specific tooling targets (insert them in a separated block before `help`). |
| `docs/Makefile` | **Diff-and-Merge.** The template version swaps the three Sphinx invocations from `poetry run … → uv run …` (`sphinx-build`, `sphinx-apidoc`, `sphinx-autobuild`). Preserve any custom Sphinx targets the user added and the `PACKAGEDIR = ../src/<package_name>` value. |
| `.github/workflows/tests.yml` | **Diff-and-Merge.** Preserve "Install system dependencies" steps, custom `run.sh` command names, extra exit-code clauses (e.g. `|| [ $? -eq 5 ]`), and project-only env/secrets. |
| `.github/workflows/docs.yml` | **Diff-and-Merge.** Preserve "Install system dependencies" steps. |
| `.github/workflows/release.yml` | **Diff-and-Merge.** Preserve release-type detection, TestPyPI verification, ReadTheDocs polling, and any extra notify/validate steps. |
| `.readthedocs.yaml` | **Full Replace.** |
| `.vscode/settings.json` | **Diff-and-Merge** at the JSON **key** level: keep every key the user added or changed; bring in new template keys; never drop a key the user has. |
| `CLAUDE.md` | **Preserve-First.** Never reduce hand-written project docs. Only swap Poetry→UV wording in the "Development Commands"/"Development Workflow" sections when the current text is a strict subset of the template. |
| `CredentialManagement.md` | **Full Replace** (standardized doc; differs only in Poetry→UV wording). If the current file has hand-added project-specific sections, preserve them. |

## Step 6 — Lockfile & Poetry cleanup

- Generate the UV lockfile: `uv lock`.
- Delete `poetry.lock`.
- Remove a stray `poetry.toml` if present.

## Step 7 — Verify

Run, reporting any failures with their output:
```bash
uv sync --all-groups     # resolve + install into .venv under UV
make pre-commit          # format + lint changed files (or: ./run.sh check:ci)
make test                # run the test suite under UV
```

## Step 8 — Summary

Report:
- Whether `uv` was installed (method + location) or already present.
- The resolved UV-template ref the infra files came from.
- `pyproject.toml` conversion result: dependencies/groups moved, build backend switched to hatchling.
- Lockfile change: `uv.lock` created, `poetry.lock` removed.
- Per-file changed-vs-preserved notes for the infra files.

Remind the user to review `git diff` before committing — **nothing has been committed**.
