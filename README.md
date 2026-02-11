# aiohomematic-config

[![CI](https://github.com/sukramj/aiohomematic-config/actions/workflows/test-run.yaml/badge.svg)](https://github.com/sukramj/aiohomematic-config/actions/workflows/test-run.yaml)
[![codecov](https://codecov.io/gh/sukramj/aiohomematic-config/branch/devel/graph/badge.svg)](https://codecov.io/gh/sukramj/aiohomematic-config)
[![PyPI](https://img.shields.io/pypi/v/aiohomematic-config.svg)](https://pypi.org/project/aiohomematic-config/)

Presentation-layer library for Homematic device configuration UI.

Transforms Homematic device paramset descriptions into UI-optimized structures. No RPC knowledge, no CCU access -- operates purely on data structures from [aiohomematic](https://github.com/sukramj/aiohomematic).

## Installation

```bash
pip install aiohomematic-config
```

## Quick Start

```python
from aiohomematic_config import FormSchemaGenerator

generator = FormSchemaGenerator(locale="en")
schema = generator.generate(
    descriptions=descriptions,
    current_values=current_values,
    channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
)
# schema is a Pydantic model, JSON-serializable
print(schema.model_dump_json(indent=2))
```

## Key Components

| Component             | Purpose                                          |
| --------------------- | ------------------------------------------------ |
| `FormSchemaGenerator` | ParameterData + values -> JSON form schemas      |
| `ParameterGrouper`    | Flat parameter list -> grouped sections          |
| `LabelResolver`       | Technical parameter IDs -> human-readable labels |
| `ConfigSession`       | Change tracking, undo/redo, dirty state          |
| `ConfigExporter`      | Serialize/deserialize device configurations      |
| `WidgetType` mapping  | ParameterType -> appropriate UI widget           |

## License

MIT License - see [LICENSE](LICENSE) for details.
