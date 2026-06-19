---
name: generate-codex-assets
description: >-
  Generate and install Codex skills, and optionally Codex prompt wrappers, from
  the bundled generate-project Claude assets. Use this when the user wants the
  generate-project maintenance skills or commands to work in Codex, wants to
  install them into .agents/skills or ~/.agents/skills, or wants Codex prompt
  wrappers under ~/.codex/prompts. The source file list must come from
  asset_manifest.txt, using local checkout/package assets when available and
  GitHub only with user consent.
---

# Generate Codex Assets

Generate Codex-native assets from the generate-project Claude assets while
keeping `asset_manifest.txt` as the single source of truth for which files exist.

## What This Skill Does

Use the bundled helper script to:

- Resolve the source assets from a local `generate-project` checkout, an
  installed `generate_project` package, or GitHub.
- Read `asset_manifest.txt`.
- Copy every manifest-listed `skills/<name>/...` tree into a Codex skill
  destination.
- Optionally copy every manifest-listed `commands/<name>.md` file into a Codex
  custom prompt destination.

Do not hardcode asset names such as `release-docs` or `update-dev-env`; the
manifest decides what exists.

## Destinations

Ask the user where they want the Codex assets installed unless they already
specified a destination:

- Repo-local skills: `.agents/skills`
- User-global skills: `~/.agents/skills`
- Optional Codex prompt wrappers: `~/.codex/prompts`

Codex skills are preferred for reusable workflows. Prompt wrappers are optional
because Codex custom prompts are a compatibility surface for slash-command-like
usage.

## Workflow

1. Resolve this skill directory and run:

   ```bash
   python <this-skill-dir>/scripts/generate_codex_assets.py --help
   ```

2. If the user wants repo-local skills, run from the target repo:

   ```bash
   python <this-skill-dir>/scripts/generate_codex_assets.py --skill-dest .agents/skills
   ```

3. If the user wants global skills:

   ```bash
   python <this-skill-dir>/scripts/generate_codex_assets.py --skill-dest ~/.agents/skills
   ```

4. If they also want Codex prompt wrappers for the manifest-listed Claude
   commands:

   ```bash
   python <this-skill-dir>/scripts/generate_codex_assets.py --prompts --prompt-dest ~/.codex/prompts
   ```

5. If no local source is available, the helper asks before downloading from
   GitHub. In a non-interactive run, pass `--yes`:

   ```bash
   python <this-skill-dir>/scripts/generate_codex_assets.py --yes --ref main --skill-dest ~/.agents/skills
   ```

6. Report the source used, the destination, installed files, skipped files, and
   whether the user should restart Codex.

## Source Resolution

The helper tries sources in this order:

1. `--assets-dir`, when provided.
2. A local checkout containing `src/generate_project/claude_assets`, searching
   from the current directory and this skill directory upward.
3. An installed `generate_project` package with bundled `claude_assets`.
4. GitHub raw files from `apisani1/generate-project` at `--ref`.

All source modes read `asset_manifest.txt` before deciding what to install.

## Safety Rules

- Use `--dry-run` when the user wants a preview.
- Existing files are skipped unless the user passes `--force`.
- Do not install prompt wrappers unless the user asks for them.
- Do not commit generated Codex assets unless the user explicitly asks.
