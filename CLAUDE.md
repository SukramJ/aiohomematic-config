# CLAUDE.md - AI Assistant Guide for aiohomematic-config

This document provides comprehensive guidance for AI assistants working on the aiohomematic-config codebase.

## Project Overview

**aiohomematic-config** is a presentation-layer Python library that transforms Homematic device paramset descriptions into UI-optimized structures. It operates purely on data structures from `aiohomematic` -- no RPC calls, no protocol knowledge, no CCU access.

### Key Design Principles

- **No RPC knowledge**: This library never talks to a CCU or backend.
- **Protocol-only imports from aiohomematic**: Only types, enums, and TypedDicts. Never concrete classes like `CentralUnit`, `InterfaceClient`, etc.
- **Fully testable without CCU**: All tests use mock `ParameterData` dictionaries.
- **Same quality standards as aiohomematic**: mypy strict, ruff, pylint, 85%+ coverage.

## Workflow Rules

1. **Plan before coding**: Before writing any code, describe your approach and wait for approval.
2. **Clarify ambiguity**: If requirements are ambiguous, ask clarifying questions before writing any code.
3. **Suggest edge-case tests**: After finishing any code change, list edge cases and suggest test cases to cover them.
4. **Bug fix = test first**: When fixing a bug, start by writing a test that reproduces it, then fix the code until the test passes.
5. **Learn from corrections**: Every time you are corrected, reflect on the mistake and update your memory to prevent repeating it.

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

## Which model does which work

