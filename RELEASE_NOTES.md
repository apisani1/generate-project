## generate-project 2.5.0

A security-hardening release for project generation, release tooling and CI workflows, with one
behavior change for scripted use of `--template`.

### ⚠️ Upgrade notes
- **Custom templates need confirmation.** `generate --template <path>` (outside the package) now
  lists the template's `hooks/` scripts and asks before running. In non-interactive environments
  (CI, pipes) it is refused unless you pass the new `--yes` flag.
- **Release rollback file renamed.** `scripts/release.py` now writes `.before_last_release.json`
  instead of `.before_last_release.pkl`. Finish or roll back any in-progress release before
  upgrading. Regenerate or run `/update-dev-env` to pick up the new `release.py` and `.gitignore`.

### Changed
- `--help` output is tidier: commands are listed once, a quick-start covers every command, and
  text fits in 80 columns.

### Added
- `--yes` flag to skip the custom-template confirmation.
- Dependabot config for GitHub Actions (weekly; minor/patch batched, majors as separate PRs) in the
  repo and both templates.
- `/update-dev-env` now syncs `dependabot.yml` and `.gitignore`.

### Security
- Jinja syntax (`{{`, `{%`, `{#`) is rejected in the project name, CLI options and `config.yaml`
  values, since cookiecutter would evaluate it as code.
- `.env` / `.pypirc` are created owner-only (`0600`), never overwritten, and never written through
  a symlink.
- Release rollback state is plain JSON, not a pickle.
- Asset installers refuse manifest paths that could escape the destination.
- Template and repo workflows pin actions to commit SHAs, pass event values via `env:` rather than
  inline expansion, and validate the `update_rtd.yml` version input.

### Documentation
- `--yes` and the custom-template security warning are documented in the reference.

**Full changelog**: https://github.com/apisani1/generate-project/compare/v2.4.0.post1...v2.5.0
