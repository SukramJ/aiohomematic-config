# aiohomematic-config

[![CI](https://github.com/sukramj/aiohomematic-config/actions/workflows/test-run.yaml/badge.svg)](https://github.com/sukramj/aiohomematic-config/actions/workflows/test-run.yaml)
[![codecov](https://codecov.io/gh/sukramj/aiohomematic-config/branch/main/graph/badge.svg)](https://codecov.io/gh/sukramj/aiohomematic-config)
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

## Development

Parts of aiohomematic-config are developed with agentic AI assistance, primarily [Claude Code](https://www.anthropic.com/claude-code). Incoming issues are also triaged and analysed with agentic help. Every change is still reviewed by a human maintainer and must pass the project's test suite before it lands -- the AI speeds up the work, it does not replace the review gate.

For the rules that apply to AI-assisted contributions, see the [AI Contribution Policy](AI_POLICY.md).

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

This library builds on the data structures of [aiohomematic](https://github.com/sukramj/aiohomematic) and the wider Homematic Python ecosystem. Special thanks to [Daniel Perna](https://github.com/danielperna84), whose original work on `pyhomematic` and `hahomematic` laid the foundation for this ecosystem.
