# generate-project 2.3.0

This release adds a Codex bootstrap skill that mirrors the existing Claude skill
installer for Codex users, fixes a manifest-generation edge case, and improves
the release tooling ergonomics and CI reliability.

## Added

- **`generate-codex-assets` Codex skill.** A new manifest-driven skill that
  installs generate-project's maintenance skills (and optionally prompt wrappers)
  into Codex from the same `asset_manifest.txt` used by `install-skills`. It
  resolves assets from a local checkout, an installed package, or GitHub (with
  explicit user confirmation). Flags: `--dry-run`, `--force`, `--yes`, `--ref`,
  `--prompts`. Skill names are never hardcoded — the manifest decides what ships.

## Fixed

- **Asset manifest excludes hidden directories and `__pycache__`.**
  `skills.py`'s manifest generator now skips any file whose path contains a
  hidden directory component or `__pycache__`, preventing stray non-asset files
  from appearing in the manifest.

## Changed

- **`ARGS` forwarding in `make release-*` targets.** All Makefile release targets
  now accept an `ARGS` variable that is passed through `run.sh` to
  `scripts/release.py`. Example: `make release-minor ARGS="--no-push"`.

## Internal / CI

- ReadTheDocs step in the release workflow (root and both templates) now:
  explicitly syncs versions before activation, waits 20 s for the sync to settle,
  accepts any 2xx HTTP response (not just 204), triggers builds for both the
  newly released tag and `latest`, and reports actual RTD outcome in the job
  summary.

## Upgrade notes

No breaking changes — upgrading is safe.
