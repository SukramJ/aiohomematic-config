"""Tests for configuration session."""

from typing import Any

from aiohomematic.const import ParameterData

from aiohomematic_config import ConfigSession


class TestConfigSession:
    """Test ConfigSession."""

    def test_discard(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
        session.discard()
        assert not session.is_dirty
        assert not session.can_undo
        assert not session.can_redo
        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 1.5

    def test_get_changed_parameters(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
        result = session.get_changed_parameters()
        assert "TEMPERATURE_OFFSET" in result
        assert result["TEMPERATURE_OFFSET"].old_value == 1.5
        assert result["TEMPERATURE_OFFSET"].new_value == 2.0

    def test_get_changes(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
        session.set(parameter="LOCAL_RESET_DISABLED", value=True)
        changes = session.get_changes()
        assert changes == {"TEMPERATURE_OFFSET": 2.0, "LOCAL_RESET_DISABLED": True}

    def test_get_changes_empty_when_not_dirty(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        assert session.get_changes() == {}

    def test_get_current_value(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 1.5
        session.set(parameter="TEMPERATURE_OFFSET", value=2.5)
        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 2.5

    def test_initial_state_not_dirty(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        assert not session.is_dirty
        assert not session.can_undo
        assert not session.can_redo

    def test_multiple_undo_redo(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
        session.set(parameter="TEMPERATURE_OFFSET", value=3.0)
        session.set(parameter="TEMPERATURE_OFFSET", value=4.0)

        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 4.0
        session.undo()
        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 3.0
        session.undo()
        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 2.0
        session.redo()
        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 3.0

    def test_redo(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
        session.undo()
        assert session.redo()
        assert session.is_dirty
        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 2.0

    def test_redo_empty_returns_false(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        assert not session.redo()

    def test_reset_to_defaults(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        # TEMPERATURE_OFFSET initial=1.5, default=0.0
        session.reset_to_defaults()
        assert session.get_current_value(parameter="TEMPERATURE_OFFSET") == 0.0
        assert session.is_dirty

    def test_set_clears_redo_stack(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
        session.undo()
        session.set(parameter="TEMPERATURE_OFFSET", value=3.0)
        assert not session.can_redo

    def test_set_makes_dirty(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
        assert session.is_dirty
        assert session.can_undo

    def test_set_same_value_no_change(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=1.5)  # same as initial
        assert not session.is_dirty
        assert not session.can_undo

    def test_undo(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=2.0)
        assert session.undo()
        assert not session.is_dirty
        assert session.can_redo

    def test_undo_empty_returns_false(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        assert not session.undo()

    def test_validate_changes_returns_empty_when_no_changes(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        result = session.validate_changes()
        assert result == {}

    def test_validate_changes_validates_only_changed(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        session.set(parameter="TEMPERATURE_OFFSET", value=99.0)
        result = session.validate_changes()
        assert "TEMPERATURE_OFFSET" in result
        assert result["TEMPERATURE_OFFSET"].valid is False

    def test_validate_returns_empty_for_valid_values(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        result = session.validate()
        assert result == {}

    def test_validate_returns_failures_for_invalid_values(
        self,
        thermostat_descriptions: dict[str, ParameterData],
        thermostat_values: dict[str, Any],
    ) -> None:
        session = ConfigSession(
            descriptions=thermostat_descriptions,
            initial_values=thermostat_values,
        )
        # Set out-of-range value (max is 3.5)
        session.set(parameter="TEMPERATURE_OFFSET", value=99.0)
        result = session.validate()
        assert "TEMPERATURE_OFFSET" in result
        assert result["TEMPERATURE_OFFSET"].valid is False
