"""Shared test fixtures for aiohomematic-config."""

from __future__ import annotations

from typing import Any

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType
import pytest


@pytest.fixture
def thermostat_descriptions() -> dict[str, ParameterData]:
    """Return MASTER paramset descriptions for a thermostat (HmIP-eTRV-2)."""
    return {
        "TEMPERATURE_OFFSET": _make_float_param(min_val=-3.5, max_val=3.5, default=0.0, unit="°C"),
        "BOOST_TIME_PERIOD": _make_integer_param(min_val=0, max_val=30, default=5, unit="min"),
        "SHOW_WEEKDAY": _make_enum_param(
            values=["SATURDAY", "SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"],
            default="SATURDAY",
        ),
        "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": _make_bool_param(default=False),
        "LOCAL_RESET_DISABLED": _make_bool_param(default=False),
        "TEMPERATURE_WINDOW_OPEN": _make_float_param(min_val=4.5, max_val=30.0, default=12.0, unit="°C"),
    }


@pytest.fixture
def thermostat_values() -> dict[str, Any]:
    """Return current values for a thermostat."""
    return {
        "TEMPERATURE_OFFSET": 1.5,
        "BOOST_TIME_PERIOD": 5,
        "SHOW_WEEKDAY": "SATURDAY",
        "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": False,
        "LOCAL_RESET_DISABLED": False,
        "TEMPERATURE_WINDOW_OPEN": 12.0,
    }


@pytest.fixture
def switch_descriptions() -> dict[str, ParameterData]:
    """Return MASTER paramset descriptions for a switch (HmIP-PS)."""
    return {
        "POWERUP_ONTIME": _make_float_param(min_val=0.0, max_val=327680.0, default=0.0, unit="s"),
        "POWERUP_OFFTIME": _make_float_param(min_val=0.0, max_val=327680.0, default=0.0, unit="s"),
        "STATUSINFO_MINDELAY": _make_float_param(min_val=2.0, max_val=10.0, default=2.0, unit="s"),
    }


@pytest.fixture
def switch_values() -> dict[str, Any]:
    """Return current values for a switch."""
    return {
        "POWERUP_ONTIME": 0.0,
        "POWERUP_OFFTIME": 0.0,
        "STATUSINFO_MINDELAY": 2.0,
    }


def _make_float_param(
    *,
    min_val: float,
    max_val: float,
    default: float,
    unit: str = "",
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create a FLOAT ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.FLOAT,
        MIN=min_val,
        MAX=max_val,
        DEFAULT=default,
        UNIT=unit,
        OPERATIONS=ops,
        FLAGS=flags,
    )


def _make_integer_param(
    *,
    min_val: int,
    max_val: int,
    default: int,
    unit: str = "",
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create an INTEGER ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.INTEGER,
        MIN=min_val,
        MAX=max_val,
        DEFAULT=default,
        UNIT=unit,
        OPERATIONS=ops,
        FLAGS=flags,
    )


def _make_bool_param(
    *,
    default: bool,
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create a BOOL ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.BOOL,
        MIN=False,
        MAX=True,
        DEFAULT=default,
        OPERATIONS=ops,
        FLAGS=flags,
    )


def _make_enum_param(
    *,
    values: list[str],
    default: str,
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create an ENUM ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.ENUM,
        MIN=0,
        MAX=len(values) - 1,
        DEFAULT=default,
        VALUE_LIST=values,
        OPERATIONS=ops,
        FLAGS=flags,
    )
