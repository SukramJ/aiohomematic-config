# Architecture Overview

## Design Principles

1. **No RPC knowledge**: This library never communicates with a CCU or backend.
2. **Protocol-only imports from aiohomematic**: Only types, enums, and TypedDicts -- never concrete classes like `CentralUnit` or `InterfaceClient`.
3. **Fully testable without CCU**: All tests use mock `ParameterData` dictionaries.
4. **Same quality standards as aiohomematic**: mypy strict, ruff, pylint, 85%+ coverage.

## Component Diagram

```
┌─────────────────────────────────────────────────────┐
│                 aiohomematic-config                  │
│                                                     │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────┐ │
│  │ FormSchema   │  │ Parameter     │  │ Label    │ │
│  │ Generator    │──│ Grouper       │  │ Resolver │ │
│  │              │  └───────────────┘  └──────────┘ │
│  │              │──────────────────────────┘        │
│  └──────────────┘                                   │
│         │                                           │
│  ┌──────────────┐  ┌───────────────┐                │
│  │ Widget       │  │ Config        │                │
│  │ Mapping      │  │ Session       │                │
│  └──────────────┘  └───────────────┘                │
│                                                     │
│  ┌──────────────┐                                   │
│  │ Config       │                                   │
│  │ Exporter     │                                   │
│  └──────────────┘                                   │
└─────────────────────────────────────────────────────┘
         │
         │ imports only types/enums/TypedDicts
         ▼
┌─────────────────────────────────────────────────────┐
│                   aiohomematic                       │
│                                                     │
│  ParameterData, ParameterType, Operations, Flag     │
│  validate_value, validate_paramset, diff_paramset   │
│  coerce_value, get_parameter_step, ...              │
└─────────────────────────────────────────────────────┘
```

## Data Flow

```
ParameterData (from aiohomematic)
        │
        ▼
┌──────────────────┐
│ FormSchemaGenerator│
│                    │
│  1. Filter visible │
│  2. Group params   │──── ParameterGrouper
│  3. Resolve labels │──── LabelResolver
│  4. Map widgets    │──── determine_widget()
│  5. Build schema   │
└──────────────────┘
        │
        ▼
    FormSchema (Pydantic model, JSON-serializable)
        │
        ▼
    Frontend renders form
        │
        ▼
    User edits values
        │
        ▼
┌──────────────────┐
│  ConfigSession    │
│                    │
│  - Track changes   │
│  - Undo/redo       │
│  - Validate        │
│  - Export changes   │
└──────────────────┘
        │
        ▼
    put_paramset(changes)  ← handled by aiohomematic
```

## Module Dependencies

```
const.py          ← no internal deps
widgets.py        ← const.py
labels.py         ← const.py
grouping.py       ← (standalone)
form_schema.py    ← widgets.py, labels.py, grouping.py, const.py
session.py        ← (standalone, uses aiohomematic.parameter_tools)
exporter.py       ← (standalone)
__init__.py       ← all modules
```