Set by the owner for the go-fabric family on 2026-10-10 (go-fabric's
`CLAUDE.md`); the review split of 2026-11-08 (go-fabric #456) likewise.
Adopted here on 2026-11-08. A statement about aiohomematic's paramset data or the CCU's parameter semantics that
lands in this repo is cited later as fact — a comment that names a caller
or a consumer, a docstring that states what the other side does, a
`changelog.md` line — so the work that produces such statements gets
the strongest model, and the work a guard checks may use a cheaper one. The
agents in [Sub-Agent Delegation](#sub-agent-delegation) carry a default
model each; the rows below decide when a call overrides it (`model:` on the
Agent tool). Implementation defaults to Opus.

| Work                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Model                                                           |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Analysis, planning, reviews of design, audits; anything written into the README or `changelog.md`, or a comment that names an aiohomematic type, a CCU parameter semantic or a UI grouping rule; the import boundary to aiohomematic (protocol-only imports, checked by `script/lint_package_imports.py`); _which_ guard gets built and its bite line; rebases and merge conflicts where `main` may have overtaken the change                                                                                                                                                                                                                                                                                          | **Fable** (the default for this repo; also the `hunt` agent)    |
| Implementation of a finished plan with guards behind it: a form-schema rule once the pattern exists, a grouping table case, a translation key, a `changelog.md` entry for a finished diff                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | **Opus** (the `impl` default; also what fast mode runs on)      |
| **Review of a slice's pull request, split (owner decision 2026-11-08, go-fabric #456).** The code review — correctness, concurrency, error paths, tests, the fixed report shape — is **Opus**. On top of it **Fable** reads, bounded: every new comment or docstring that names an aiohomematic type, a CCU parameter semantic or a UI grouping rule against aiohomematic at the pinned version (`pyproject.toml`, `requirements.txt`), every line that enters the README or `changelog.md`, the paths of the first row, and the brief's decisions against the reference — the behavioural gaps a code review does not see. The load-bearing claims of the Opus review are verified before they reach the implementer. | **Opus**, then **Fable**                                        |
| Work a test or generator checks immediately: `ruff format`, `prek run --all-files`, `script/check_i18n.py`, a table case on an existing pattern; search and first reading of a tree whose result a stronger model or the owner reads again                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | **Sonnet** (the `guard` default; `impl` with `model: "sonnet"`) |
| Mechanical inventories whose answer is a list the caller can re-grep: which files reference X, which links are dead, which entries lack a counterpart                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | **Haiku** (`sweep` default)                                     |

Sonnet never writes a claim about an aiohomematic type, a CCU parameter semantic or a UI grouping rule into the repo, and
never touches the paths named in the first row. Haiku returns lists, never
verdicts. When in doubt about which row a task is in, it is in the first.

---

## Sub-Agent Delegation

As go-fabric's and openccu-loom's rule (owner, 2026-10-10). The main
conversation owns planning, contract and wire decisions, guard
specifications, sub-agent steering, and final verification. It does not own
typing.

**Delegate what a gate can prove; keep what only a reader can accept.**
Delegate freely: table cases, fakes, scaffolding, fixture updates, doc and
link cleanups, version bumps across the changelog set, inventories and grep
sweeps. Never delegate: the aiohomematic import boundary, the public API consumed by the integration and the frontend, and _which_ guard gets
built. Locating is delegable; reading is not.

| Agent   | Default model | Use for                                                     |
| ------- | ------------- | ----------------------------------------------------------- |
| `impl`  | Opus          | scoped implementation with a stated acceptance command      |
| `guard` | Sonnet        | tests from a caller-written guard spec, plus the bite proof |
| `sweep` | Haiku         | read-only inventories and grep sweeps, high fan-out         |
| `hunt`  | Fable         | adversarial read-only defect hunt, ranked candidates        |

Each default is one row of
[Which model does which work](#which-model-does-which-work); a call that
falls into another row passes `model:` on the Agent tool — `impl` with
`model: "sonnet"` for work a generator or formatter checks immediately.

**Size CPU-bound fan-out from the host, never from a constant** — the owner
works from a 4-core box and a 14-core box:

```sh
cores=$(nproc); agents=$(( (cores - 1) / share ))   # share = cores per agent
```

Check the 1-minute load first; if it is at or above the core count, run one
CPU-bound agent and queue the rest. Eight concurrent agents is a practical
ceiling whatever the core count. Every CPU-bound agent must **pin** its share
in the command it runs (`pytest -n <share> tests/<area>`) — handing out a number without
pinning it changes nothing. Read-only agents cost no core worth counting;
6–8 is a practical ceiling there.

Two hard rules: **no sub-agent runs the full gate (`pytest tests/`, `prek run --all-files`, `mypy`) or a
repo-wide lint** — the full gate runs once, in the main conversation, at the
end of the slice — and **no two writing agents in the same package**
(disjoint file sets, or `isolation: "worktree"`).

Every brief carries five things: the files and public surface plus one style
reference; the acceptance command the agent runs itself; the invariants it
touches; **stop conditions** (new dependency, API or wire change, credential
handling, an ADR-shaped decision — a stop is a successful outcome); and a
report format ≤ 250 words, large artefacts to the scratchpad as a path.

**A report is a claim.** Read the diff, run the gate yourself. For `guard`,
the acceptance artefact is not a green test but the **bite proof**: the named
production line removed, the test observed red with its message, the line
restored, green again.

---

## Token use

Set by the owner on 2026-10-14 (efficient use of the tokens matters to the
owner), as go-fabric's rule of the same date. A slice costs on
the order of half a million to a million tokens per implementing agent
before the owner's review; the rules below are what keeps that from
doubling.

- **Read slices, not files.** `sed -n a,bp`, `grep -n` with a tight
  pattern and `head`; a whole file only when the task is the file. Never
  re-read what is already in context; cite the earlier read.
- **Delegate first reads.** A source tree's inventory (aiohomematic, this repo)
  is a `sweep` or Sonnet read written to the scratchpad with `file:line`
  for every fact; the owner spot-checks the load-bearing lines and verifies
  every fact about aiohomematic's paramset data or the CCU's parameter semantics before it enters a brief or
  the README or `changelog.md` — the agent's result is a map, never a citation.
- **Logs by their summary.** The gate (`pytest tests/`, `prek run --all-files`, `mypy`) runs in the
  background with a summary file (one line per gate, `FAIL`/`ok` lines
  only); read the summary, and open a log only on failure, with `grep` for
  the failure markers and the error strings — never `cat`. The same for CI:
  the job log is fetched once to a file and grepped.
- **One turn, every independent call.** Reads, checks and background
  starts that do not depend on each other go out together; a wait is a
  `Monitor` or an `until` loop in the background, not polling by hand.
- **Short artefacts.** A brief names files, decisions and the acceptance
  command, not prose; a report follows the fixed shape of
  [Sub-Agent Delegation](#sub-agent-delegation) (≤ 250 words, large
  artefacts as a scratchpad path); status messages to the owner are short,
  outcome first, in German.
- **Skip what cannot have changed.** No regeneration for a comment change;
  no second gate run for a notes-only commit — say what was skipped and
  why.
- **Edit by script.** Several replacements in several files are one
  scripted call with asserted anchors, not a chain of interactive edits;
  a generated or formatted artefact is regenerated, never patched.
- **Agents read what the brief names.** An implementing agent gets the
  file list and the pinned sources in the brief, reads those, and reports
  in the fixed shape; it does not survey the tree. One agent per brief;
  two agents only on disjoint paths, at most one Opus agent at a time.
- **Push, pull request and tag are the session's own calls.** An
  implementing agent works locally — branch, commits, guards — and
  reports; the owner's session reads the diff, runs the gate, pushes,
  opens the pull request and tags the merge commit; the owner merges. A
  delegated push, pull request or tag is refused by the auto-mode
  classifier ("Create Public Surface", 2026-11-07), and the review in
  [Which model does which work](#which-model-does-which-work) sits
  between the agent's report and the push anyway.

---

## Git Workflow

- Main development branch: `main`
- No direct commits to `main`
- Feature branches for all changes
- Pre-commit hooks enforced via `prek`

## Changelog Versioning

- Format: `YYYY.M.P` (e.g., `2026.2.1`)
- Version defined in `aiohomematic_config/const.py`
- Changelog in `changelog.md`
- Both must be updated together for releases
