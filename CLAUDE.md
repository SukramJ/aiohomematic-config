# CLAUDE.md - AI Assistant Guide for aiohomematic-config

This document provides comprehensive guidance for AI assistants working on the aiohomematic-config codebase.

## Project Overview

**aiohomematic-config** is a presentation-layer Python library that transforms Homematic device paramset descriptions into UI-optimized structures. It operates purely on data structures from `aiohomematic` -- no RPC calls, no protocol knowledge, no CCU access.

### Key Design Principles

- **No RPC knowledge**: This library never talks to a CCU or backend.
- **Protocol-only imports from aiohomematic**: Only types, enums, and TypedDicts. Never concrete classes like `CentralUnit`, `InterfaceClient`, etc.
- **Fully testable without CCU**: All tests use mock `ParameterData` dictionaries.
- **Same quality standards as aiohomematic**: mypy strict, ruff, pylint, 85%+ coverage.

## Codebase Structure

```
aiohomematic_config/        # Main package
    __init__.py             # Public API, __all__
    change_log.py           # ConfigChangeLog, ConfigChangeEntry, build_change_diff
    const.py                # VERSION, constants, thresholds
    form_schema.py          # FormSchemaGenerator
    grouping.py             # ParameterGrouper
    labels.py               # LabelResolver
    session.py              # ConfigSession
    exporter.py             # ConfigExporter
    widgets.py              # WidgetType enum + determine_widget()
    py.typed                # PEP 561 marker

tests/                      # Test suite
    conftest.py             # Shared fixtures
    test_*.py               # Test modules
    helpers/                # Test helper utilities
    bandit.yaml             # Bandit security config

script/                     # Development scripts
    run-in-env.sh           # Virtualenv wrapper
    sort_class_members.py   # Class member ordering
    check_i18n.py           # Translation validation
    lint_kwonly.py           # Keyword-only args linting
    lint_package_imports.py  # Import conventions
    lint_all_exports.py      # __all__ validation
```

## Development Environment Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements_test.txt
pip install -e .
```

## Code Quality & Standards

### Running checks

```bash
# Tests
pytest tests/

# All linters (pre-commit)
prek run --all-files

# Type checking
mypy

# Ruff
ruff check aiohomematic_config/
ruff format --check aiohomematic_config/
```

### Quality gates

- **mypy strict**: All code must pass strict type checking
- **ruff**: Linting and formatting
- **pylint**: Additional static analysis
- **coverage >= 85%**: Enforced by coverage configuration
- **keyword-only args**: All function parameters must be keyword-only (enforced by `lint_kwonly.py`)

### Code conventions

- All modules have `from __future__ import annotations`
- All public APIs use keyword-only arguments (`*` separator)
- Classes use `__slots__` for memory efficiency
- Module-level `__all__` using dynamic inspection pattern
- Pydantic `BaseModel` for serializable data structures
- `Final` type annotation for constants

## Testing Guidelines

- All tests use mock `ParameterData` dictionaries (no CCU needed)
- Shared fixtures in `tests/conftest.py`
- Factory functions in `tests/helpers/parameter_data_factory.py`
- Test files mirror source module names: `test_<module>.py`

## Architecture

### Dependency on aiohomematic

Only import types and utility functions:

```python
from aiohomematic.const import ParameterData, ParameterType, Operations, Flag
from aiohomematic.parameter_tools import validate_paramset, diff_paramset, ...
```

Never import concrete classes like `CentralUnit`, `InterfaceClient`, etc.

### Module dependency graph

```
change_log.py     <- (standalone)
const.py          <- no internal deps
widgets.py        <- const.py
labels.py         <- const.py
grouping.py       <- (standalone)
form_schema.py    <- widgets.py, labels.py, grouping.py, const.py
session.py        <- (standalone, uses aiohomematic.parameter_tools)
exporter.py       <- (standalone)
__init__.py       <- all modules
```

## Git Workflow

- Main development branch: `devel`
- Release branch: `master`
- No direct commits to `devel` or `master`
- Feature branches for all changes
- Pre-commit hooks enforced via `prek`

## Changelog Versioning

- Format: `YYYY.M.P` (e.g., `2026.2.1`)
- Version defined in `aiohomematic_config/const.py`
- Changelog in `changelog.md`
- Both must be updated together for releases
