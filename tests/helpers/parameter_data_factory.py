"""Factory functions for creating mock ParameterData in tests."""

from __future__ import annotations

from aiohomematic.const import Flag, Operations, ParameterData, ParameterType


def make_float_param(
    *,
    min_val: float = 0.0,
    max_val: float = 100.0,
    default: float = 0.0,
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


def make_integer_param(
    *,
    min_val: int = 0,
    max_val: int = 100,
    default: int = 0,
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


def make_bool_param(
    *,
    default: bool = False,
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


def make_enum_param(
    *,
    values: list[str],
    default: str | None = None,
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
        DEFAULT=default or values[0],
        VALUE_LIST=values,
        OPERATIONS=ops,
        FLAGS=flags,
    )


def make_string_param(
    *,
    default: str = "",
    writable: bool = True,
    visible: bool = True,
) -> ParameterData:
    """Create a STRING ParameterData."""
    ops = Operations.READ | (Operations.WRITE if writable else Operations.NONE)
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.STRING,
        MIN="",
        MAX="",
        DEFAULT=default,
        OPERATIONS=ops,
        FLAGS=flags,
    )


def make_action_param(
    *,
    visible: bool = True,
) -> ParameterData:
    """Create an ACTION ParameterData."""
    flags = Flag.VISIBLE if visible else 0
    return ParameterData(
        TYPE=ParameterType.ACTION,
        MIN=False,
        MAX=True,
        DEFAULT=False,
        OPERATIONS=Operations.WRITE,
        FLAGS=flags,
    )
