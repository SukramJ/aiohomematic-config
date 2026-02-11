"""Tests for widget type determination."""

from __future__ import annotations

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType

from aiohomematic_config import WidgetType, determine_widget


class TestDetermineWidget:
    """Test determine_widget function."""

    def test_action_returns_button(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.ACTION,
            MIN=False,
            MAX=True,
            DEFAULT=False,
            OPERATIONS=Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.BUTTON

    def test_bool_returns_toggle(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.BOOL,
            MIN=False,
            MAX=True,
            DEFAULT=False,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.TOGGLE

    def test_enum_few_options_returns_radio_group(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.ENUM,
            MIN=0,
            MAX=1,
            DEFAULT="OFF",
            VALUE_LIST=["OFF", "ON"],
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.RADIO_GROUP

    def test_enum_five_options_returns_dropdown(self) -> None:
        values = ["A", "B", "C", "D", "E"]
        pd = ParameterData(
            TYPE=ParameterType.ENUM,
            MIN=0,
            MAX=len(values) - 1,
            DEFAULT=values[0],
            VALUE_LIST=values,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.DROPDOWN

    def test_enum_four_options_returns_radio_group(self) -> None:
        """Four options is exactly at threshold, should be radio group."""
        values = ["A", "B", "C", "D"]
        pd = ParameterData(
            TYPE=ParameterType.ENUM,
            MIN=0,
            MAX=len(values) - 1,
            DEFAULT=values[0],
            VALUE_LIST=values,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.RADIO_GROUP

    def test_enum_many_options_returns_dropdown(self) -> None:
        values = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        pd = ParameterData(
            TYPE=ParameterType.ENUM,
            MIN=0,
            MAX=len(values) - 1,
            DEFAULT=values[0],
            VALUE_LIST=values,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.DROPDOWN

    def test_float_exact_100_returns_slider(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.FLOAT,
            MIN=0.0,
            MAX=100.0,
            DEFAULT=0.0,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.SLIDER_WITH_INPUT

    def test_float_large_range_returns_number_input(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.FLOAT,
            MIN=0.0,
            MAX=327680.0,
            DEFAULT=0.0,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.NUMBER_INPUT

    def test_float_small_range_returns_slider(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.FLOAT,
            MIN=-3.5,
            MAX=3.5,
            DEFAULT=0.0,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.SLIDER_WITH_INPUT

    def test_integer_boundary_range_returns_slider(self) -> None:
        """Range of exactly 20 should still be a slider."""
        pd = ParameterData(
            TYPE=ParameterType.INTEGER,
            MIN=0,
            MAX=20,
            DEFAULT=0,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.SLIDER_WITH_INPUT

    def test_integer_just_over_boundary_returns_number(self) -> None:
        """Range of 21 should be a number input."""
        pd = ParameterData(
            TYPE=ParameterType.INTEGER,
            MIN=0,
            MAX=21,
            DEFAULT=0,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.NUMBER_INPUT

    def test_integer_large_range_returns_number_input(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.INTEGER,
            MIN=0,
            MAX=65535,
            DEFAULT=0,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.NUMBER_INPUT

    def test_integer_small_range_returns_slider(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.INTEGER,
            MIN=0,
            MAX=10,
            DEFAULT=5,
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.SLIDER_WITH_INPUT

    def test_string_returns_text_input(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.STRING,
            MIN="",
            MAX="",
            DEFAULT="",
            OPERATIONS=Operations.READ | Operations.WRITE,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.TEXT_INPUT

    def test_unknown_type_returns_read_only(self) -> None:
        pd = ParameterData(
            TYPE=ParameterType.EMPTY,
            MIN=0,
            MAX=0,
            DEFAULT=0,
            OPERATIONS=Operations.READ,
            FLAGS=Flag.VISIBLE,
        )
        assert determine_widget(parameter_data=pd) == WidgetType.READ_ONLY


class TestWidgetType:
    """Test WidgetType enum values."""

    def test_all_widget_types_are_strings(self) -> None:
        for widget in WidgetType:
            assert isinstance(widget, str)
            assert isinstance(widget.value, str)

    def test_widget_type_count(self) -> None:
        assert len(WidgetType) == 8
