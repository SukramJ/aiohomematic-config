# API Reference

## FormSchemaGenerator

Main entry point for generating UI form schemas.

```python
from aiohomematic_config import FormSchemaGenerator

generator = FormSchemaGenerator(locale="en")
schema = generator.generate(
    descriptions=descriptions,      # dict[str, ParameterData]
    current_values=current_values,  # dict[str, Any]
    channel_address="ADDR:1",
    channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
    model="HmIP-eTRV-2",
)
```

### generate() Parameters

| Parameter             | Type                            | Default | Description                                                         |
| --------------------- | ------------------------------- | ------- | ------------------------------------------------------------------- |
| `descriptions`        | `Mapping[str, ParameterData]`   | —       | Parameter descriptions (from get_paramset_description)              |
| `current_values`      | `dict[str, Any]`                | —       | Current parameter values (from get_paramset)                        |
| `channel_address`     | `str`                           | `""`    | Channel address for context                                         |
| `channel_type`        | `str`                           | `""`    | Channel type for grouping hints and label lookup                    |
| `model`               | `str`                           | `""`    | Device model ID for description lookup                              |
| `sub_model`           | `str \| None`                   | `None`  | Optional sub-model for description fallback                         |
| `require_translation` | `bool`                          | `True`  | Only include parameters with CCU translations (False for LINK sets) |
| `enrich_link_metadata`| `bool`                          | `False` | Attach link metadata (keypress group, category, time presets, etc.) |

### FormSchema

| Field                 | Type                | Description                            |
| --------------------- | ------------------- | -------------------------------------- |
| `channel_address`     | `str`               | Channel address                        |
| `channel_type`        | `str`               | Channel type                           |
| `model_description`   | `str`               | Human-readable device model name       |
| `channel_type_label`  | `str`               | Translated channel type label          |
| `sections`            | `list[FormSection]` | Grouped parameter sections             |
| `total_parameters`    | `int`               | Total visible parameters               |
| `writable_parameters` | `int`               | Writable parameters count              |

### FormSection

| Field        | Type                  | Description                |
| ------------ | --------------------- | -------------------------- |
| `id`         | `str`                 | Group identifier           |
| `title`      | `str`                 | Human-readable group title |
| `parameters` | `list[FormParameter]` | Parameters in this group   |

### FormParameter

| Field                | Type                              | Description                                    |
| -------------------- | --------------------------------- | ---------------------------------------------- |
| `id`                 | `str`                             | Parameter ID                                   |
| `label`              | `str`                             | Human-readable label                           |
| `type`               | `str`                             | Parameter type                                 |
| `widget`             | `WidgetType`                      | Recommended UI widget                          |
| `min`                | `float \| int \| None`            | Minimum value (numeric types only)             |
| `max`                | `float \| int \| None`            | Maximum value (numeric types only)             |
| `step`               | `float \| None`                   | Step increment (numeric types only)            |
| `unit`               | `str`                             | Unit string                                    |
| `default`            | `Any`                             | Default value                                  |
| `current_value`      | `Any`                             | Current value                                  |
| `writable`           | `bool`                            | Whether parameter is writable                  |
| `modified`           | `bool`                            | Whether value differs from default             |
| `options`            | `list[str] \| None`              | Enum option values                             |
| `option_labels`      | `dict[str, str] \| None`         | Translated labels for enum option values       |
| `keypress_group`     | `str \| None`                    | Link: SHORT / LONG / COMMON                   |
| `category`           | `str \| None`                    | Link: time / level / jump_target / etc.        |
| `display_as_percent` | `bool`                            | Link: show value as percentage                 |
| `has_last_value`     | `bool`                            | Link: supports "last value" option             |
| `hidden_by_default`  | `bool`                            | Link: hide in default view (jump targets etc.) |
| `time_pair_id`       | `str \| None`                    | Link: groups BASE/FACTOR pairs                 |
| `time_selector_type` | `str \| None`                    | Link: timeOnOff / delay / rampOnOff            |
| `time_presets`       | `list[dict[str, int \| str]] \| None` | Link: preset options for time selector    |

## WidgetType

```python
from aiohomematic_config import WidgetType

class WidgetType(StrEnum):
    TOGGLE = "toggle"
    SLIDER_WITH_INPUT = "slider_with_input"
    NUMBER_INPUT = "number_input"
    RADIO_GROUP = "radio_group"
    DROPDOWN = "dropdown"
    TEXT_INPUT = "text_input"
    BUTTON = "button"
    READ_ONLY = "read_only"
```

## ConfigSession

