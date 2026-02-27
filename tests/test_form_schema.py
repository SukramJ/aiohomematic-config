"""Tests for form schema generator."""

from __future__ import annotations

from typing import Any

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType

from aiohomematic_config import FormParameter, FormSchema, FormSchemaGenerator, FormSection, WidgetType


class TestFormSchemaGenerator:
    """Test FormSchemaGenerator."""

    def test_channel_type_label(self) -> None:
        """channel_type_label should be resolved from upstream translations."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="SWITCH_VIRTUAL_RECEIVER",
        )
        assert schema.channel_type_label == "Switch actuator"

    def test_channel_type_label_de(self) -> None:
        """channel_type_label should use the correct locale."""
        generator = FormSchemaGenerator(locale="de")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="SWITCH_VIRTUAL_RECEIVER",
        )
        assert schema.channel_type_label == "Schaltaktor"

    def test_channel_type_label_empty(self) -> None:
        """channel_type_label should be empty when no channel_type is given."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
        )
        assert schema.channel_type_label == ""

    def test_channel_type_label_fallback(self) -> None:
        """channel_type_label should fall back to channel_type if no translation."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            channel_type="NONEXISTENT_CHANNEL_TYPE",
        )
        assert schema.channel_type_label == "NONEXISTENT_CHANNEL_TYPE"

    def test_description_locale_de(
        self,
        permissive_generator_de: FormSchemaGenerator,
    ) -> None:
        """Description should use the correct locale."""
        descriptions: dict[str, ParameterData] = {
            "TEMPERATURE_OFFSET": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=-3.5,
                MAX=3.5,
                DEFAULT=0.0,
                UNIT="°C",
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema_de = permissive_generator_de.generate(
            descriptions=descriptions,
            current_values={"TEMPERATURE_OFFSET": 0.0},
        )
        param_de = schema_de.sections[0].parameters[0]
        assert param_de.description is not None

    def test_description_none_for_unknown_parameter(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Description should be None when no help text exists."""
        descriptions: dict[str, ParameterData] = {
            "FAKE_UNKNOWN_PARAM_Z": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=1.0,
                DEFAULT=0.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"FAKE_UNKNOWN_PARAM_Z": 0.0},
            require_translation=False,
        )
        param = schema.sections[0].parameters[0]
        assert param.description is None

    def test_description_populated_for_known_parameter(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Description should contain Markdown help text for known parameters."""
        descriptions: dict[str, ParameterData] = {
            "TEMPERATURE_OFFSET": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=-3.5,
                MAX=3.5,
                DEFAULT=0.0,
                UNIT="°C",
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"TEMPERATURE_OFFSET": 0.0},
        )
        param = schema.sections[0].parameters[0]
        assert param.description is not None
        assert len(param.description) > 0

    def test_empty_descriptions(self) -> None:
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
        )
        assert schema.total_parameters == 0
        assert schema.writable_parameters == 0
        assert schema.sections == []

    def test_enum_options_included(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        descriptions: dict[str, ParameterData] = {
            "CHANNEL_OPERATION_MODE": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=2,
                DEFAULT="OFF",
                VALUE_LIST=["OFF", "MANUAL", "AUTO"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"CHANNEL_OPERATION_MODE": "OFF"},
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

    def test_invisible_parameters_excluded(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Parameters without VISIBLE flag should be excluded."""
        descriptions: dict[str, ParameterData] = {
            "TEMPERATURE_OFFSET": ParameterData(
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
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"TEMPERATURE_OFFSET": 5.0, "INVISIBLE_PARAM": 5.0},
        )
        all_param_ids = [p.id for s in schema.sections for p in s.parameters]
        assert "TEMPERATURE_OFFSET" in all_param_ids
        assert "INVISIBLE_PARAM" not in all_param_ids

    def test_model_description(self) -> None:
        """model_description should be resolved from upstream translations."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            model="HmIP-SWDO",
        )
        assert schema.model_description == "Homematic IP Window / Door Contact - optical"

    def test_model_description_de(self) -> None:
        """model_description should use the correct locale."""
        generator = FormSchemaGenerator(locale="de")
        schema = generator.generate(
            descriptions={},
            current_values={},
            model="HmIP-SWDO",
        )
        assert "Fenster" in schema.model_description

    def test_model_description_empty(self) -> None:
        """model_description should be empty when no model is given."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
        )
        assert schema.model_description == ""

    def test_model_description_fallback(self) -> None:
        """model_description should be empty when no translation is available."""
        generator = FormSchemaGenerator(locale="en")
        schema = generator.generate(
            descriptions={},
            current_values={},
            model="NONEXISTENT-MODEL",
        )
        assert schema.model_description == ""

    def test_modified_detection(
        self,
        thermostat_descriptions: dict[str, ParameterData],
    ) -> None:
        """Modified flag should be True when current != default."""
        generator = FormSchemaGenerator(locale="en")
        values = {
            "TEMPERATURE_OFFSET": 2.0,  # default is 0.0
            "TRANSMIT_TRY_MAX": 6,  # default is 6 (not modified)
            "CHANNEL_OPERATION_MODE": "NORMAL_MODE",
            "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": False,
            "LOCAL_RESET_DISABLED": False,
            "BRIGHTNESS_FILTER": 2.0,
        }
        schema = generator.generate(
            descriptions=thermostat_descriptions,
            current_values=values,
        )
        all_params = [p for s in schema.sections for p in s.parameters]
        temp_offset = next(p for p in all_params if p.id == "TEMPERATURE_OFFSET")
        transmit_try = next(p for p in all_params if p.id == "TRANSMIT_TRY_MAX")
        assert temp_offset.modified is True
        assert transmit_try.modified is False

    def test_option_labels_de(
        self,
        permissive_generator_de: FormSchemaGenerator,
    ) -> None:
        """option_labels should use the correct locale."""
        descriptions: dict[str, ParameterData] = {
            "COLOR": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=1,
                DEFAULT="BLUE",
                VALUE_LIST=["BLUE", "RED"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_de.generate(
            descriptions=descriptions,
            current_values={"COLOR": "BLUE"},
        )
        param = schema.sections[0].parameters[0]
        assert param.option_labels is not None
        assert param.option_labels["BLUE"] == "Blau"
        assert param.option_labels["RED"] == "Rot"

    def test_option_labels_humanized_when_no_translations(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """option_labels should fall back to humanized values when no translations exist."""
        descriptions: dict[str, ParameterData] = {
            "CHANNEL_OPERATION_MODE": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=2,
                DEFAULT="XYZZY_OPTION",
                VALUE_LIST=["XYZZY_OPTION", "QWERTY_OPTION", "ASDFG_OPTION"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"CHANNEL_OPERATION_MODE": "XYZZY_OPTION"},
        )
        param = schema.sections[0].parameters[0]
        assert param.option_labels is not None
        assert param.option_labels["XYZZY_OPTION"] == "Xyzzy Option"
        assert param.option_labels["QWERTY_OPTION"] == "Qwerty Option"
        assert param.option_labels["ASDFG_OPTION"] == "Asdfg Option"

    def test_option_labels_populated(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """option_labels should map VALUE_LIST entries to upstream translations."""
        descriptions: dict[str, ParameterData] = {
            "COLOR": ParameterData(
                TYPE=ParameterType.ENUM,
                MIN=0,
                MAX=2,
                DEFAULT="BLUE",
                VALUE_LIST=["BLUE", "GREEN", "RED"],
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"COLOR": "BLUE"},
        )
        param = schema.sections[0].parameters[0]
        assert param.options == ["BLUE", "GREEN", "RED"]
        assert param.option_labels is not None
        assert param.option_labels["BLUE"] == "Blue"
        assert param.option_labels["GREEN"] == "Green"
        assert param.option_labels["RED"] == "Red"

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

    def test_read_only_parameter(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Non-writable parameters should get READ_ONLY widget."""
        descriptions: dict[str, ParameterData] = {
            "ACTUAL_TEMPERATURE": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=100.0,
                DEFAULT=50.0,
                OPERATIONS=Operations.READ,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"ACTUAL_TEMPERATURE": 50.0},
        )
        param = schema.sections[0].parameters[0]
        assert param.widget == WidgetType.READ_ONLY
        assert param.writable is False

    def test_require_translation_false_includes_untranslated_params(self) -> None:
        """Parameters without CCU translations should be included when require_translation=False."""
        generator = FormSchemaGenerator(locale="en")
        descriptions: dict[str, ParameterData] = {
            "FAKE_UNKNOWN_PARAM_A": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=111600.0,
                DEFAULT=0.0,
                UNIT="s",
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
            "FAKE_UNKNOWN_PARAM_B": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=1.0,
                DEFAULT=1.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        # With require_translation=True (default), untranslated params are excluded
        schema_strict = generator.generate(
            descriptions=descriptions,
            current_values={"FAKE_UNKNOWN_PARAM_A": 0.0, "FAKE_UNKNOWN_PARAM_B": 1.0},
            require_translation=True,
        )
        assert schema_strict.total_parameters == 0

        # With require_translation=False, untranslated params are included
        schema_permissive = generator.generate(
            descriptions=descriptions,
            current_values={"FAKE_UNKNOWN_PARAM_A": 0.0, "FAKE_UNKNOWN_PARAM_B": 1.0},
            require_translation=False,
        )
        assert schema_permissive.total_parameters == 2
        all_param_ids = [p.id for s in schema_permissive.sections for p in s.parameters]
        assert "FAKE_UNKNOWN_PARAM_A" in all_param_ids
        assert "FAKE_UNKNOWN_PARAM_B" in all_param_ids

    def test_require_translation_false_uses_humanized_labels(self) -> None:
        """Parameters without translations should get humanized labels as fallback."""
        generator = FormSchemaGenerator(locale="en")
        descriptions: dict[str, ParameterData] = {
            "FAKE_UNKNOWN_PARAM_X": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=0.0,
                MAX=1.0,
                DEFAULT=0.05,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = generator.generate(
            descriptions=descriptions,
            current_values={"FAKE_UNKNOWN_PARAM_X": 0.05},
            require_translation=False,
        )
        param = schema.sections[0].parameters[0]
        assert param.label == "Fake Unknown Param X"

    def test_schedule_parameters_excluded(
        self,
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        """Schedule parameters (XX_WP_* and WEEK_PROGRAM_*) should be excluded."""
        descriptions: dict[str, ParameterData] = {
            "TEMPERATURE_OFFSET": ParameterData(
                TYPE=ParameterType.FLOAT,
                MIN=-3.5,
                MAX=3.5,
                DEFAULT=0.0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
            "1_WP_ENDTIME_1": ParameterData(
                TYPE=ParameterType.INTEGER,
                MIN=0,
                MAX=1440,
                DEFAULT=360,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
            "WEEK_PROGRAM_POINTER": ParameterData(
                TYPE=ParameterType.INTEGER,
                MIN=0,
                MAX=5,
                DEFAULT=0,
                OPERATIONS=Operations.READ | Operations.WRITE,
                FLAGS=Flag.VISIBLE,
            ),
        }
        schema = permissive_generator_en.generate(
            descriptions=descriptions,
            current_values={"TEMPERATURE_OFFSET": 0.0, "1_WP_ENDTIME_1": 360, "WEEK_PROGRAM_POINTER": 0},
        )
        all_param_ids = [p.id for s in schema.sections for p in s.parameters]
        assert "TEMPERATURE_OFFSET" in all_param_ids
        assert "1_WP_ENDTIME_1" not in all_param_ids
        assert "WEEK_PROGRAM_POINTER" not in all_param_ids

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
        permissive_generator_en: FormSchemaGenerator,
    ) -> None:
        schema = permissive_generator_en.generate(
            descriptions=switch_descriptions,
            current_values=switch_values,
        )
        assert schema.total_parameters == 3
