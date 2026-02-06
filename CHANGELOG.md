# Changelog

## [1.2.0b2] - 2026-02-06

 ### Changes
- 📝 docs: update app Quick Start to show CLI usage instead of Python import



## [1.2.0b1] - 2026-02-06

 ### Changes
- 📝 docs: adapt documentation templates for app vs library projects
- ✅ test: add tests for library vs application project types
- ✨ feat: add --library flag for library vs application projects



## [1.1.1] - 2026-02-05

 ### Changes
- 📝 docs: add documentation for --version option


## [1.1.1rc2] - 2026-02-05

 ### Changes
- 🐛 fix: correct GitHub Actions script context in docs workflow



## [1.1.1rc1] - 2026-02-05

 ### Changes
- ✨ feat: add --version option to CLI
- 🐛 fix: search for .env file from current working directory


## [1.1.0] - 2025-12-23

### New Features:
✨ Support for `.` as project name: Generate project files directly in the current directory without creating a subdirectory   
✨ Local environment file option: New `--local-env` flag to create a project-specific `.env` file with authentication tokens for manual publishing workflows

### CI/CD Enhancements:
🚀 Added pull_request trigger to test workflows for automatic PR testing   
🔧 Added VS Code configuration to root project for improved developer experience

### Documentation Improvements:
📝 Added CLAUDE.md integration guide to project template for Claude Code users   
📝 Enhanced reference documentation with comprehensive `v1.1.0` features and examples   
📝 Improved publishing setup documentation and command examples   
📝 Improved command `--help` with context-specific help epilogs   


## [1.0.3rc11] - 2025-12-19

 ### Changes
- 📝 docs: add context-specific help epilogs for CLI commands
- ♻️ refactor: consolidate credential file creation into generic function



## [1.0.3rc10] - 2025-12-19

 ### Changes
- 🐛 fix: resolve FileNotFoundError in project generation



## [1.0.3rc9] - 2025-12-18

 ### Changes
- fix: add template documentation and fix bash syntax errors
- feat: implement tool-agnostic credential management



## [1.0.3rc7] - 2025-12-16

 ### Changes
- 🐛 fix: add v2 prefix to Poetry cache keys to force invalidation
- 🐛 fix: include poetry.lock in CI cache key for proper invalidation
- 🐛 fix: add roman package for Sphinx/Python 3.13 compatibility


## [1.0.3rc6] - 2025-12-15

 ### Changes
- ♻️ refactor: simplify publishing instructions output



## [1.0.3rc5] - 2025-12-15

 ### Changes
- 💄 style: improve color consistency in terminal output



## [1.0.3rc4] - 2025-12-15

 ### Changes
- refactor: simplify GitHub repository ownership check



## [1.0.3rc3] - 2025-12-15

 ### Changes
- 🐛 fix: improve error message when directory already exists



## [1.0.3rc2] - 2025-12-15

 ### Changes
- 🐛 fix: prevent crash when GitHub repository already exists



## [1.0.3rc1] - 2025-12-15

 ### Changes
- feat: activate ReadTheDocs for all version tags
- feat: modernize project with PEP 621 dual format (root + template)
  


## [1.0.2.post1] - 2025-07-09

 ### Changes
- Add detailed documentation
- Force documentation github check
- Fix module import issue when running tests locally


## [1.0.2] - 2025-07-06

 ### Changes
- Fix generate command flags
- Add toml type stub


## [1.0.1.post3] - 2025-07-04

 ### Changes
- Include template folder in the generated package



## [1.0.1.post2] - 2025-07-04

 ### Changes
- Add test suite
- Add user configuration file


## [1.0.1.post1] - 2025-07-03

 ### Changes
- Update README.md



## [1.0.1] - 2025-07-02

 ### Changes
- First release


## [1.0.0] - 2025-07-02

 ### Changes
- First release


## [0.1.0] - 2025-07-02

 ### Changes
- First release


## [0.1.0] - 2025-07-02

 ### Changes
- First version

