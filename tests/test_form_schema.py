"""Tests for form schema generator."""

from __future__ import annotations

from typing import Any

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType

from aiohomematic_config import FormParameter, FormSchema, FormSchemaGenerator, FormSection, WidgetType


class TestFormSchemaGenerator:
    """Test FormSchemaGenerator."""

    def test_empty_descriptions(self) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
        )
        assert schema.total_parameters == 0
        assert schema.writable_parameters == 0
        assert schema.sections == []

    def test_enum_options_included(self) -> None:
        descriptions: dict[str, ParameterData] = {
            "MODE": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=2,
                DEFAULT="OFF",
                VALUE_LIST=["OFF", "MANUAL", "AUTO"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=descriptions,
            current_values={"MODE": "OFF"},
        )
        param = schema.sections[0].parameters[0]
        assert param.options == ["OFF", "MANUAL", "AUTO"]

    def test_generate_thermostat_schema(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=thermostat_values,
            channel_address="0001D3C99C36D0:1",
            channel_type="HEATING_CLIMATECONTROL_TRANSCEIVER",
        )
        assert isinstance(schema, FormSchema)
        assert schema.channel_address == "0001D3C99C36D0:1"
        assert schema.total_parameters > 0
        assert schema.writable_parameters > 0

    def test_invisible_parameters_excluded(self) -> None:
        """Parameters without VISIBLE flag should be excluded."""
        descriptions: dict[str, ParameterData] = {
            "VISIBLE_PARAM": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=10.0,
                DEFAULT=5.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
            "INVISIBLE_PARAM": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=10.0,
                DEFAULT=5.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=0,
            ),
        }
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=descriptions,
            current_values={"VISIBLE_PARAM": 5.0, "INVISIBLE_PARAM": 5.0},
        )
        all_param_ids = [p.id for s in schema.sections for p in s.parameters]
        assert "VISIBLE_PARAM" in all_param_ids
        assert "INVISIBLE_PARAM" not in all_param_ids

    def test_modified_detection(
        self,
        thermostat_descriptions: dict[str, ParameterData],
    ) -> None:
        """Modified flag should be True when current != default."""
        generator = FormSchemaGenerator(locale="en")
        values = {
            "TEMPERATURE_OFFSET": 2.0,  # default is 0.0
            "BOOST_TIME_PERIOD": 5,  # default is 5 (not modified)
            "SHOW_WEEKDAY": "SATURDAY",
            "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": False,
            "LOCAL_RESET_DISABLED": False,
            "TEMPERATURE_WINDOW_OPEN": 12.0,
        }
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=values,
        )
        all_params = [p for s in schema.sections for p in s.parameters]
        temp_offset = next(p for p in all_params if p.id == "TEMPERATURE_OFFSET")
        boost_time = next(p for p in all_params if p.id == "BOOST_TIME_PERIOD")
        assert temp_offset.modified is True
        assert boost_time.modified is False

    def test_parameters_have_labels(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=thermostat_values,
        )
        for section in schema.sections:
            for param in section.parameters:
                assert isinstance(param, FormParameter)
                assert len(param.label) > 0
                assert param.id

    def test_read_only_parameter(self) -> None:
        """Non-writable parameters should get READ_ONLY widget."""
        descriptions: dict[str, ParameterData] = {
            "READONLY_PARAM": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=100.0,
                DEFAULT=50.0,
                OPERATIONS=Operations.READ,
                FLAGS=Flag.VISIBLE,
            ),
        }
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=descriptions,
            current_values={"READONLY_PARAM": 50.0},
        )
        param = schema.sections[0].parameters[0]
        assert param.widget == WidgetType.READ_ONLY
        assert param.writable is False

    def test_sections_are_populated(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=thermostat_values,
        )
        assert len(schema.sections) > 0
        for section in schema.sections:
            assert isinstance(section, FormSection)
            assert len(section.parameters) > 0

    def test_switch_descriptions(
        self,
        switch_descriptions: dict[str, ParameterData],
        switch_values: dict[str, Any],
    ) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions=switch_descriptions,
            current_values=switch_values,
        )
        assert schema.total_parameters == 3
