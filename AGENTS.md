# AGENTS.md — Coding Standards for linkedin2md

## Code Style (Python)

- **Formatter**: ruff (line length 88, target Python 3.13+)
- **Type checker**: pyright (strict mode)
- **Linting**: ruff check with rules E, W, F, I, B, UP
- **Imports**: sorted by ruff (isort-compatible)
- **String quotes**: prefer double quotes (`"`)
- **Type annotations**: required on all public function signatures

## Testing

- **Framework**: pytest
- **Test location**: `tests/` directory, files named `test_*.py`
- **All tests must pass** before merging — `pytest -v`
- **Test classes**: group related tests in `class TestXxx` with descriptive docstrings
- **Edge cases**: test empty inputs, None, unicode, special characters
- **Security tests**: path traversal, URL sanitization, file size limits

## Git Commits

- Use conventional commit format: `type: description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`
- Reference issue numbers: `fix #2`, `closes #5`
- Keep commits focused — one logical change per commit

## Architecture

- **Zero-dependency core**: only Python stdlib in the main package
- **Dependency injection**: use factory functions (`create_converter()`)
- **Separation**: parsers → formatter → writer, no circular imports
- **CLI**: `cli.py` is the thin entry point, logic lives in domain modules

## Universal Rules (all files)

REJECT if:
- Hardcoded secrets or credentials
- Silent error handling (empty `except: pass`, empty `catch {}` blocks)
- `TODO` or `FIXME` without a linked issue number

REQUIRE:
- Descriptive variable and function names
- Error messages that help debugging