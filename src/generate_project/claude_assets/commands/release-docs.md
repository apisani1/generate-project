---
description: Prepare release documentation drafts (commit, tag, changelog, release notes) under .tmp_release_docs/
argument-hint: "[target version, e.g. 2.1.0]"
---

# Prepare Release Docs

Use the **release-docs** skill to prepare the four release documentation drafts for the
current repository and write them to `.tmp_release_docs/`:

- `.tmp_release_docs/commit.txt` — complete release commit message (plain text)
- `.tmp_release_docs/tag.txt` — annotated git tag message (plain text)
- `.tmp_release_docs/changelog.md` — `CHANGELOG.md` entry for this release (markdown)
- `.tmp_release_docs/release_notes.md` — GitHub Release body (markdown)

Follow the skill's workflow: find the previous release tag, inspect the full diff since
then (not just commit subjects), then write all four files directly, overwriting any stale
drafts. Do not ask for confirmation before writing the files.

Target version / extra instructions (optional): $ARGUMENTS

If a target version is given above, use it for the version in the drafts; otherwise infer
the appropriate version bump from the changes.