```python
from aiohomematic_config import ConfigSession

session = ConfigSession(
    descriptions=descriptions,
    initial_values=current_values,
)

session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
session.undo()
session.redo()

if session.is_dirty:
    errors = session.validate_changes()
    if not errors:
        changes = session.get_changes()
        # pass changes to put_paramset
```

### Methods

| Method                     | Returns                       | Description                            |
| -------------------------- | ----------------------------- | -------------------------------------- |
| `set(parameter, value)`    | `None`                        | Set value, record for undo             |
| `undo()`                   | `bool`                        | Undo last change                       |
| `redo()`                   | `bool`                        | Redo last undone change                |
| `get_changes()`            | `dict[str, Any]`              | Changed values for put_paramset        |
| `get_changed_parameters()` | `dict[str, ParamsetChange]`   | Detailed diff between initial/current  |
| `get_current_value()`      | `Any`                         | Current value of a parameter           |
| `validate()`               | `dict[str, ValidationResult]` | Validate all values                    |
| `validate_changes()`       | `dict[str, ValidationResult]` | Validate only changed values           |
| `reset_to_defaults()`      | `None`                        | Reset to parameter defaults            |
| `discard()`                | `None`                        | Revert all changes                     |

### Properties

| Property   | Type   | Description                    |
| ---------- | ------ | ------------------------------ |
| `is_dirty` | `bool` | Any value differs from initial |
| `can_undo` | `bool` | Undo is possible               |
| `can_redo` | `bool` | Redo is possible               |

## LabelResolver

Uses upstream CCU translations from aiohomematic. Falls back to automatic formatting (split by underscore, title case) when no translation is found.

```python
from aiohomematic_config import LabelResolver

resolver = LabelResolver(locale="de")
label = resolver.resolve(parameter_id="TEMPERATURE_OFFSET", channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER")
# -> translated label from CCU translations

has = resolver.has_translation(parameter_id="TEMPERATURE_OFFSET", channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER")
# -> True if CCU translation exists
```

### Methods

| Method                                       | Returns | Description                                    |
| -------------------------------------------- | ------- | ---------------------------------------------- |
| `resolve(parameter_id, channel_type="")`     | `str`   | Translated label or humanized fallback         |
| `has_translation(parameter_id, channel_type)` | `bool`  | Whether a CCU translation exists               |

### Properties

| Property | Type  | Description        |
| -------- | ----- | ------------------ |
| `locale` | `str` | The current locale |

## ConfigExporter

```python
from aiohomematic_config import export_configuration, import_configuration

json_str = export_configuration(
    device_address="ADDR",
    model="HmIP-eTRV-2",
    channel_address="ADDR:1",
    channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
    paramset_key="MASTER",
    values={"TEMPERATURE_OFFSET": 1.5},
)

config = import_configuration(json_data=json_str)
```

### ExportedConfiguration

| Field             | Type              | Description                |
| ----------------- | ----------------- | -------------------------- |
| `version`         | `str`             | Export format version      |
| `exported_at`     | `str`             | ISO timestamp              |
| `device_address`  | `str`             | Device address             |
| `model`           | `str`             | Device model               |
| `channel_address` | `str`             | Channel address            |
| `channel_type`    | `str`             | Channel type               |
| `paramset_key`    | `str`             | Paramset key               |
| `values`          | `dict[str, Any]`  | Configuration values       |

## ConfigChangeLog

FIFO-capped log for tracking paramset modifications.

```python
from aiohomematic_config import ConfigChangeLog, build_change_diff

log = ConfigChangeLog(max_entries=500)

# Build diff from old/new values
diff = build_change_diff(
    old_values={"TEMPERATURE_OFFSET": 0.0},
    new_values={"TEMPERATURE_OFFSET": 1.5},
)
# -> {"TEMPERATURE_OFFSET": {"old": 0.0, "new": 1.5}}

# Record a change
entry = log.add(
    entry_id="device_001",
    interface_id="HmIP-RF",
    channel_address="ADDR:1",
    device_name="Living Room TRV",
    device_model="HmIP-eTRV-2",
    paramset_key="MASTER",
    changes=diff,
    source="user",
)

# Query entries
entries, total = log.get_entries(entry_id="device_001", limit=50)

# Persistence
raw = log.to_dicts()
log.load_entries(raw_entries=raw)

# Clear by entry
removed = log.clear_by_entry_id(entry_id="device_001")
```

### ConfigChangeEntry

