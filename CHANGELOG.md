# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-06-14

### Added
- 86 new unit tests for 8 content parser/formatter pairs (Posts, Comments, Reactions, Reposts, Votes, SavedItems, Events, Media)
- 23 unit tests for PDF exporter (`convert_md_to_pdf`) covering ImportError paths, HTML template structure, unicode, injection blocking, exception handling
- 10 CLI integration tests for `--pdf` flag (section ordering, quiet mode, empty sections, failure modes)
- Test suite: **304 tests** (up from 189 in v0.4.0)

### Changed
- PDF tests use `patch.dict(sys.modules)` for module-level mocking — no weasyprint installation required
- CLI PDF tests mock at `convert_md_to_pdf` boundary for clean isolation

### Fixed
- Template injection test: injected content correctly verified to stay in body, not head

## [0.4.0] - 2026-06-14

### Added
- Job Description (JD) parser and formatter — parses job posting CSVs from LinkedIn exports (#17)
- `--quiet` CLI flag to suppress file listing output (#6)
- `--version` CLI flag (`linkedin2md --version`)
- Script and Articles parser/formatter for content exports
- Unit tests for Messages, Content, Script, Articles parsers and formatters (#2, #3)
- Unit tests for JobDescriptionParser and JobDescriptionFormatter
- CI matrix testing on Python 3.10, 3.11, 3.12, 3.13
- Dependabot configuration for automated dependency updates
- Stale issue/PR management workflow
- First-time contributor welcome workflow
- Pre-commit hook configuration (ruff, pyright)
- N3RV agent MCP servers: n3rv-memory, n3rv-hub
- Sequential-thinking MCP server for agentic workflows
- Plugin file rename nerv → n3rv with internal reference updates

### Changed
- **BREAKING**: Minimum Python version lowered from >=3.13 to >=3.10
- nerv → n3rv complete rename across agent config, plugins, and MCP servers
- Moved analytics to centralized UMD on data.daza.ar
- GitHub MCP restored to wrapper script for automatic token detection
- opencode.json MCP config overhaul (dedup servers, sequential-thinking)
- Author email updated to juan@daza.ar
- CODE_OF_CONDUCT.md and SECURITY.md updated with N3RV references

### Fixed
- Removed stale nerv-memory/nerv-hub MCP server duplicates
- JobDescriptionFormatter empty-company heading fallback (uses title or "Unknown")
- Missing test_parse_no_scripts_key in TestScriptParser
- Lint issues (E402, E501) in rescued test files
- Import ordering in parsers/formatters __init__

## [0.3.1] - 2026-05-22

### Added
- Optional A4 PDF Resume Generator (`--pdf` flag) producing print-ready professional CVs via WeasyPrint
- N3RV Agentic Development framework configuration (opencode.json, agents, skills)
- GitHub Pages landing page with custom domain, structured data, and GA4 Consent Mode v2
- OG image meta tags for social media sharing

### Changed
- Improved README documentation with PDF and N3RV sections
- Better social sharing titles and descriptions

### Fixed
- Type ignore comments for optional imports in pdf.py to pass pyright CI
- Long docstring lines in pdf.py to comply with ruff 88-char limit
- Code formatting compliance with ruff standards

## [0.3.0] - 2025-01-20

### Added
- Extensible multilingual system: `BilingualText` → `MultilingualText` supporting N languages
- `LanguageDetector.supported_languages` property for detector introspection
- Proper logging module integration (replaces print statements)
- Fallback chain support in `_get_text()` for flexible language resolution

### Changed
- Version now single-sourced from `pyproject.toml` via `importlib.metadata`
- CLI errors now use structured logging to stderr
- `MultilingualText` uses `**kwargs` for language flexibility while maintaining backward compatibility

### Fixed
- Version mismatch between `__init__.py` and `pyproject.toml`

## [0.2.0] - 2025-01-20

### Added
- Comprehensive test suite with 146 tests (was 58)
- CLI tests for argument parsing and error handling
- End-to-end tests with realistic LinkedIn export data
- Parser tests for all 12 parser modules
- Formatter tests for all 12 formatter modules
- Edge case tests (empty data, Unicode, special characters)
- Security E2E tests (path traversal, malicious content, CSV injection)

### Changed
- Test coverage significantly improved
- More robust handling of edge cases

## [0.1.3] - 2025-01-20

### Fixed
- Fixed all pyright type checking errors
- Updated type annotations to use `Any` for flexible data types in protocols

## [0.1.2] - 2025-01-20

### Changed
- Added `pipx` as recommended installation method
- Added note about "externally-managed-environment" on modern Linux systems

## [0.1.1] - 2025-01-20

### Changed
- Updated README with LLM use cases and example prompts
- Added documentation for compatible AI tools (NotebookLM, Claude, Obsidian, etc.)

## [0.1.0] - 2025-01-20

### Added
- Initial release
- Convert LinkedIn data exports (ZIP) to Markdown files
- Support for 40+ data categories:
  - Profile (name, title, contact, summary)
  - Experience and education
  - Skills and certifications
  - Recommendations and endorsements
  - LinkedIn Learning history
  - Connections and network
  - Posts, comments, and reactions
  - Job applications and saved jobs
  - Activity history (searches, logins)
  - Advertising and privacy data
- Bilingual support (English and Spanish)
- CLI with customizable output directory
- SOLID architecture for extensibility
- Security features (path traversal protection, URL sanitization, file size limits)

[Unreleased]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.3.1...v0.4.0
[0.3.1]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.1.3...v0.2.0
[0.1.3]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/juanmanueldaza/linkedin2md/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/juanmanueldaza/linkedin2md/releases/tag/v0.1.0
