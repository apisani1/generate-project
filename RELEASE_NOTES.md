# generate-project 2.2.0

This release makes the bundled Claude asset manifest self-maintaining at release
time and lets a single `release.py` be shared across the generator and its
templates, plus a few dependency security pins for the Poetry template docs.

## Added
- **Manifest auto-regeneration on release.** `scripts/release.py` now regenerates
  the bundled Claude asset manifest (`claude_assets/asset_manifest.txt`) and folds
  any change into the release commit, so a published package can never ship a
  manifest that's out of sync with the asset tree.

## Changed
- **One shared `release.py`.** The `generate_project.skills` import is now optional
  (`try`/`except`), so manifest regeneration cleanly no-ops in generated projects
  that don't have the module — letting the root repo and both templates use a
  byte-identical `release.py`.
- **`run.sh`:** manifest regeneration moved from `format` to `check` (pre-commit
  and the release flow still keep it fresh).

## Security
- The Poetry template's `docs/requirements.txt` now pins `urllib3>=1.26.19`,
  `zipp>=3.19.1`, `idna>=3.15`, and `pygments>=2.20.0` (Snyk) to avoid known
  vulnerabilities in transitive documentation dependencies.

## Upgrade notes
No breaking changes — upgrading is safe.
