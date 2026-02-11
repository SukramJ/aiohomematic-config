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
from aiohomematic_config.exporter import ExportedConfiguration, export_configuration, import_configuration
from aiohomematic_config.form_schema import FormParameter, FormSchema, FormSchemaGenerator, FormSection
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
