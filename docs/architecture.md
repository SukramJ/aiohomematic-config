# Architecture Overview

## Design Principles

1. **No RPC knowledge**: This library never communicates with a CCU or backend.
2. **Protocol-only imports from aiohomematic**: Only types, enums, TypedDicts, and utility functions -- never concrete classes like `CentralUnit` or `InterfaceClient`.
3. **Fully testable without CCU**: All tests use mock `ParameterData` dictionaries.
4. **Same quality standards as aiohomematic**: mypy strict, ruff, pylint, 85%+ coverage.

## Component Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                      aiohomematic-config                         │
│                                                                  │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────┐            │
│  │ FormSchema   │  │ Parameter     │  │ Label      │            │
│  │ Generator    │──│ Grouper       │  │ Resolver   │            │
│  │              │  └───────────────┘  └────────────┘            │
│  │              │─────────────────────────────┘                  │
│  └──────────────┘                                                │
│         │                                                        │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐  │
│  │ Widget       │  │ Config        │  │ Link Param           │  │
│  │ Mapping      │  │ Session       │  │ Metadata             │  │
│  └──────────────┘  └───────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐  │
│  │ Config       │  │ Config        │  │ Profile Store        │  │
│  │ Exporter     │  │ Change Log    │  │ + Profile Data       │  │
│  └──────────────┘  └───────────────┘  └──────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
         │
         │ imports types/enums/TypedDicts + utility functions
         ▼
┌──────────────────────────────────────────────────────────────────┐
│                        aiohomematic                              │
│                                                                  │
│  ParameterData, ParameterType, Operations, Flag, SCHEDULE_PATTERN│
│  validate_value, validate_paramset, diff_paramset                │
│  coerce_value, get_parameter_step, is_parameter_visible, ...     │
│  get_parameter_translation, get_parameter_value_translation      │
│  get_channel_type_translation, get_device_model_description      │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
ParameterData (from aiohomematic)
        │
        ▼
┌───────────────────┐
│ FormSchemaGenerator│
│                    │
│  1. Filter params  │  (visible, not internal, not schedule,
│                    │   optionally CCU-translated only)
│  2. Group params   │──── ParameterGrouper
│  3. Resolve labels │──── LabelResolver (via CCU translations)
│  4. Map widgets    │──── determine_widget()
│  5. Enrich link    │──── classify_link_parameter() (optional)
│     metadata       │
│  6. Build schema   │
└───────────────────┘
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
        ├──────────────────────────────┐
        ▼                              ▼
┌──────────────────┐     ┌──────────────────┐
│  ConfigSession    │     │  ProfileStore     │
│                    │     │                    │
│  - Track changes   │     │  - Match active   │
│  - Undo/redo       │     │    profile        │
│  - Validate        │     │  - Get profiles   │
│  - Export changes   │     │  - Resolve for    │
│                    │     │    locale          │
└──────────────────┘     └──────────────────┘
        │
        ▼
    put_paramset(changes)  ← handled by aiohomematic
        │
        ▼
┌──────────────────┐
│ ConfigChangeLog   │
│                    │
│  - Record change   │
│  - Query history   │
│  - Persist/load    │
└──────────────────┘
```

## Module Dependencies

```
const.py               ← no internal deps
widgets.py             ← const.py
labels.py              ← const.py (uses aiohomematic.ccu_translations)
grouping.py            ← const.py
link_param_metadata.py ← (standalone)
form_schema.py         ← widgets.py, labels.py, grouping.py, link_param_metadata.py, const.py
session.py             ← (standalone, uses aiohomematic.parameter_tools)
exporter.py            ← (standalone)
change_log.py          ← (standalone)
profile_data.py        ← (standalone)
profile_store.py       ← profile_data.py, const.py
__init__.py            ← all modules
```
