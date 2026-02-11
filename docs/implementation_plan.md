# aiohomematic-config: Comprehensive Implementation Plan

**Date**: 2026-02-11
**Status**: Draft
**Base**: Concept document `aiohomematic/docs/concepts/device_configuration_ui.md`

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Setup](#2-project-setup)
   - [2.1 Repository Structure](#21-repository-structure)
   - [2.2 pyproject.toml](#22-pyprojecttoml)
   - [2.3 MANIFEST.in](#23-manifestin)
   - [2.4 Requirements Files](#24-requirements-files)
   - [2.5 Configuration Files](#25-configuration-files)
3. [Pre-commit Hooks](#3-pre-commit-hooks)
4. [Development Scripts](#4-development-scripts)
5. [GitHub Workflows (CI/CD)](#5-github-workflows-cicd)
6. [Package Implementation](#6-package-implementation)
   - [6.1 Core Module: const.py](#61-core-module-constpy)
   - [6.2 Widget Mapping: widgets.py](#62-widget-mapping-widgetspy)
   - [6.3 Form Schema Generator: form_schema.py](#63-form-schema-generator-form_schemapy)
   - [6.4 Parameter Grouper: grouping.py](#64-parameter-grouper-groupingpy)
   - [6.5 Label Resolver: labels.py](#65-label-resolver-labelspy)
   - [6.6 Config Session: session.py](#66-config-session-sessionpy)
   - [6.7 Config Exporter: exporter.py](#67-config-exporter-exporterpy)
   - [6.8 Package Init: \_\_init\_\_.py](#68-package-init-__init__py)
7. [Translation Files](#7-translation-files)
8. [Test Infrastructure](#8-test-infrastructure)
   - [8.1 conftest.py](#81-conftestpy)
   - [8.2 Test Modules](#82-test-modules)
9. [Documentation](#9-documentation)
10. [Quality Gates](#10-quality-gates)
11. [Implementation Phases](#11-implementation-phases)
12. [Dependency Map](#12-dependency-map)

---

## 1. Project Overview

**aiohomematic-config** is a presentation-layer Python library that transforms Homematic device paramset descriptions into UI-optimized structures. It operates purely on data structures from `aiohomematic` -- no RPC calls, no protocol knowledge, no CCU access.

### Core Responsibilities

| Component             | Purpose                                                 |
| --------------------- | ------------------------------------------------------- |
| `FormSchemaGenerator` | `ParameterData` + values -> JSON form schemas           |
| `ParameterGrouper`    | Flat parameter list -> grouped sections                 |
| `LabelResolver`       | Technical parameter IDs -> human-readable labels (i18n) |
| `ConfigSession`       | Change tracking, undo/redo, dirty state, validation     |
| `ConfigExporter`      | Serialize/deserialize device configurations             |
| `WidgetType` mapping  | `ParameterType` -> appropriate UI widget                |

### Key Design Principles

- **No RPC knowledge**: This library never talks to a CCU or backend.
- **Protocol-only imports from aiohomematic**: Only types, enums, and TypedDicts. Never concrete classes like `CentralUnit`, `InterfaceClient`, etc.
- **Fully testable without CCU**: All tests use mock `ParameterData` dictionaries.
- **Same quality standards as aiohomematic**: mypy strict, ruff, pylint, 85%+ coverage.

### Imported Types from aiohomematic

```python
# Types and enums used (never concrete classes):
from aiohomematic.const import (
    Flag,
    Operations,
    ParameterData,
    ParameterType,
    ParamsetKey,
)
from aiohomematic.parameter_tools import (
    ParamsetChange,
    ValidationResult,
    coerce_value,
    diff_paramset,
    get_parameter_step,
    is_parameter_readable,
    is_parameter_visible,
    is_parameter_writable,
    validate_paramset,
    validate_value,
)
```

---

## 2. Project Setup

### 2.1 Repository Structure

```
aiohomematic-config/
├── aiohomematic_config/              # Main package
│   ├── __init__.py                   # Public API, __all__
│   ├── const.py                      # VERSION, constants, WidgetType enum
│   ├── form_schema.py                # FormSchemaGenerator
│   ├── grouping.py                   # ParameterGrouper
│   ├── labels.py                     # LabelResolver
│   ├── session.py                    # ConfigSession
│   ├── exporter.py                   # ConfigExporter
│   ├── widgets.py                    # Widget type determination
│   ├── py.typed                      # PEP 561 marker
│   ├── strings.json                  # Primary translation source (en)
│   └── translations/                 # i18n translation files
│       ├── en.json                   # English (synced from strings.json)
│       └── de.json                   # German
│
├── tests/                            # Test suite
│   ├── conftest.py                   # Shared fixtures
│   ├── test_widgets.py               # Widget mapping tests
│   ├── test_form_schema.py           # FormSchemaGenerator tests
│   ├── test_grouping.py              # ParameterGrouper tests
│   ├── test_labels.py                # LabelResolver tests
│   ├── test_session.py               # ConfigSession tests
│   ├── test_exporter.py              # ConfigExporter tests
│   └── helpers/                      # Test helpers
│       └── parameter_data_factory.py # Factory for mock ParameterData
│
├── script/                           # Development scripts
│   ├── run-in-env.sh                 # Virtualenv wrapper
│   ├── sort_class_members.py         # Class member ordering
│   ├── check_i18n.py                 # Translation validation
│   ├── check_i18n_catalogs.py        # Translation sync
│   ├── lint_kwonly.py                # Keyword-only args linting
│   ├── lint_package_imports.py       # Package import conventions
│   └── lint_all_exports.py           # __all__ export validation
│
├── docs/                             # Documentation
│   ├── implementation_plan.md        # This document
│   ├── architecture.md               # Architecture overview
│   └── api.md                        # API reference
│
├── .github/                          # GitHub configuration
│   └── workflows/
│       ├── test-run.yaml             # Test execution
│       ├── pre-commit.yml            # Linting CI
│       ├── python-publish.yml        # PyPI release
│       └── release-on-tag.yml        # GitHub release creation
│
├── pyproject.toml                    # Build + tool configuration
├── MANIFEST.in                       # Package distribution
├── requirements.txt                  # Runtime dependencies
├── requirements_test.txt             # Test dependencies
├── requirements_test_pre_commit.txt  # Pre-commit dependencies
├── .pre-commit-config.yaml           # Pre-commit hooks
├── .yamllint                         # YAML linting rules
├── codecov.yml                       # Coverage configuration
├── .gitignore                        # Git ignore rules
├── README.md                         # Project readme
├── changelog.md                      # Release history
├── LICENSE                           # MIT License
└── CLAUDE.md                         # AI assistant guide
```

### 2.2 pyproject.toml

```toml
[build-system]
requires = ["setuptools>=80.9.0"]
build-backend = "setuptools.build_meta"

[project]
name        = "aiohomematic-config"
dynamic = ["version"]
license     = {text = "MIT License"}
description = "Presentation-layer library for Homematic device configuration UI."
readme      = "README.md"
authors     = [
    {name = "SukramJ", email = "sukramj@icloud.com"},
]
keywords    = ["home", "automation", "homematic", "configuration", "paramset"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Natural Language :: German",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.13",
    "Programming Language :: Python :: 3.14",
    "Programming Language :: Python :: Implementation :: CPython",
    "Topic :: Home Automation",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Typing :: Typed",
]
requires-python = ">=3.13"
dependencies = [
    "aiohomematic>=2026.2.9",
    "pydantic>=2.10.0",
]

[project.urls]
"Homepage" = "https://github.com/sukramj/aiohomematic-config"
"Source Code" = "https://github.com/sukramj/aiohomematic-config"
"Bug Reports" = "https://github.com/sukramj/aiohomematic-config/issues"
"Changelog" = "https://github.com/sukramj/aiohomematic-config/blob/devel/changelog.md"

[tool.setuptools]
include-package-data = true

[tool.setuptools.dynamic]
version = {attr = "aiohomematic_config.const.VERSION"}

[tool.setuptools.packages.find]
include = ["aiohomematic_config", "aiohomematic_config.*"]
exclude = ["tests", "tests.*", "dist", "build"]

[tool.setuptools.package-data]
aiohomematic_config = ["py.typed", "translations/*.json", "strings.json"]

# ---------------------------------------------------------------------------
# pylint
# ---------------------------------------------------------------------------

[tool.pylint.MAIN]
py-version = "3.13"
ignore = ["tests"]
jobs = 2
init-hook = """\
    from pathlib import Path; \
    import sys; \
\
    from pylint.config import find_default_config_files; \
\
    sys.path.append( \
        str(Path(next(find_default_config_files())).parent.joinpath('pylint/plugins'))
    ); \
    sys.path.append(".") \
    """
load-plugins = [
    "pylint.extensions.code_style",
    "pylint.extensions.typing",
    "pylint_strict_informational",
    "pylint_per_file_ignores",
]
persistent = false
extension-pkg-allow-list = ["orjson"]

[tool.pylint.BASIC]
class-const-naming-style = "any"
good-names = ["_", "ev", "ex", "fp", "i", "id", "j", "k", "T"]

[tool.pylint."MESSAGES CONTROL"]
disable = [
    "format",
    "abstract-method",
    "broad-except",
    "cyclic-import",
    "duplicate-code",
    "inconsistent-return-statements",
    "import-outside-toplevel",
    "locally-disabled",
    "not-context-manager",
    "too-few-public-methods",
    "too-many-ancestors",
    "too-many-arguments",
    "too-many-instance-attributes",
    "too-many-lines",
    "too-many-locals",
    "too-many-positional-arguments",
    "too-many-public-methods",
    "too-many-boolean-expressions",
    "wrong-import-order",
    "consider-using-namedtuple-or-dataclass",
    # Handled by ruff
    "await-outside-async",
    "bad-str-strip-call",
    "bad-string-format-type",
    "bidirectional-unicode",
    "continue-in-finally",
    "duplicate-bases",
    "format-needs-mapping",
    "function-redefined",
    "invalid-all-format",
    "invalid-all-object",
    "invalid-character-backspace",
    "invalid-character-esc",
    "invalid-character-nul",
    "invalid-character-sub",
    "invalid-character-zero-width-space",
    "logging-too-few-args",
    "logging-too-many-args",
    "missing-format-string-key",
    "mixed-format-string",
    "no-method-argument",
    "no-self-argument",
    "nonexistent-operator",
    "nonlocal-without-binding",
    "not-in-loop",
    "notimplemented-raised",
    "return-in-init",
    "return-outside-function",
    "syntax-error",
    "too-few-format-args",
    "too-many-format-args",
    "too-many-star-expressions",
    "truncated-format-string",
    "undefined-all-variable",
    "undefined-variable",
    "used-prior-global-declaration",
    "yield-inside-async-function",
    "yield-outside-function",
    "anomalous-backslash-in-string",
    "assert-on-string-literal",
    "assert-on-tuple",
    "bad-format-string",
    "bad-format-string-key",
    "bare-except",
    "binary-op-exception",
    "cell-var-from-loop",
    "duplicate-except",
    "duplicate-key",
    "duplicate-string-formatting-argument",
    "duplicate-value",
    "eval-used",
    "exec-used",
    "f-string-without-interpolation",
    "forgotten-debug-statement",
    "format-string-without-interpolation",
    "global-variable-not-assigned",
    "import-self",
    "inconsistent-quotes",
    "invalid-envvar-default",
    "keyword-arg-before-vararg",
    "logging-format-interpolation",
    "logging-fstring-interpolation",
    "logging-not-lazy",
    "misplaced-future",
    "named-expr-without-context",
    "nested-min-max",
    "raise-missing-from",
    "try-except-raise",
    "unused-argument",
    "unused-format-string-argument",
    "unused-format-string-key",
    "unused-import",
    "unused-variable",
    "useless-else-on-loop",
    "wildcard-import",
    "bad-classmethod-argument",
    "consider-iterating-dictionary",
    "empty-docstring",
    "invalid-name",
    "line-too-long",
    "missing-class-docstring",
    "missing-final-newline",
    "missing-function-docstring",
    "missing-module-docstring",
    "multiple-imports",
    "no-else-raise",
    "no-else-return",
    "singleton-comparison",
    "subprocess-run-check",
    "superfluous-parens",
    "ungrouped-imports",
    "unidiomatic-typecheck",
    "unnecessary-direct-lambda-call",
    "unnecessary-lambda-assignment",
    "unneeded-not",
    "useless-import-alias",
    "wrong-import-position",
    "comparison-of-constants",
    "comparison-with-itself",
    "consider-alternative-union-syntax",
    "consider-merging-isinstance",
    "consider-using-alias",
    "consider-using-dict-comprehension",
    "consider-using-generator",
    "consider-using-get",
    "consider-using-set-comprehension",
    "consider-using-sys-exit",
    "consider-using-ternary",
    "literal-comparison",
    "property-with-parameters",
    "super-with-arguments",
    "too-many-branches",
    "too-many-return-statements",
    "too-many-statements",
    "trailing-comma-tuple",
    "unnecessary-comprehension",
    "use-a-generator",
    "use-dict-literal",
    "use-list-literal",
    "useless-object-inheritance",
    "useless-return",
    # Handled by mypy
    "abstract-class-instantiated",
    "arguments-differ",
    "assigning-non-slot",
    "assignment-from-no-return",
    "assignment-from-none",
    "bad-exception-cause",
    "bad-format-character",
    "bad-reversed-sequence",
    "bad-super-call",
    "bad-thread-instantiation",
    "catching-non-exception",
    "comparison-with-callable",
    "deprecated-class",
    "dict-iter-missing-items",
    "format-combined-specification",
    "global-variable-undefined",
    "import-error",
    "inconsistent-mro",
    "inherit-non-class",
    "init-is-generator",
    "invalid-class-object",
    "invalid-enum-extension",
    "invalid-envvar-value",
    "invalid-format-returned",
    "invalid-hash-returned",
    "invalid-metaclass",
    "invalid-overridden-method",
    "invalid-repr-returned",
    "invalid-sequence-index",
    "invalid-slice-index",
    "invalid-slots-object",
    "invalid-slots",
    "invalid-star-assignment-target",
    "invalid-str-returned",
    "invalid-unary-operand-type",
    "invalid-unicode-codec",
    "isinstance-second-argument-not-valid-type",
    "method-hidden",
    "misplaced-format-function",
    "missing-format-argument-key",
    "missing-format-attribute",
    "missing-kwoa",
    "no-member",
    "no-value-for-parameter",
    "non-iterator-returned",
    "non-str-assignment-to-dunder-name",
    "nonlocal-and-global",
    "not-a-mapping",
    "not-an-iterable",
    "not-async-context-manager",
    "not-callable",
    "overridden-final-method",
    "raising-bad-type",
    "raising-non-exception",
    "redundant-keyword-arg",
    "relative-beyond-top-level",
    "self-cls-assignment",
    "signature-differs",
    "star-needs-assignment-target",
    "subclassed-final-class",
    "super-without-brackets",
    "too-many-function-args",
    "typevar-double-variance",
    "typevar-name-mismatch",
    "unbalanced-dict-unpacking",
    "unbalanced-tuple-unpacking",
    "unexpected-keyword-arg",
    "unhashable-member",
    "unpacking-non-sequence",
    "unsubscriptable-object",
    "unsupported-assignment-operation",
    "unsupported-binary-operation",
    "unsupported-delete-operation",
    "unsupported-membership-test",
    "used-before-assignment",
    "using-final-decorator-in-unsupported-version",
    "wrong-exception-operation",
]
enable = [
    "useless-suppression",
    "use-symbolic-message-instead",
]

[tool.pylint.REPORTS]
score = false

[tool.pylint.TYPECHECK]
ignored-classes = ["_CountingAttr"]
mixin-class-rgx = ".*[Mm]ix[Ii]n"

[tool.pylint.FORMAT]
expected-line-ending-format = "LF"

[tool.pylint.EXCEPTIONS]
overgeneral-exceptions = ["builtins.Exception"]

[tool.pylint.TYPING]
runtime-typing = false

[tool.pylint.CODE_STYLE]
max-line-length-suggestions = 120

# ---------------------------------------------------------------------------
# pytest
# ---------------------------------------------------------------------------

[tool.pytest.ini_options]
pythonpath = [".", "aiohomematic_config"]
testpaths = ["tests"]
norecursedirs = [".git", "testing_config"]
log_format = "%(asctime)s.%(msecs)03d %(levelname)-8s %(threadName)s %(name)s:%(filename)s:%(lineno)s %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
]

# ---------------------------------------------------------------------------
# ruff
# ---------------------------------------------------------------------------

[tool.ruff]
target-version = "py313"
line-length = 120

lint.select = [
    "A",
    "ASYNC",
    "B002", "B005", "B007", "B014", "B015", "B018", "B023", "B026", "B032", "B904",
    "C",
    "COM818",
    "D",
    "DTZ003", "DTZ004",
    "E",
    "F",
    "FLY",
    "G",
    "I",
    "INP",
    "ISC",
    "ICN001",
    "LOG",
    "N804", "N805", "N815",
    "PERF",
    "PGH",
    "PIE",
    "PL",
    "PT",
    "PYI",
    "RET",
    "RSE",
    "RUF005", "RUF006", "RUF013", "RUF018", "RUF100",
    "S102", "S103", "S108", "S306", "S307",
    "S313", "S314", "S315", "S316", "S317", "S318", "S319",
    "S601", "S602", "S604", "S608", "S609",
    "SIM",
    "SLOT",
    "T100", "T20",
    "TID251",
    "TRY",
    "TC",
    "FURB",
    "UP",
    "W",
]

lint.ignore = [
    "A005",
    "D202", "D203", "D212", "D406", "D407",
    "E501", "E731",
    "PLC1901",
    "PLR0911", "PLR0912", "PLR0913", "PLR0915", "PLR2004",
    "PLW2901",
    "PT011", "PT012", "PT018",
    "SIM115",
    "TRY003", "TRY400",
    "UP040",
    # May conflict with the formatter
    "W191", "E111", "E114", "E117",
    "D206", "D300",
    "Q", "COM812", "COM819", "ISC001",
    "RET503",
    "TRY301",
    "PYI041",
    # TC rules - low benefit for this project
    "TC001", "TC002", "TC003", "TC006",
]

[tool.ruff.lint.flake8-pytest-style]
fixture-parentheses = false

[tool.ruff.lint.flake8-import-conventions.extend-aliases]
"aiohomematic_config" = "hmcfg"

[tool.ruff.lint.per-file-ignores]
"script/*" = ["T20"]
"tests/*.py" = ["D100", "D101", "D102", "D103", "D107", "TRY002"]

[tool.ruff.lint.isort]
force-sort-within-sections = true
required-imports = ["from __future__ import annotations"]
known-first-party = ["aiohomematic_config"]
known-third-party = ["pydantic", "aiohomematic"]
combine-as-imports = true
split-on-trailing-comma = false

[tool.ruff.lint.mccabe]
max-complexity = 25

# ---------------------------------------------------------------------------
# coverage
# ---------------------------------------------------------------------------

[tool.coverage.run]
branch = true
source = ["aiohomematic_config"]
omit = [
    "aiohomematic_config/const.py",
]
parallel = true

[tool.coverage.report]
show_missing = true
skip_empty = true
skip_covered = false
sort = "cover"
precision = 2
fail_under = 85.0
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self\\.debug",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if False:",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@overload",
    "@abstractmethod",
    "@abc.abstractmethod",
    "\\.\\.\\.",
    "except ImportError:",
]

[tool.coverage.html]
directory = "htmlcov"
show_contexts = true

[tool.coverage.xml]
output = "coverage.xml"

# ---------------------------------------------------------------------------
# mypy
# ---------------------------------------------------------------------------

[tool.mypy]
python_version = "3.13"
plugins = ["pydantic.mypy"]
strict = true
show_error_codes = true
follow_imports = "normal"
local_partial_types = true
strict_equality = true
no_implicit_optional = true
warn_incomplete_stub = true
warn_redundant_casts = true
warn_unused_configs = true
warn_unused_ignores = true
exclude = "(?x)(^build/|^dist/|^htmlcov/|^.*\\.egg-info/|^venv/|^script/)"
enable_error_code = [
    "ignore-without-code",
    "redundant-self",
    "truthy-iterable",
]
disable_error_code = [
    "annotation-unchecked",
    "import-not-found",
    "import-untyped",
]
extra_checks = false
check_untyped_defs = true
disallow_incomplete_defs = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_decorators = true
disallow_untyped_defs = true
warn_return_any = true
warn_unreachable = true
```

### 2.3 MANIFEST.in

```
graft aiohomematic_config
include README.md
include LICENSE
prune tests
prune build
prune dist
```

### 2.4 Requirements Files

**requirements.txt** -- Runtime dependencies:

```
aiohomematic>=2026.2.9
pydantic>=2.10.0
```

**requirements_test.txt** -- Full test dependencies:

```
-r requirements.txt
coverage==7.13.3
freezegun==1.5.5
mypy==1.19.1
pip>=24.0
pre-commit==4.0.0
prek==0.3.2
pylint==4.0.4
pylint-per-file-ignores==1.4.0
pylint-strict-informational==0.2
pytest==9.0.2
pytest-asyncio==0.26.0
pytest-cov==6.1.1
pytest-timeout==2.4.0
pytest-xdist==3.5.0
ruff==0.15.0
```

**requirements_test_pre_commit.txt** -- Pre-commit subset:

```
ruff==0.15.0
codespell==2.4.1
yamllint==1.38.0
```

### 2.5 Configuration Files

**.yamllint**:

```yaml
---
ignore: |
  .github/workflows/python-publish.yml
rules:
  braces:
    max-spaces-inside: 1
  brackets:
    max-spaces-inside: 0
  colons:
    max-spaces-after: -1
  commas:
    max-spaces-after: -1
  comments:
    require-starting-space: true
    min-spaces-from-content: 2
  comments-indentation: {}
  document-end: disable
  document-start: disable
  empty-lines:
    max: 1
  hyphens: {}
  indentation:
    indent-sequences: true
    spaces: 2
  key-duplicates: {}
  line-length: disable
  new-line-at-end-of-file: {}
  new-lines:
    type: unix
  octal-values: {}
  truthy:
    allowed-values: ["true", "false"]
    check-keys: false
```

**codecov.yml**:

```yaml
codecov:
  branch: devel
coverage:
  precision: 2
  round: nearest
  range: "70...100"
  status:
    project:
      default:
        target: auto
        threshold: 9%
    patch:
      default:
        target: auto
        threshold: 5%
comment:
  layout: "reach, diff, flags, tree"
  behavior: default
  require_changes: false
ignore:
  - "tests/**"
  - "script/**"
  - "docs/**"
  - "**/__pycache__/**"
flags:
  full-suite:
    paths:
      - aiohomematic_config/
    carryforward: true
component_management:
  individual_components:
    - component_id: form-schema
      name: "Form Schema Module"
      paths:
        - aiohomematic_config/form_schema.py
        - aiohomematic_config/widgets.py
    - component_id: grouping
      name: "Grouping Module"
      paths:
        - aiohomematic_config/grouping.py
    - component_id: session
      name: "Session Module"
      paths:
        - aiohomematic_config/session.py
    - component_id: labels
      name: "Labels Module"
      paths:
        - aiohomematic_config/labels.py
```

**.gitignore**:

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
dist/
*.egg-info/
*.egg

# Virtual environments
venv/
.venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Coverage
htmlcov/
.coverage
.coverage.*
coverage.xml
coverage.json

# mypy
.mypy_cache/

# ruff
.ruff_cache/

# pytest
.pytest_cache/

# OS
.DS_Store
Thumbs.db
```

---

## 3. Pre-commit Hooks

**.pre-commit-config.yaml**:

```yaml
repos:
  - repo: local
    hooks:
      - id: sort-class-members
        name: sort-class-members
        entry: script/run-in-env.sh python script/sort_class_members.py
        language: script
        types_or: [python]
        files: ^(aiohomematic_config|tests)/.+\.py$
      - id: check-i18n
        name: check-i18n
        entry: script/run-in-env.sh python script/check_i18n.py
        language: script
        types_or: [python]
        files: ^(aiohomematic_config)/.+\.py$
      - id: check-i18n-catalogs
        name: check-i18n-catalogs
        entry: script/run-in-env.sh python script/check_i18n_catalogs.py --fix
        language: script
        always_run: true
        pass_filenames: false
      - id: lint-package-imports
        name: lint-package-imports
        entry: script/run-in-env.sh python script/lint_package_imports.py
        language: script
        types_or: [python]
        files: ^(tests)/.+\.py$
        pass_filenames: false
      - id: lint-all-exports
        name: lint-all-exports
        entry: script/run-in-env.sh python script/lint_all_exports.py
        language: script
        files: ^aiohomematic_config/.+/__init__\.py$
        pass_filenames: false
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.15.0
    hooks:
      - id: ruff
        args:
          - --fix
      - id: ruff-format
        files: ^((aiohomematic_config|script|tests)/.+)?[^/]+\.py$
  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.0
    hooks:
      - id: codespell
        args:
          - --ignore-words-list=ans,hass
          - --skip="./.*,*.csv,*.json"
          - --quiet-level=2
        exclude_types: [csv, json]
  - repo: https://github.com/PyCQA/bandit
    rev: 1.9.2
    hooks:
      - id: bandit
        args:
          - --quiet
          - --format=custom
          - --configfile=tests/bandit.yaml
        files: ^(aiohomematic_config|script|tests)/.+\.py$
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: check-executables-have-shebangs
        stages: [manual]
      - id: check-json
        exclude: (.vscode|.devcontainer)
      - id: no-commit-to-branch
        args:
          - --branch=devel
          - --branch=master
  - repo: https://github.com/adrienverge/yamllint.git
    rev: v1.37.1
    hooks:
      - id: yamllint
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        files: ^.+\.(md|json|ya?ml)$
        exclude: ^(tests/fixtures/)
  - repo: https://github.com/cdce8p/python-typing-update
    rev: v0.7.3
    hooks:
      - id: python-typing-update
        stages: [manual]
        args:
          - --py313-plus
          - --force
          - --keep-updates
        files: ^(aiohomematic_config|tests|script)/.+\.py$
  - repo: local
    hooks:
      - id: mypy
        name: mypy
        entry: script/run-in-env.sh mypy
        language: script
        types_or: [python, pyi]
        require_serial: true
        files: ^(aiohomematic_config)/.+\.py$
      - id: pylint
        name: pylint
        entry: script/run-in-env.sh pylint -j 0
        language: script
        types_or: [python, pyi]
        files: ^(aiohomematic_config)/.+\.py$
      - id: kwonly-lint
        name: kwonly-lint
        entry: script/run-in-env.sh python script/lint_kwonly.py aiohomematic_config
        language: script
        types_or: [python, pyi]
        files: ^(aiohomematic_config)/.+\.py$
```

---

## 4. Development Scripts

All scripts are adapted from aiohomematic. The key scripts to copy and adapt:

### script/run-in-env.sh

Copy verbatim from aiohomematic -- it is project-agnostic.

### script/sort_class_members.py

Copy from aiohomematic. Update file path patterns to target `aiohomematic_config/` instead of `aiohomematic/`.

### script/check_i18n.py

Copy from aiohomematic. Update package path to `aiohomematic_config/`.

### script/check_i18n_catalogs.py

Copy from aiohomematic. Update paths:

- Primary source: `aiohomematic_config/strings.json`
- Target: `aiohomematic_config/translations/en.json`

### script/lint_kwonly.py

Copy from aiohomematic. No changes needed (takes package path as argument).

### script/lint_package_imports.py

Copy from aiohomematic. Update to enforce import conventions for `aiohomematic_config`.

### script/lint_all_exports.py

Copy from aiohomematic. Update package path to `aiohomematic_config/`.

---

## 5. GitHub Workflows (CI/CD)

### .github/workflows/test-run.yaml

```yaml
name: Run tests

on:
  pull_request:
  workflow_dispatch:

jobs:
  tests:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.13", "3.14"]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"
      - name: Install dependencies
        run: pip install -r requirements_test.txt
      - name: Run tests
        run: |
          pytest tests/ \
            --cov=aiohomematic_config \
            --cov-report=xml
      - name: Upload coverage
        if: matrix.python-version == '3.13'
        uses: codecov/codecov-action@v5
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          fail_ci_if_error: false
```

### .github/workflows/pre-commit.yml

```yaml
name: Pre-commit

on:
  pull_request:
    branches:
      - devel
  push:
    branches-ignore:
      - master
      - devel
    tags-ignore:
      - "**"

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    if: github.repository_owner == 'SukramJ'
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.13"
          cache: "pip"
      - name: Install dependencies
        run: pip install -r requirements_test.txt
      - name: Run pre-commit
        run: prek run --all-files
```

### .github/workflows/python-publish.yml

```yaml
name: Publish to PyPI

on:
  repository_dispatch:
    types: [publish]

jobs:
  release-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.client_payload.tag }}
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"
      - name: Build
        run: |
          pip install build
          python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: release-dists
          path: dist/

  pypi-publish:
    runs-on: ubuntu-latest
    needs: release-build
    permissions:
      id-token: write
    environment:
      name: pypi
      url: https://pypi.org/p/aiohomematic-config
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: release-dists
          path: dist/
      - uses: pypa/gh-action-pypi-publish@release/v1
```

### .github/workflows/release-on-tag.yml

```yaml
name: Create Release

on:
  push:
    tags:
      - "**"

jobs:
  release:
    runs-on: ubuntu-latest
    if: github.repository_owner == 'SukramJ'
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
      - name: Extract version
        id: version
        run: echo "version=${GITHUB_REF_NAME}" >> "$GITHUB_OUTPUT"
      - name: Extract release notes
        id: notes
        run: |
          VERSION="${{ steps.version.outputs.version }}"
          NOTES=$(awk "/^# Version ${VERSION}/{flag=1; next} /^# Version /{flag=0} flag" changelog.md)
          PREV=$(awk "/^# Version /{if(seen) {print \$3; exit} if(\$3==\"${VERSION}\") seen=1}" changelog.md)
          if [ -n "$PREV" ]; then
            NOTES="${NOTES}

          **Full Changelog**: https://github.com/${{ github.repository }}/compare/${PREV}...${VERSION}"
          fi
          {
            echo "notes<<NOTES_EOF"
            echo "$NOTES"
            echo "NOTES_EOF"
          } >> "$GITHUB_OUTPUT"
      - name: Create release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.version.outputs.version }}
          name: ${{ steps.version.outputs.version }}
          body: ${{ steps.notes.outputs.notes }}
      - name: Trigger publish
        uses: peter-evans/repository-dispatch@v3
        with:
          event-type: publish
          client-payload: '{"tag": "${{ steps.version.outputs.version }}"}'
```

---

## 6. Package Implementation

### 6.1 Core Module: const.py

**File**: `aiohomematic_config/const.py`

```python
"""
Constants and version for aiohomematic-config.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

import inspect
from typing import Final

VERSION: Final = "2026.2.1"

# Widget slider threshold: if an integer range is <= this value, use a slider
SLIDER_RANGE_THRESHOLD: Final = 20

# Widget radio group threshold: if an enum has <= this many options, use radio buttons
RADIO_GROUP_THRESHOLD: Final = 4

# Default locale
DEFAULT_LOCALE: Final = "en"

__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
```

### 6.2 Widget Mapping: widgets.py

**File**: `aiohomematic_config/widgets.py`

```python
"""
Widget type determination for parameter-to-UI mapping.

Determines the appropriate UI widget for a given Homematic parameter
based on its type, range, and metadata.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

import inspect
from enum import StrEnum, unique

from aiohomematic.const import ParameterData, ParameterType

from aiohomematic_config.const import RADIO_GROUP_THRESHOLD, SLIDER_RANGE_THRESHOLD


@unique
class WidgetType(StrEnum):
    """UI widget types for parameter rendering."""

    TOGGLE = "toggle"
    SLIDER_WITH_INPUT = "slider_with_input"
    NUMBER_INPUT = "number_input"
    RADIO_GROUP = "radio_group"
    DROPDOWN = "dropdown"
    TEXT_INPUT = "text_input"
    BUTTON = "button"
    READ_ONLY = "read_only"


def determine_widget(*, parameter_data: ParameterData) -> WidgetType:
    """
    Determine the appropriate UI widget for a parameter.

    Mapping logic:
    - BOOL                           -> TOGGLE
    - INTEGER (range <= 20)          -> SLIDER_WITH_INPUT
    - INTEGER (range > 20)           -> NUMBER_INPUT
    - FLOAT (range <= 100)           -> SLIDER_WITH_INPUT
    - FLOAT (range > 100)            -> NUMBER_INPUT
    - ENUM (options <= 4)            -> RADIO_GROUP
    - ENUM (options > 4)             -> DROPDOWN
    - STRING                         -> TEXT_INPUT
    - ACTION                         -> BUTTON
    """
    param_type = parameter_data.get("TYPE", ParameterType.EMPTY)

    if param_type == ParameterType.BOOL:
        return WidgetType.TOGGLE

    if param_type == ParameterType.INTEGER:
        p_min = parameter_data.get("MIN", 0)
        p_max = parameter_data.get("MAX", 0)
        if isinstance(p_min, (int, float)) and isinstance(p_max, (int, float)):
            value_range = abs(p_max - p_min)
            if value_range <= SLIDER_RANGE_THRESHOLD:
                return WidgetType.SLIDER_WITH_INPUT
        return WidgetType.NUMBER_INPUT

    if param_type == ParameterType.FLOAT:
        p_min = parameter_data.get("MIN", 0.0)
        p_max = parameter_data.get("MAX", 0.0)
        if isinstance(p_min, (int, float)) and isinstance(p_max, (int, float)):
            value_range = abs(float(p_max) - float(p_min))
            if value_range <= 100.0:
                return WidgetType.SLIDER_WITH_INPUT
        return WidgetType.NUMBER_INPUT

    if param_type == ParameterType.ENUM:
        value_list = parameter_data.get("VALUE_LIST", [])
        if len(tuple(value_list)) <= RADIO_GROUP_THRESHOLD:
            return WidgetType.RADIO_GROUP
        return WidgetType.DROPDOWN

    if param_type == ParameterType.STRING:
        return WidgetType.TEXT_INPUT

    if param_type == ParameterType.ACTION:
        return WidgetType.BUTTON

    return WidgetType.READ_ONLY


__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
```

### 6.3 Form Schema Generator: form_schema.py

**File**: `aiohomematic_config/form_schema.py`

```python
"""
Form schema generator for Homematic device configuration.

Transforms ParameterData descriptions and current values into a
JSON-serializable form schema that any frontend can render.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from aiohomematic.const import ParameterData, ParameterType
from aiohomematic.parameter_tools import (
    get_parameter_step,
    is_parameter_visible,
    is_parameter_writable,
)

from aiohomematic_config.const import DEFAULT_LOCALE
from aiohomematic_config.grouping import ParameterGrouper
from aiohomematic_config.labels import LabelResolver
from aiohomematic_config.widgets import WidgetType, determine_widget


class FormParameter(BaseModel):
    """A single parameter in a form schema."""

    id: str
    label: str
    type: str
    widget: WidgetType
    min: float | int | None = None
    max: float | int | None = None
    step: float | None = None
    unit: str = ""
    default: Any = None
    current_value: Any = None
    writable: bool = True
    modified: bool = False
    options: list[str] | None = None


class FormSection(BaseModel):
    """A logical group of parameters in a form."""

    id: str
    title: str
    parameters: list[FormParameter]


class FormSchema(BaseModel):
    """Complete form schema for a channel's paramset configuration."""

    channel_address: str
    channel_type: str
    sections: list[FormSection]
    total_parameters: int
    writable_parameters: int


class FormSchemaGenerator:
    """
    Generate form schemas from paramset descriptions.

    Combines widget determination, parameter grouping, and label resolution
    to produce a complete, frontend-agnostic form schema.
    """

    __slots__ = ("_grouper", "_label_resolver")

    def __init__(
        self,
        *,
        locale: str = DEFAULT_LOCALE,
        label_resolver: LabelResolver | None = None,
        grouper: ParameterGrouper | None = None,
    ) -> None:
        """Initialize the form schema generator."""
        self._label_resolver = label_resolver or LabelResolver(locale=locale)
        self._grouper = grouper or ParameterGrouper()

    def generate(
        self,
        *,
        descriptions: Mapping[str, ParameterData],
        current_values: dict[str, Any],
        channel_address: str = "",
        channel_type: str = "",
    ) -> FormSchema:
        """
        Generate a complete form schema for the given paramset.

        Args:
            descriptions: Parameter descriptions (from get_paramset_description).
            current_values: Current parameter values (from get_paramset).
            channel_address: Channel address for context.
            channel_type: Channel type for grouping hints.

        Returns:
            A FormSchema ready for JSON serialization.

        """
        # Filter to visible parameters
        visible_params: dict[str, ParameterData] = {
            param_id: pd
            for param_id, pd in descriptions.items()
            if is_parameter_visible(parameter_data=pd)
        }

        # Group parameters
        groups = self._grouper.group(
            descriptions=visible_params,
            channel_type=channel_type,
        )

        # Build sections
        sections: list[FormSection] = []
        total_params = 0
        writable_params = 0

        for group in groups:
            form_params: list[FormParameter] = []
            for param_id in group.parameters:
                pd = visible_params.get(param_id)
                if pd is None:
                    continue

                writable = is_parameter_writable(parameter_data=pd)
                current = current_values.get(param_id)
                default = pd.get("DEFAULT")
                modified = current is not None and default is not None and current != default
                param_type = pd.get("TYPE", ParameterType.EMPTY)

                widget = determine_widget(parameter_data=pd)
                if not writable:
                    widget = WidgetType.READ_ONLY

                form_param = FormParameter(
                    id=param_id,
                    label=self._label_resolver.resolve(parameter_id=param_id),
                    type=str(param_type),
                    widget=widget,
                    min=pd.get("MIN"),
                    max=pd.get("MAX"),
                    step=get_parameter_step(parameter_data=pd),
                    unit=pd.get("UNIT", ""),
                    default=default,
                    current_value=current,
                    writable=writable,
                    modified=modified,
                    options=list(pd["VALUE_LIST"]) if "VALUE_LIST" in pd else None,
                )
                form_params.append(form_param)
                total_params += 1
                if writable:
                    writable_params += 1

            if form_params:
                sections.append(
                    FormSection(
                        id=group.id,
                        title=group.title,
                        parameters=form_params,
                    )
                )

        return FormSchema(
            channel_address=channel_address,
            channel_type=channel_type,
            sections=sections,
            total_parameters=total_params,
            writable_parameters=writable_params,
        )


__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
```

### 6.4 Parameter Grouper: grouping.py

**File**: `aiohomematic_config/grouping.py`

```python
"""
Parameter grouping for configuration forms.

Groups a flat list of parameters into logical sections using
prefix-based heuristics and curated category mappings.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

import inspect
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final

from aiohomematic.const import ParameterData


@dataclass(frozen=True)
class ParameterGroup:
    """A logical group of parameters."""

    id: str
    title: str
    parameters: tuple[str, ...]


# Curated group definitions: (group_id, title, regex patterns)
_GROUP_DEFINITIONS: Final[tuple[tuple[str, str, tuple[str, ...]], ...]] = (
    (
        "temperature",
        "Temperature Settings",
        (r"TEMPERATURE_.*", r".*_TEMP_.*", r"FROST_.*", r"COMFORT_.*", r"ECO_.*"),
    ),
    (
        "timing",
        "Timing & Duration",
        (r".*_TIME_.*", r".*_DURATION_.*", r".*_DELAY_.*", r".*_INTERVAL_.*", r".*_TIMEOUT_.*"),
    ),
    (
        "display",
        "Display Settings",
        (r"SHOW_.*", r"DISPLAY_.*", r"BACKLIGHT_.*", r"LED_.*"),
    ),
    (
        "transmission",
        "Transmission & Communication",
        (r"TRANSMIT_.*", r"TX_.*", r"SIGNAL_.*", r"DUTYCYCLE_.*", r"COND_TX_.*"),
    ),
    (
        "powerup",
        "Power-Up Behavior",
        (r"POWERUP_.*",),
    ),
    (
        "boost",
        "Boost Settings",
        (r"BOOST_.*",),
    ),
    (
        "button",
        "Button Behavior",
        (r"BUTTON_.*", r"LOCAL_.*"),
    ),
    (
        "threshold",
        "Thresholds & Conditions",
        (r".*_THRESHOLD_.*", r".*_DECISION_.*", r".*_FILTER.*"),
    ),
    (
        "status",
        "Status & Reporting",
        (r"STATUSINFO_.*", r"STATUS_.*"),
    ),
)


@dataclass
class _GroupCollector:
    """Mutable collector for building parameter groups."""

    id: str
    title: str
    patterns: tuple[re.Pattern[str], ...]
    parameters: list[str] = field(default_factory=list)


class ParameterGrouper:
    """
    Group parameters into logical sections.

    Applies pattern-based heuristics to organize flat parameter lists.
    """

    __slots__ = ("_collectors",)

    def __init__(self) -> None:
        """Initialize the parameter grouper."""
        self._collectors: tuple[_GroupCollector, ...] = tuple(
            _GroupCollector(
                id=gid,
                title=title,
                patterns=tuple(re.compile(p) for p in patterns),
            )
            for gid, title, patterns in _GROUP_DEFINITIONS
        )

    def group(
        self,
        *,
        descriptions: Mapping[str, ParameterData],
        channel_type: str = "",
    ) -> tuple[ParameterGroup, ...]:
        """
        Group parameters into logical sections.

        Args:
            descriptions: Parameter descriptions to group.
            channel_type: Optional channel type for context-aware grouping.

        Returns:
            Tuple of ParameterGroup instances.

        """
        # Reset collectors
        for collector in self._collectors:
            collector.parameters.clear()

        ungrouped: list[str] = []

        for param_id in sorted(descriptions.keys()):
            matched = False
            for collector in self._collectors:
                if any(pattern.fullmatch(param_id) for pattern in collector.patterns):
                    collector.parameters.append(param_id)
                    matched = True
                    break
            if not matched:
                ungrouped.append(param_id)

        groups: list[ParameterGroup] = []
        for collector in self._collectors:
            if collector.parameters:
                groups.append(
                    ParameterGroup(
                        id=collector.id,
                        title=collector.title,
                        parameters=tuple(collector.parameters),
                    )
                )

        if ungrouped:
            groups.append(
                ParameterGroup(
                    id="other",
                    title="Other Settings",
                    parameters=tuple(ungrouped),
                )
            )

        return tuple(groups)


__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
```

### 6.5 Label Resolver: labels.py

**File**: `aiohomematic_config/labels.py`

```python
"""
Human-readable label resolution for parameter IDs.

Maps technical Homematic parameter identifiers to user-friendly labels
with i18n support. Falls back to automatic formatting when no translation
is available.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

import inspect
import json
import logging
from pathlib import Path
from typing import Final

from aiohomematic_config.const import DEFAULT_LOCALE

_LOGGER: Final = logging.getLogger(__name__)

_TRANSLATIONS_DIR: Final = Path(__file__).parent / "translations"


class LabelResolver:
    """
    Resolve parameter IDs to human-readable labels.

    Loads translations from JSON files in the translations directory.
    Falls back to automatic formatting (split by underscore, title case)
    when no translation is found.
    """

    __slots__ = ("_labels", "_locale")

    def __init__(self, *, locale: str = DEFAULT_LOCALE) -> None:
        """Initialize the label resolver."""
        self._locale: Final = locale
        self._labels: Final[dict[str, str]] = self._load_translations(locale=locale)

    @staticmethod
    def _load_translations(*, locale: str) -> dict[str, str]:
        """Load translation file for the given locale."""
        translation_file = _TRANSLATIONS_DIR / f"{locale}.json"
        if not translation_file.exists():
            _LOGGER.warning("Translation file not found for locale '%s'", locale)
            return {}
        with translation_file.open(encoding="utf-8") as f:
            data: dict[str, str] = json.load(f)
        return data

    def resolve(self, *, parameter_id: str) -> str:
        """
        Resolve a parameter ID to a human-readable label.

        Returns the translated label if available, otherwise applies
        automatic formatting: split by underscores, title case each word.
        """
        if (label := self._labels.get(parameter_id)) is not None:
            return label
        return _humanize_parameter_id(parameter_id=parameter_id)

    @property
    def locale(self) -> str:
        """Return the current locale."""
        return self._locale


def _humanize_parameter_id(*, parameter_id: str) -> str:
    """
    Convert a technical parameter ID to a human-readable label.

    Example: ``TEMPERATURE_OFFSET`` -> ``Temperature Offset``
    """
    return parameter_id.replace("_", " ").title()


__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
```

### 6.6 Config Session: session.py

**File**: `aiohomematic_config/session.py`

```python
"""
Configuration editing session with change tracking.

Tracks parameter modifications during an editing session, providing
undo/redo, dirty state detection, and validation before write.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

import inspect
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Final

from aiohomematic.const import ParameterData
from aiohomematic.parameter_tools import (
    ParamsetChange,
    ValidationResult,
    diff_paramset,
    validate_paramset,
)


@dataclass(frozen=True)
class _UndoEntry:
    """A single undo/redo entry."""

    parameter: str
    old_value: Any
    new_value: Any


class ConfigSession:
    """
    Track changes during a configuration editing session.

    Provides change tracking, undo/redo, dirty state detection,
    validation, and export of changed values for put_paramset.
    """

    __slots__ = (
        "_current_values",
        "_descriptions",
        "_initial_values",
        "_redo_stack",
        "_undo_stack",
    )

    def __init__(
        self,
        *,
        descriptions: Mapping[str, ParameterData],
        initial_values: dict[str, Any],
    ) -> None:
        """Initialize the configuration session."""
        self._descriptions: Final = descriptions
        self._initial_values: Final[dict[str, Any]] = dict(initial_values)
        self._current_values: dict[str, Any] = dict(initial_values)
        self._undo_stack: list[_UndoEntry] = []
        self._redo_stack: list[_UndoEntry] = []

    def set(self, *, parameter: str, value: Any) -> None:
        """
        Set a parameter value, recording the change for undo.

        Clears the redo stack since the user has diverged from the redo path.
        """
        old_value = self._current_values.get(parameter)
        if old_value == value:
            return
        self._undo_stack.append(
            _UndoEntry(parameter=parameter, old_value=old_value, new_value=value)
        )
        self._redo_stack.clear()
        self._current_values[parameter] = value

    def undo(self) -> bool:
        """
        Undo the last change.

        Returns True if an undo was performed, False if nothing to undo.
        """
        if not self._undo_stack:
            return False
        entry = self._undo_stack.pop()
        self._redo_stack.append(entry)
        self._current_values[entry.parameter] = entry.old_value
        return True

    def redo(self) -> bool:
        """
        Redo the last undone change.

        Returns True if a redo was performed, False if nothing to redo.
        """
        if not self._redo_stack:
            return False
        entry = self._redo_stack.pop()
        self._undo_stack.append(entry)
        self._current_values[entry.parameter] = entry.new_value
        return True

    @property
    def is_dirty(self) -> bool:
        """Return True if any parameter differs from the initial value."""
        return self._current_values != self._initial_values

    @property
    def can_undo(self) -> bool:
        """Return True if undo is possible."""
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        """Return True if redo is possible."""
        return len(self._redo_stack) > 0

    def get_changes(self) -> dict[str, Any]:
        """
        Return only the parameters that differ from initial values.

        Suitable for passing directly to put_paramset.
        """
        return {
            param: value
            for param, value in self._current_values.items()
            if self._initial_values.get(param) != value
        }

    def get_changed_parameters(self) -> dict[str, ParamsetChange]:
        """Return a detailed diff between initial and current values."""
        return diff_paramset(
            descriptions=self._descriptions,
            baseline=self._initial_values,
            current=self._current_values,
        )

    def get_current_value(self, *, parameter: str) -> Any:
        """Return the current value of a parameter."""
        return self._current_values.get(parameter)

    def validate(self) -> dict[str, ValidationResult]:
        """
        Validate all current values against their descriptions.

        Returns only failures. An empty dict means all values are valid.
        """
        return validate_paramset(
            descriptions=self._descriptions,
            values=self._current_values,
        )

    def validate_changes(self) -> dict[str, ValidationResult]:
        """
        Validate only the changed values.

        Returns only failures for parameters that differ from initial values.
        """
        changes = self.get_changes()
        if not changes:
            return {}
        return validate_paramset(
            descriptions=self._descriptions,
            values=changes,
        )

    def reset_to_defaults(self) -> None:
        """Reset all values to their DEFAULT from parameter descriptions."""
        for param, pd in self._descriptions.items():
            default = pd.get("DEFAULT")
            if default is not None and param in self._current_values:
                self.set(parameter=param, value=default)

    def discard(self) -> None:
        """Discard all changes and revert to initial values."""
        self._current_values = dict(self._initial_values)
        self._undo_stack.clear()
        self._redo_stack.clear()


__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
```

### 6.7 Config Exporter: exporter.py

**File**: `aiohomematic_config/exporter.py`

```python
"""
Configuration export and import utilities.

Serializes and deserializes device configurations for backup,
transfer, or comparison purposes.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

import inspect
import json
from datetime import datetime, timezone
from typing import Any, Final

from pydantic import BaseModel


class ExportedConfiguration(BaseModel):
    """Serializable device configuration snapshot."""

    version: str = "1.0"
    exported_at: str
    device_address: str
    device_type: str
    channel_address: str
    channel_type: str
    paramset_key: str
    values: dict[str, Any]


_EXPORT_VERSION: Final = "1.0"


def export_configuration(
    *,
    device_address: str,
    device_type: str,
    channel_address: str,
    channel_type: str,
    paramset_key: str,
    values: dict[str, Any],
) -> str:
    """
    Export a configuration as a JSON string.

    Returns a JSON string containing the device configuration
    with metadata for identification and versioning.
    """
    config = ExportedConfiguration(
        version=_EXPORT_VERSION,
        exported_at=datetime.now(tz=timezone.utc).isoformat(),
        device_address=device_address,
        device_type=device_type,
        channel_address=channel_address,
        channel_type=channel_type,
        paramset_key=paramset_key,
        values=values,
    )
    return config.model_dump_json(indent=2)


def import_configuration(*, json_data: str) -> ExportedConfiguration:
    """
    Import a configuration from a JSON string.

    Returns an ExportedConfiguration instance.
    Raises ValueError if the JSON is invalid or the version is unsupported.
    """
    data = json.loads(json_data)
    if not isinstance(data, dict):
        msg = "Invalid configuration: expected a JSON object."
        raise ValueError(msg)

    version = data.get("version", "")
    if version != _EXPORT_VERSION:
        msg = f"Unsupported configuration version: {version!r} (expected {_EXPORT_VERSION!r})."
        raise ValueError(msg)

    return ExportedConfiguration.model_validate(data)


__all__ = tuple(
    sorted(
        name
        for name, obj in globals().items()
        if not name.startswith("_")
        and (name.isupper() or inspect.isfunction(obj) or inspect.isclass(obj))
        and getattr(obj, "__module__", __name__) == __name__
    )
)
```

### 6.8 Package Init: \_\_init\_\_.py

**File**: `aiohomematic_config/__init__.py`

```python
"""
aiohomematic-config: Presentation layer for Homematic device configuration.

Transforms Homematic device paramset descriptions into UI-optimized
structures. No RPC knowledge, no CCU access -- operates purely on data
structures from aiohomematic.

Key components:

- ``FormSchemaGenerator``: ParameterData + values -> JSON form schemas
- ``ParameterGrouper``: Flat parameter list -> grouped sections
- ``LabelResolver``: Technical IDs -> human-readable labels (i18n)
- ``ConfigSession``: Change tracking, undo/redo, dirty state
- ``ConfigExporter``: Serialize/deserialize configurations

Quick start::

    from aiohomematic_config import FormSchemaGenerator

    generator = FormSchemaGenerator(locale="en")
    schema = generator.generate(
        descriptions=descriptions,
        current_values=current_values,
        channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
    )
    # schema is a Pydantic model, JSON-serializable
"""

from __future__ import annotations

from aiohomematic_config.const import VERSION
from aiohomematic_config.exporter import (
    ExportedConfiguration,
    export_configuration,
    import_configuration,
)
from aiohomematic_config.form_schema import (
    FormParameter,
    FormSchema,
    FormSchemaGenerator,
    FormSection,
)
from aiohomematic_config.grouping import ParameterGroup, ParameterGrouper
from aiohomematic_config.labels import LabelResolver
from aiohomematic_config.session import ConfigSession
from aiohomematic_config.widgets import WidgetType, determine_widget

__all__ = [
    "ConfigSession",
    "ExportedConfiguration",
    "FormParameter",
    "FormSchema",
    "FormSchemaGenerator",
    "FormSection",
    "LabelResolver",
    "ParameterGroup",
    "ParameterGrouper",
    "VERSION",
    "WidgetType",
    "determine_widget",
    "export_configuration",
    "import_configuration",
]
```

**File**: `aiohomematic_config/py.typed`

Empty file (PEP 561 marker).

---

## 7. Translation Files

### aiohomematic_config/strings.json (Primary Source)

```json
{
  "TEMPERATURE_OFFSET": "Temperature Offset",
  "TEMPERATURE_WINDOW_OPEN": "Window Open Temperature",
  "TEMPERATURE_COMFORT": "Comfort Temperature",
  "TEMPERATURE_LOWERING": "Lowering Temperature",
  "TEMPERATURE_MINIMUM": "Minimum Temperature",
  "TEMPERATURE_MAXIMUM": "Maximum Temperature",
  "FROST_PROTECTION": "Frost Protection",
  "BOOST_TIME_PERIOD": "Boost Duration",
  "BOOST_POSITION": "Boost Position",
  "SHOW_WEEKDAY": "Display Weekday",
  "DISPLAY_INFORMATION": "Display Information",
  "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": "Button Response Without Backlight",
  "LOCAL_RESET_DISABLED": "Local Reset Disabled",
  "TRANSMIT_TRY_MAX": "Max Transmission Retries",
  "POWERUP_ONTIME": "Power-Up On Time",
  "POWERUP_OFFTIME": "Power-Up Off Time",
  "STATUSINFO_MINDELAY": "Status Info Min Delay",
  "COND_TX_THRESHOLD_HI": "Condition TX Threshold High",
  "COND_TX_THRESHOLD_LO": "Condition TX Threshold Low",
  "COND_TX_DECISION_ABOVE": "Condition TX Decision Above",
  "COND_TX_DECISION_BELOW": "Condition TX Decision Below",
  "BRIGHTNESS_FILTER": "Brightness Filter",
  "LED_DISABLE_CHANNELSTATE": "Disable Channel State LED",
  "LED_SLEEP_MODE": "LED Sleep Mode"
}
```

### aiohomematic_config/translations/en.json

Synced from `strings.json` by `check_i18n_catalogs.py`.

### aiohomematic_config/translations/de.json

```json
{
  "TEMPERATURE_OFFSET": "Temperatur-Offset",
  "TEMPERATURE_WINDOW_OPEN": "Fenster-Offen-Temperatur",
  "TEMPERATURE_COMFORT": "Komforttemperatur",
  "TEMPERATURE_LOWERING": "Absenktemperatur",
  "TEMPERATURE_MINIMUM": "Mindesttemperatur",
  "TEMPERATURE_MAXIMUM": "Maximaltemperatur",
  "FROST_PROTECTION": "Frostschutz",
  "BOOST_TIME_PERIOD": "Boost-Dauer",
  "BOOST_POSITION": "Boost-Position",
  "SHOW_WEEKDAY": "Wochentag anzeigen",
  "DISPLAY_INFORMATION": "Anzeigeinformation",
  "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": "Tastendruck ohne Hintergrundbeleuchtung",
  "LOCAL_RESET_DISABLED": "Lokaler Reset deaktiviert",
  "TRANSMIT_TRY_MAX": "Maximale Sendeversuche",
  "POWERUP_ONTIME": "Einschaltzeit nach Spannungswiederkehr",
  "POWERUP_OFFTIME": "Ausschaltzeit nach Spannungswiederkehr",
  "STATUSINFO_MINDELAY": "Statusinfo Mindestverzögerung",
  "COND_TX_THRESHOLD_HI": "Sendebedingung Oberer Schwellwert",
  "COND_TX_THRESHOLD_LO": "Sendebedingung Unterer Schwellwert",
  "COND_TX_DECISION_ABOVE": "Sendebedingung Überschreitung",
  "COND_TX_DECISION_BELOW": "Sendebedingung Unterschreitung",
  "BRIGHTNESS_FILTER": "Helligkeitsfilter",
  "LED_DISABLE_CHANNELSTATE": "Kanalstatus-LED deaktivieren",
  "LED_SLEEP_MODE": "LED-Schlafmodus"
}
```

---

## 8. Test Infrastructure

### 8.1 conftest.py

**File**: `tests/conftest.py`

```python
"""Shared test fixtures for aiohomematic-config."""

from __future__ import annotations

from typing import Any

import pytest

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType


@pytest.fixture
def thermostat_descriptions() -> dict[str, ParameterData]:
    """Return MASTER paramset descriptions for a thermostat (HmIP-eTRV-2)."""
    return {
        "TEMPERATURE_OFFSET": _make_float_param(
            min_val=-3.5, max_val=3.5, default=0.0, unit="°C"
        ),
        "BOOST_TIME_PERIOD": _make_integer_param(
            min_val=0, max_val=30, default=5, unit="min"
        ),
        "SHOW_WEEKDAY": _make_enum_param(
            values=["SATURDAY", "SUNDAY", "MONDAY", "TUESDAY",
                    "WEDNESDAY", "THURSDAY", "FRIDAY"],
            default="SATURDAY",
        ),
        "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": _make_bool_param(default=False),
        "LOCAL_RESET_DISABLED": _make_bool_param(default=False),
        "TEMPERATURE_WINDOW_OPEN": _make_float_param(
            min_val=4.5, max_val=30.0, default=12.0, unit="°C"
        ),
    }


@pytest.fixture
def thermostat_values() -> dict[str, Any]:
    """Return current values for a thermostat."""
    return {
        "TEMPERATURE_OFFSET": 1.5,
        "BOOST_TIME_PERIOD": 5,
        "SHOW_WEEKDAY": "SATURDAY",
        "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": False,
        "LOCAL_RESET_DISABLED": False,
        "TEMPERATURE_WINDOW_OPEN": 12.0,
    }


@pytest.fixture
def switch_descriptions() -> dict[str, ParameterData]:
    """Return MASTER paramset descriptions for a switch (HmIP-PS)."""
    return {
        "POWERUP_ONTIME": _make_float_param(
            min_val=0.0, max_val=327680.0, default=0.0, unit="s"
        ),
        "POWERUP_OFFTIME": _make_float_param(
            min_val=0.0, max_val=327680.0, default=0.0, unit="s"
        ),
        "STATUSINFO_MINDELAY": _make_float_param(
            min_val=2.0, max_val=10.0, default=2.0, unit="s"
        ),
    }


@pytest.fixture
def switch_values() -> dict[str, Any]:
    """Return current values for a switch."""
    return {
        "POWERUP_ONTIME": 0.0,
        "POWERUP_OFFTIME": 0.0,
        "STATUSINFO_MINDELAY": 2.0,
    }


def _make_float_param(
    *,
    min_val: float,
    max_val: float,
    default: float,
    unit: str = "",
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create a FLOAT ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.FLOAT,
        MIN=min_val,
        MAX=max_val,
        DEFAULT=default,
        UNIT=unit,
        OPERATIONS=ops,
        FLAGS=flags,
    )


def _make_integer_param(
    *,
    min_val: int,
    max_val: int,
    default: int,
    unit: str = "",
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create an INTEGER ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.INTEGER,
        MIN=min_val,
        MAX=max_val,
        DEFAULT=default,
        UNIT=unit,
        OPERATIONS=ops,
        FLAGS=flags,
    )


def _make_bool_param(
    *,
    default: bool,
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create a BOOL ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.BOOL,
        MIN=False,
        MAX=True,
        DEFAULT=default,
        OPERATIONS=ops,
        FLAGS=flags,
    )


def _make_enum_param(
    *,
    values: list[str],
    default: str,
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create an ENUM ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.ENUM,
        MIN=values[0],
        MAX=values[-1],
        DEFAULT=default,
        VALUE_LIST=values,
        OPERATIONS=ops,
        FLAGS=flags,
    )
```

### 8.2 Test Modules

**Required test files** (minimum):

| File                        | Tests                                                                                  |
| --------------------------- | -------------------------------------------------------------------------------------- |
| `tests/test_widgets.py`     | All WidgetType mappings, edge cases (empty range, zero options)                        |
| `tests/test_form_schema.py` | Full schema generation, section ordering, writable/read-only split, modified detection |
| `tests/test_grouping.py`    | Pattern matching, ungrouped fallback, empty input, all group categories                |
| `tests/test_labels.py`      | Known translations, fallback humanization, missing locale, German locale               |
| `tests/test_session.py`     | Set/get, undo/redo, is_dirty, discard, reset_to_defaults, validate, get_changes        |
| `tests/test_exporter.py`    | Export round-trip, import validation, version check, malformed JSON                    |

**Bandit config** -- `tests/bandit.yaml`:

```yaml
skips:
  - B101 # assert used (normal in tests)
  - B104 # hardcoded bind address (test fixtures)
  - B105 # hardcoded password (test fixtures)
  - B106 # hardcoded password (test fixtures)
  - B110 # try-except-pass
  - B311 # random (not crypto)
```

---

## 9. Documentation

### README.md

Standard project README with:

- Project description
- Installation instructions (`pip install aiohomematic-config`)
- Quick start example
- Link to full documentation
- Badge for CI, coverage, PyPI version

### changelog.md

```markdown
# Version 2026.2.1 (2026-02-11)

- Initial release
- FormSchemaGenerator: Generate UI form schemas from paramset descriptions
- ParameterGrouper: Group parameters into logical sections
- LabelResolver: Translate parameter IDs to human-readable labels (en/de)
- ConfigSession: Change tracking with undo/redo and validation
- ConfigExporter: Export/import device configurations as JSON
- WidgetType mapping: Type-aware widget selection
```

### CLAUDE.md

Create a CLAUDE.md for the new project following the same structure as aiohomematic's CLAUDE.md but scoped to aiohomematic-config. Key sections:

- Project overview (presentation layer, no RPC)
- Codebase structure
- Development setup
- Code quality standards (same as aiohomematic)
- Testing guidelines
- Architecture (dependency on aiohomematic protocols only)
- Key conventions
- Git workflow
- Changelog versioning rules

---

## 10. Quality Gates

Before any release, all of these must pass:

```bash
# 1. Run all tests
pytest tests/

# 2. Run all pre-commit hooks
prek run --all-files

# 3. Type check
mypy

# 4. Verify no TODO/FIXME related to migration
grep -r "TODO\|FIXME" aiohomematic_config/

# 5. Check for unused imports
ruff check --select F401,F841

# 6. Verify version sync
echo "Changelog: $(head -1 changelog.md)"
echo "const.py: VERSION = $(grep '^VERSION' aiohomematic_config/const.py)"

# 7. Verify translations
python script/check_i18n.py aiohomematic_config/
python script/check_i18n_catalogs.py
```

---

## 11. Implementation Phases

### Phase 1: Project Scaffold (Week 1)

| Step | Deliverable                                      | Verification                                                                |
| ---- | ------------------------------------------------ | --------------------------------------------------------------------------- |
| 1.1  | Create repository structure (all dirs and files) | `ls -R` matches Section 2.1                                                 |
| 1.2  | Write `pyproject.toml` (complete)                | `pip install -e .` succeeds                                                 |
| 1.3  | Write `const.py` with VERSION                    | `python -c "from aiohomematic_config.const import VERSION; print(VERSION)"` |
| 1.4  | Write `py.typed` marker                          | File exists                                                                 |
| 1.5  | Copy and adapt development scripts               | `script/run-in-env.sh` works                                                |
| 1.6  | Write `.pre-commit-config.yaml`                  | `prek run --all-files` runs (may have errors)                               |
| 1.7  | Write `.yamllint`, `codecov.yml`, `.gitignore`   | Files exist                                                                 |
| 1.8  | Write GitHub workflows                           | CI triggers on push                                                         |
| 1.9  | Write `MANIFEST.in`, `requirements*.txt`         | `python -m build` succeeds                                                  |
| 1.10 | Write `README.md`, `changelog.md`, `LICENSE`     | Files exist                                                                 |

### Phase 2: Core Implementation (Weeks 2-3)

| Step | Deliverable                                                    | Verification                 |
| ---- | -------------------------------------------------------------- | ---------------------------- |
| 2.1  | Implement `widgets.py` (WidgetType + determine_widget)         | `test_widgets.py` passes     |
| 2.2  | Implement `labels.py` (LabelResolver)                          | `test_labels.py` passes      |
| 2.3  | Write translation files (`strings.json`, `en.json`, `de.json`) | Translations load correctly  |
| 2.4  | Implement `grouping.py` (ParameterGrouper)                     | `test_grouping.py` passes    |
| 2.5  | Implement `form_schema.py` (FormSchemaGenerator)               | `test_form_schema.py` passes |
| 2.6  | Implement `session.py` (ConfigSession)                         | `test_session.py` passes     |
| 2.7  | Implement `exporter.py` (ConfigExporter)                       | `test_exporter.py` passes    |
| 2.8  | Write `__init__.py` with public API                            | Import verification          |

### Phase 3: Quality Assurance (Week 4)

| Step | Deliverable                  | Verification                       |
| ---- | ---------------------------- | ---------------------------------- |
| 3.1  | All tests pass               | `pytest tests/` green              |
| 3.2  | All linters pass             | `prek run --all-files` green       |
| 3.3  | Coverage >= 85%              | `pytest --cov=aiohomematic_config` |
| 3.4  | mypy strict passes           | `mypy` green                       |
| 3.5  | Write CLAUDE.md              | File exists and is comprehensive   |
| 3.6  | Write `docs/architecture.md` | File exists                        |
| 3.7  | Finalize `changelog.md`      | Version matches const.py           |
| 3.8  | Tag first release            | `git tag 2026.2.1`                 |

---

## 12. Dependency Map

```
Phase 1: Scaffold
  ├── 1.1 Directory structure
  ├── 1.2 pyproject.toml
  ├── 1.3 const.py ────────────────────────┐
  ├── 1.4 py.typed                         │
  ├── 1.5 Scripts                          │
  ├── 1.6 Pre-commit config                │
  ├── 1.7 Config files                     │
  ├── 1.8 GitHub workflows                 │
  ├── 1.9 Build files                      │
  └── 1.10 Documentation stubs             │
                                           │
Phase 2: Core (depends on Phase 1)         │
  ├── 2.1 widgets.py ─────────────────┐    │
  ├── 2.2 labels.py ──────────────┐   │    │
  ├── 2.3 translations ───────────┤   │    │
  ├── 2.4 grouping.py ────────┐   │   │    │
  │                            │   │   │    │
  ├── 2.5 form_schema.py ─────┤───┤───┤────┘
  │   (depends on: 2.1, 2.2, 2.4, 1.3)
  │                            │
  ├── 2.6 session.py ─────────┘
  │   (depends on: aiohomematic.parameter_tools)
  │
  ├── 2.7 exporter.py
  │   (standalone)
  │
  └── 2.8 __init__.py
      (depends on: all of 2.1-2.7)

Phase 3: Quality (depends on Phase 2)
  ├── 3.1 All tests
  ├── 3.2 All linters
  ├── 3.3 Coverage
  ├── 3.4 mypy
  ├── 3.5 CLAUDE.md
  ├── 3.6 Architecture docs
  ├── 3.7 Changelog
  └── 3.8 First release
```

---

## Appendix A: Files Copied from aiohomematic

These files are copied from `aiohomematic/` and adapted for `aiohomematic-config`:

| Source File                      | Target File                      | Adaptation              |
| -------------------------------- | -------------------------------- | ----------------------- |
| `script/run-in-env.sh`           | `script/run-in-env.sh`           | None (project-agnostic) |
| `script/sort_class_members.py`   | `script/sort_class_members.py`   | Update file patterns    |
| `script/check_i18n.py`           | `script/check_i18n.py`           | Update package path     |
| `script/check_i18n_catalogs.py`  | `script/check_i18n_catalogs.py`  | Update file paths       |
| `script/lint_kwonly.py`          | `script/lint_kwonly.py`          | None (takes args)       |
| `script/lint_package_imports.py` | `script/lint_package_imports.py` | Update conventions      |
| `script/lint_all_exports.py`     | `script/lint_all_exports.py`     | Update package path     |

## Appendix B: Key Differences from aiohomematic

| Aspect                   | aiohomematic                      | aiohomematic-config                          |
| ------------------------ | --------------------------------- | -------------------------------------------- |
| **Purpose**              | Protocol adapter + device model   | Presentation layer                           |
| **RPC/I/O**              | Yes (XML-RPC, JSON-RPC, aiohttp)  | No I/O at all                                |
| **Dependencies**         | aiohttp, pydantic, python-slugify | aiohomematic, pydantic                       |
| **Size**                 | ~26.8K LOC, 67 files              | ~1.5K LOC, 8 files (estimated)               |
| **Test strategy**        | Session recordings, mock servers  | Pure unit tests with mock ParameterData      |
| **Test support package** | Yes (aiohomematic_test_support)   | No (not needed)                              |
| **Async**                | Heavy (all RPC operations)        | Minimal (only if delegating to aiohomematic) |
| **Release cycle**        | Tied to Home Assistant            | Independent, faster iteration                |
| **CI Python versions**   | 3.13, 3.14, 3.14t                 | 3.13, 3.14                                   |
