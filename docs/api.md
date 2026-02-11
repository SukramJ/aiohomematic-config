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
)
```

### FormSchema

| Field                 | Type                | Description                |
| --------------------- | ------------------- | -------------------------- |
| `channel_address`     | `str`               | Channel address            |
| `channel_type`        | `str`               | Channel type               |
| `sections`            | `list[FormSection]` | Grouped parameter sections |
| `total_parameters`    | `int`               | Total visible parameters   |
| `writable_parameters` | `int`               | Writable parameters count  |

### FormSection

| Field        | Type                  | Description                |
| ------------ | --------------------- | -------------------------- |
| `id`         | `str`                 | Group identifier           |
| `title`      | `str`                 | Human-readable group title |
| `parameters` | `list[FormParameter]` | Parameters in this group   |

### FormParameter

| Field           | Type                   | Description                        |
| --------------- | ---------------------- | ---------------------------------- |
| `id`            | `str`                  | Parameter ID                       |
| `label`         | `str`                  | Human-readable label               |
| `type`          | `str`                  | Parameter type                     |
| `widget`        | `WidgetType`           | Recommended UI widget              |
| `min`           | `float \| int \| None` | Minimum value                      |
| `max`           | `float \| int \| None` | Maximum value                      |
| `step`          | `float \| None`        | Step increment                     |
| `unit`          | `str`                  | Unit string                        |
| `default`       | `Any`                  | Default value                      |
| `current_value` | `Any`                  | Current value                      |
| `writable`      | `bool`                 | Whether parameter is writable      |
| `modified`      | `bool`                 | Whether value differs from default |
| `options`       | `list[str] \| None`    | Enum options                       |

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

| Method                  | Returns                       | Description                     |
| ----------------------- | ----------------------------- | ------------------------------- |
| `set(parameter, value)` | `None`                        | Set value, record for undo      |
| `undo()`                | `bool`                        | Undo last change                |
| `redo()`                | `bool`                        | Redo last undone change         |
| `get_changes()`         | `dict[str, Any]`              | Changed values for put_paramset |
| `get_current_value()`   | `Any`                         | Current value of a parameter    |
| `validate()`            | `dict[str, ValidationResult]` | Validate all values             |
| `validate_changes()`    | `dict[str, ValidationResult]` | Validate only changed values    |
| `reset_to_defaults()`   | `None`                        | Reset to parameter defaults     |
| `discard()`             | `None`                        | Revert all changes              |

### Properties

| Property   | Type   | Description                    |
| ---------- | ------ | ------------------------------ |
| `is_dirty` | `bool` | Any value differs from initial |
| `can_undo` | `bool` | Undo is possible               |
| `can_redo` | `bool` | Redo is possible               |

## LabelResolver

```python
from aiohomematic_config import LabelResolver

resolver = LabelResolver(locale="de")
label = resolver.resolve(parameter_id="TEMPERATURE_OFFSET")
# -> "Temperatur-Offset"
```

## ConfigExporter

```python
from aiohomematic_config import export_configuration, import_configuration

json_str = export_configuration(
    device_address="ADDR",
    device_type="HmIP-eTRV-2",
    channel_address="ADDR:1",
    channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
    paramset_key="MASTER",
    values={"TEMPERATURE_OFFSET": 1.5},
)

config = import_configuration(json_data=json_str)
```
