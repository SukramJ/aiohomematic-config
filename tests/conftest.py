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
        "TRANSMIT_TRY_MAX": _make_integer_param(min_val=1, max_val=10, default=6, unit=""),
        "CHANNEL_OPERATION_MODE": _make_enum_param(
            values=["NORMAL_MODE", "PASSIVE_MODE"],
            default="NORMAL_MODE",
        ),
        "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": _make_bool_param(default=False),
        "LOCAL_RESET_DISABLED": _make_bool_param(default=False),
        "BRIGHTNESS_FILTER": _make_float_param(min_val=0.0, max_val=7.0, default=2.0, unit=""),
    }


@pytest.fixture
def thermostat_values() -> dict[str, Any]:
    """Return current values for a thermostat."""
    return {
        "TEMPERATURE_OFFSET": 1.5,
        "TRANSMIT_TRY_MAX": 6,
        "CHANNEL_OPERATION_MODE": "NORMAL_MODE",
        "BUTTON_RESPONSE_WITHOUT_BACKLIGHT": False,
        "LOCAL_RESET_DISABLED": False,
        "BRIGHTNESS_FILTER": 2.0,
    }


@pytest.fixture
def switch_descriptions() -> dict[str, ParameterData]:
    """Return MASTER paramset descriptions for a switch (HmIP-PS)."""
    return {
        "ON_TIME": _make_float_param(min_val=0.0, max_val=327680.0, default=0.0, unit="s"),
        "RAMP_TIME": _make_float_param(min_val=0.0, max_val=327680.0, default=0.0, unit="s"),
        "STATUSINFO_MINDELAY": _make_float_param(min_val=2.0, max_val=10.0, default=2.0, unit="s"),
    }


@pytest.fixture
def switch_values() -> dict[str, Any]:
    """Return current values for a switch."""
    return {
        "ON_TIME": 0.0,
        "RAMP_TIME": 0.0,
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
