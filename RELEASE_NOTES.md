# generate-project 2.4.0.post1

Documentation-only follow-up to 2.4.0: the `--supacode` flag and `make run`
shipped in that release without corresponding README/reference updates, and
one paragraph had gone stale. No code changes.

## Documentation

- **Supacode Integration.** README.md and docs/source/home.md gain a new
  "Supacode Integration" section covering the `--supacode` flag, what
  `supacode.json` wires up, and the three `make worktree-*` targets
  (`worktree-setup`, `worktree-archive`, `worktree-delete`).
  docs/source/reference.md's Project Type Options table and behavior notes
  now cover `--supacode` alongside `--library` and `--manager`.
- **`make run`.** Added to the Makefile task list in all three docs.
- **`examples/` directory.** Added to the generated Project Structure tree
  (shipped for libraries, removed for applications) in all three docs.
- **Stale content removed.** Deleted a `docs/source/reference.md` paragraph
  describing a PyPI badge `?v=<version>` cache-bust parameter — that behavior
  was already removed in 2.4.0, but the doc describing it never was.

## Upgrade notes

None — this release contains no code or behavior changes.