| Field             | Type                          | Description               |
| ----------------- | ----------------------------- | ------------------------- |
| `timestamp`       | `str`                         | ISO timestamp             |
| `entry_id`        | `str`                         | Identifier for grouping   |
| `interface_id`    | `str`                         | Interface identifier      |
| `channel_address` | `str`                         | Channel address           |
| `device_name`     | `str`                         | Human-readable name       |
| `device_model`    | `str`                         | Device model              |
| `paramset_key`    | `str`                         | Paramset key              |
| `changes`         | `dict[str, dict[str, Any]]`   | Parameter diffs           |
| `source`          | `str`                         | Change origin             |

## Link Parameter Metadata

Classifies link paramset parameters into categories with UI metadata.

```python
from aiohomematic_config import classify_link_parameter, LinkParamCategory, KeypressGroup

meta = classify_link_parameter(parameter_id="SHORT_ON_TIME_BASE")
# meta.category      -> LinkParamCategory.TIME
# meta.keypress_group -> KeypressGroup.SHORT
# meta.time_pair_id  -> "SHORT_ON_TIME"
# meta.time_selector_type -> TimeSelectorType.TIME_ON_OFF
```

### classify_link_parameter

Returns a `LinkParamMeta` dataclass with:

| Field                | Type                       | Description                              |
| -------------------- | -------------------------- | ---------------------------------------- |
| `category`           | `LinkParamCategory`        | time / level / jump_target / condition / action / other |
| `keypress_group`     | `KeypressGroup`            | short / long / common                    |
| `display_as_percent` | `bool`                     | Show value as percentage                 |
| `has_last_value`     | `bool`                     | Supports "last value" option             |
| `hidden_by_default`  | `bool`                     | Hide in default view                     |
| `time_pair_id`       | `str \| None`             | Groups BASE/FACTOR pairs                 |
| `time_selector_type` | `TimeSelectorType \| None` | timeOnOff / delay / rampOnOff            |

### Time Encoding / Decoding

```python
from aiohomematic_config import decode_time_value, encode_time_value, TimeSelectorType

seconds = decode_time_value(base=7, factor=1)
# -> 3600.0 (1 hour)

base, factor = encode_time_value(seconds=3600.0, selector_type=TimeSelectorType.TIME_ON_OFF)
# -> (7, 1)
```

### Time Presets

```python
from aiohomematic_config import get_time_presets, TimeSelectorType

presets = get_time_presets(selector_type=TimeSelectorType.TIME_ON_OFF, locale="de")
# -> [{"base": 0, "factor": 0, "label": "Nicht aktiv"}, ...]
```

## Profile Store

Loads and queries easymode profile definitions for Homematic device links.

```python
from aiohomematic_config import ProfileStore

store = ProfileStore()

# Get available profiles for a channel type pair
profiles = await store.get_profiles(
    receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
    sender_channel_type="KEY_TRANSCEIVER",
    locale="de",
)
# -> list[ResolvedProfile] or None

# Match current values to active profile
profile_id = await store.match_active_profile(
    receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
    sender_channel_type="KEY_TRANSCEIVER",
    current_values=current_link_values,
)
# -> profile ID (0 = Expert/no match)
```

### ResolvedProfile

| Field             | Type                | Description                        |
| ----------------- | ------------------- | ---------------------------------- |
| `id`              | `int`               | Profile ID                         |
| `name`            | `str`               | Localized profile name             |
| `description`     | `str`               | Localized profile description      |
| `editable_params` | `list[str]`         | Parameters the user can adjust     |
| `fixed_params`    | `dict[str, float]`  | Parameters fixed by this profile   |
| `default_values`  | `dict[str, float]`  | Default values for editable params |

### ProfileDef

| Field         | Type                                   | Description                     |
| ------------- | -------------------------------------- | ------------------------------- |
| `id`          | `int`                                  | Profile ID                      |
| `name`        | `dict[str, str]`                       | Names by locale                 |
| `description` | `dict[str, str]`                       | Descriptions by locale          |
| `params`      | `dict[str, ProfileParamConstraint]`    | Parameter constraints           |

### ProfileParamConstraint

| Field             | Type                           | Description                 |
| ----------------- | ------------------------------ | --------------------------- |
| `constraint_type` | `"fixed" \| "list" \| "range"` | Type of constraint          |
| `value`           | `float \| None`               | Fixed value                 |
| `values`          | `list[float] \| None`         | Allowed values (list)       |
| `default`         | `float \| None`               | Default value               |
| `min_value`       | `float \| None`               | Range minimum               |
| `max_value`       | `float \| None`               | Range maximum               |
