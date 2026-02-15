"""
Form schema generator for Homematic device configuration.

Transforms ParameterData descriptions and current values into a
JSON-serializable form schema that any frontend can render.

Public API of this module is defined by __all__.
"""

from __future__ import annotations

from collections.abc import Mapping
import inspect
from typing import Any

from aiohomematic.ccu_translations import (
    get_channel_type_translation,
    get_device_model_description,
    get_parameter_value_translation,
)
from aiohomematic.const import ParameterData, ParameterType
from aiohomematic.parameter_tools import (
    get_parameter_step,
    is_parameter_internal,
    is_parameter_readable,
    is_parameter_visible,
    is_parameter_writable,
)
from pydantic import BaseModel

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
    option_labels: dict[str, str] | None = None


class FormSection(BaseModel):
    """A logical group of parameters in a form."""

    id: str
    title: str
    parameters: list[FormParameter]


class FormSchema(BaseModel):
    """Complete form schema for a channel's paramset configuration."""

    channel_address: str
    channel_type: str
    model_description: str = ""
    channel_type_label: str = ""
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
        self._grouper = grouper or ParameterGrouper(locale=locale)

    def generate(
        self,
        *,
        descriptions: Mapping[str, ParameterData],
        current_values: dict[str, Any],
        channel_address: str = "",
        channel_type: str = "",
        model: str = "",
        sub_model: str | None = None,
    ) -> FormSchema:
        """
        Generate a complete form schema for the given paramset.

        Args:
            descriptions: Parameter descriptions (from get_paramset_description).
            current_values: Current parameter values (from get_paramset).
            channel_address: Channel address for context.
            channel_type: Channel type for grouping hints.
            model: Device model ID for description lookup.
            sub_model: Optional sub-model for description fallback.

        Returns:
            A FormSchema ready for JSON serialization.

        """
        # Filter parameters using CCU-compatible rules:
        # 1. FLAGS & VISIBLE must be set
        # 2. FLAGS & INTERNAL must NOT be set
        # 3. OPERATIONS must include READ or WRITE
        # 4. A CCU translation must exist (matches CCU WebUI easymode behavior)
        visible_params: dict[str, ParameterData] = {
            param_id: pd
            for param_id, pd in descriptions.items()
            if is_parameter_visible(parameter_data=pd)
            and not is_parameter_internal(parameter_data=pd)
            and (is_parameter_readable(parameter_data=pd) or is_parameter_writable(parameter_data=pd))
            and self._label_resolver.has_translation(parameter_id=param_id, channel_type=channel_type)
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
                if (pd := visible_params.get(param_id)) is None:
                    continue

                writable = is_parameter_writable(parameter_data=pd)
                current = current_values.get(param_id)
                default = pd.get("DEFAULT")
                modified = current is not None and default is not None and current != default
                param_type = pd.get("TYPE", ParameterType.EMPTY)

                widget = determine_widget(parameter_data=pd)
                if not writable:
                    widget = WidgetType.READ_ONLY

                # Only include min/max for numeric types
                p_min = pd.get("MIN")
                p_max = pd.get("MAX")
                has_numeric_range = isinstance(p_min, (int, float)) and isinstance(p_max, (int, float))

                # Build option_labels for VALUE_LIST parameters
                options: list[str] | None = None
                option_labels: dict[str, str] | None = None
                if "VALUE_LIST" in pd:
                    options = list(pd["VALUE_LIST"])
                    resolved_labels: dict[str, str] = {}
                    for value in options:
                        if (
                            translated := get_parameter_value_translation(
                                parameter=param_id,
                                value=value,
                                channel_type=channel_type or None,
                                locale=self._label_resolver.locale,
                            )
                        ) is not None:
                            resolved_labels[value] = translated
                    if resolved_labels:
                        option_labels = resolved_labels

                form_param = FormParameter(
                    id=param_id,
                    label=self._label_resolver.resolve(
                        parameter_id=param_id,
                        channel_type=channel_type,
                    ),
                    type=str(param_type),
                    widget=widget,
                    min=p_min if has_numeric_range else None,
                    max=p_max if has_numeric_range else None,
                    step=get_parameter_step(parameter_data=pd) if has_numeric_range else None,
                    unit=pd.get("UNIT", ""),
                    default=default,
                    current_value=current,
                    writable=writable,
                    modified=modified,
                    options=options,
                    option_labels=option_labels,
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

        # Resolve channel type label
        channel_type_label = ""
        if channel_type:
            channel_type_label = (
                get_channel_type_translation(
                    channel_type=channel_type,
                    locale=self._label_resolver.locale,
                )
                or channel_type
            )

        # Resolve model description
        model_description = ""
        if model:
            model_description = (
                get_device_model_description(
                    model=model,
                    sub_model=sub_model,
                    locale=self._label_resolver.locale,
                )
                or ""
            )

        return FormSchema(
            channel_address=channel_address,
            channel_type=channel_type,
            model_description=model_description,
            channel_type_label=channel_type_label,
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
