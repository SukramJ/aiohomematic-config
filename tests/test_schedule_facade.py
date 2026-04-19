"""Tests for the schedule_facade module."""

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any
from unittest.mock import AsyncMock, Mock, PropertyMock

if TYPE_CHECKING:
    from aiohomematic.interfaces.model import DeviceProtocol, WeekProfileDataPointProtocol

from aiohomematic.const import ScheduleField, ScheduleProfile, ScheduleType
from aiohomematic.interfaces import ClimateWeekProfileDataPointProtocol
import pytest

from aiohomematic_config import (
    ClimateScheduleData,
    DeviceScheduleData,
    ScheduleDeviceInfo,
    get_climate_schedule,
    get_device_schedule,
    list_schedule_devices,
    set_climate_active_profile,
    set_climate_schedule_weekday,
    set_device_schedule,
    set_schedule_enabled,
)

# ---------------------------------------------------------------------------
# Helper: build mock devices
# ---------------------------------------------------------------------------


def _make_device(
    *,
    address: str = "0001D3C98DD4B6",
    name: str = "Test Device",
    model: str = "HmIP-BSM",
    interface_id: str = "hmip-rf",
    wp_dp: WeekProfileDataPointProtocol | None = None,
) -> DeviceProtocol:
    """Create a mock DeviceProtocol."""
    device = Mock(spec_set=["address", "name", "model", "interface_id", "week_profile_data_point"])
    type(device).address = PropertyMock(return_value=address)
    type(device).name = PropertyMock(return_value=name)
    type(device).model = PropertyMock(return_value=model)
    type(device).interface_id = PropertyMock(return_value=interface_id)
    type(device).week_profile_data_point = PropertyMock(return_value=wp_dp)
    return device


def _make_wp_dp(
    *,
    schedule_channel_address: str | None = "0001D3C98DD4B6:3",
    schedule_type: ScheduleType = ScheduleType.DEFAULT,
    schedule_domain: str | None = "switch",
    schedule_enabled: Mapping[str, bool] | None = None,
    max_entries: int = 5,
    available_target_channels: dict[str, Any] | None = None,
    schedule_data: dict[str, Any] | None = None,
    supported_schedule_fields: frozenset | None = None,
) -> WeekProfileDataPointProtocol:
    """Create a mock WeekProfileDataPointProtocol."""
    wp_dp = Mock()
    type(wp_dp).schedule_channel_address = PropertyMock(return_value=schedule_channel_address)
    type(wp_dp).schedule_type = PropertyMock(return_value=schedule_type)
    type(wp_dp).schedule_domain = PropertyMock(return_value=schedule_domain)
    type(wp_dp).schedule_enabled = PropertyMock(return_value=schedule_enabled)
    type(wp_dp).max_entries = PropertyMock(return_value=max_entries)
    type(wp_dp).available_target_channels = PropertyMock(
        return_value=available_target_channels if available_target_channels is not None else {}
    )
    type(wp_dp).supported_schedule_fields = PropertyMock(
        return_value=supported_schedule_fields if supported_schedule_fields is not None else frozenset()
    )
    wp_dp.get_schedule = AsyncMock(return_value=schedule_data or {"MONDAY": []})
    wp_dp.set_schedule = AsyncMock()
    wp_dp.set_schedule_enabled = AsyncMock()
    return wp_dp


def _make_climate_wp_dp(
    *,
    schedule_channel_address: str | None = "0001D3C98DD4B6:1",
    schedule_type: ScheduleType = ScheduleType.CLIMATE,
    schedule_domain: str | None = None,
    available_profiles: tuple[ScheduleProfile, ...] = (ScheduleProfile.P1, ScheduleProfile.P2, ScheduleProfile.P3),
    current_schedule_profile: ScheduleProfile = ScheduleProfile.P1,
    device_active_profile_index: int | None = 1,
    min_temp: float | None = 5.0,
    max_temp: float | None = 30.5,
    schedule_profile_data: dict[str, Any] | None = None,
    schedule_enabled: Mapping[str, bool] | None = None,
) -> ClimateWeekProfileDataPointProtocol:
    """
    Create a mock that passes isinstance checks for ClimateWeekProfileDataPointProtocol.

    We cannot use create_autospec or Mock(spec=...) because the protocol classes
    reference types (e.g. UnsubscribeCallback) that may not be resolvable in all
    environments. Instead we patch __class__ so isinstance() succeeds.
    """
    wp_dp = Mock()
    wp_dp.__class__ = ClimateWeekProfileDataPointProtocol
    type(wp_dp).schedule_channel_address = PropertyMock(return_value=schedule_channel_address)
    type(wp_dp).schedule_type = PropertyMock(return_value=schedule_type)
    type(wp_dp).schedule_domain = PropertyMock(return_value=schedule_domain)
    type(wp_dp).schedule_enabled = PropertyMock(return_value=schedule_enabled)
    type(wp_dp).available_profiles = PropertyMock(return_value=available_profiles)
    type(wp_dp).current_schedule_profile = PropertyMock(return_value=current_schedule_profile)
    type(wp_dp).device_active_profile_index = PropertyMock(return_value=device_active_profile_index)
    type(wp_dp).min_temp = PropertyMock(return_value=min_temp)
    type(wp_dp).max_temp = PropertyMock(return_value=max_temp)
    wp_dp.get_schedule_profile = AsyncMock(return_value=schedule_profile_data or {"MONDAY": []})
    wp_dp.set_schedule_weekday = AsyncMock()
    wp_dp.set_current_schedule_profile = Mock()
    wp_dp.set_schedule_enabled = AsyncMock()
    return wp_dp


# ---------------------------------------------------------------------------
# list_schedule_devices
# ---------------------------------------------------------------------------


class TestListScheduleDevices:
    """Tests for list_schedule_devices."""

    def test_empty_devices(self) -> None:
        """Empty tuple returns empty list."""
        result = list_schedule_devices(devices=())
        assert result == []

    def test_mixed_devices(self) -> None:
        """Only schedule-capable devices are returned."""
        wp_dp = _make_wp_dp()
        device_with = _make_device(address="AAA", name="With", wp_dp=wp_dp)
        device_without = _make_device(address="BBB", name="Without", wp_dp=None)
        result = list_schedule_devices(devices=(device_with, device_without))
        assert len(result) == 1
        assert result[0].address == "AAA"

    def test_returns_devices_with_schedule_support(self) -> None:
        """Devices with week_profile_data_point are included."""
        wp_dp = _make_wp_dp()
        device = _make_device(wp_dp=wp_dp)
        result = list_schedule_devices(devices=(device,))

        assert len(result) == 1
        info = result[0]
        assert isinstance(info, ScheduleDeviceInfo)
        assert info.address == "0001D3C98DD4B6"
        assert info.name == "Test Device"
        assert info.model == "HmIP-BSM"
        assert info.interface_id == "hmip-rf"
        assert info.channel_address == "0001D3C98DD4B6:3"
        assert info.schedule_type == ScheduleType.DEFAULT.value
        assert info.schedule_domain == "switch"

    def test_schedule_channel_address_none(self) -> None:
        """When schedule_channel_address is None, empty string is used."""
        wp_dp = _make_wp_dp(schedule_channel_address=None)
        device = _make_device(wp_dp=wp_dp)
        result = list_schedule_devices(devices=(device,))
        assert result[0].channel_address == ""

    def test_schedule_domain_none(self) -> None:
        """schedule_domain can be None (e.g. climate devices)."""
        wp_dp = _make_wp_dp(schedule_domain=None)
        device = _make_device(wp_dp=wp_dp)
        result = list_schedule_devices(devices=(device,))
        assert result[0].schedule_domain is None

    def test_skips_devices_without_schedule_support(self) -> None:
        """Devices without week_profile_data_point are excluded."""
        device = _make_device(wp_dp=None)
        result = list_schedule_devices(devices=(device,))
        assert result == []

    def test_uses_address_as_name_fallback(self) -> None:
        """When device.name is None, address is used as name."""
        wp_dp = _make_wp_dp()
        device = _make_device(name=None, wp_dp=wp_dp)
        result = list_schedule_devices(devices=(device,))
        assert result[0].name == "0001D3C98DD4B6"


# ---------------------------------------------------------------------------
# get_climate_schedule
# ---------------------------------------------------------------------------


class TestGetClimateSchedule:
    """Tests for get_climate_schedule."""

    @pytest.mark.asyncio
    async def test_defaults_min_max_temp(self) -> None:
        """When min_temp/max_temp are None, defaults are used."""
        wp_dp = _make_climate_wp_dp(min_temp=None, max_temp=None)
        device = _make_device(wp_dp=wp_dp)

        result = await get_climate_schedule(device=device)

        assert result.min_temp == 5.0
        assert result.max_temp == 30.5

    @pytest.mark.asyncio
    async def test_raises_for_device_without_schedule(self) -> None:
        """TypeError when device has no week_profile_data_point."""
        device = _make_device(wp_dp=None)

        with pytest.raises(TypeError, match="does not support climate schedules"):
            await get_climate_schedule(device=device)

    @pytest.mark.asyncio
    async def test_raises_for_non_climate_device(self) -> None:
        """TypeError when device has non-climate week profile."""
        wp_dp = _make_wp_dp()
        device = _make_device(wp_dp=wp_dp)

        with pytest.raises(TypeError, match="does not support climate schedules"):
            await get_climate_schedule(device=device)

    @pytest.mark.asyncio
    async def test_returns_climate_schedule_data(self) -> None:
        """Returns ClimateScheduleData with correct fields."""
        profile_data = {"MONDAY": [{"start": "06:00", "temp": 21.0}]}
        wp_dp = _make_climate_wp_dp(schedule_profile_data=profile_data)
        device = _make_device(wp_dp=wp_dp)

        result = await get_climate_schedule(device=device)

        assert isinstance(result, ClimateScheduleData)
        assert result.schedule_data == profile_data
        assert result.available_profiles == ["P1", "P2", "P3"]
        assert result.active_profile == "P1"
        assert result.device_active_profile_index == 1
        assert result.min_temp == 5.0
        assert result.max_temp == 30.5
        assert result.step == 0.5

    @pytest.mark.asyncio
    async def test_uses_current_profile_when_none(self) -> None:
        """When profile is None, current_schedule_profile is used."""
        wp_dp = _make_climate_wp_dp(current_schedule_profile=ScheduleProfile.P3)
        device = _make_device(wp_dp=wp_dp)

        await get_climate_schedule(device=device)

        wp_dp.get_schedule_profile.assert_awaited_once_with(
            profile=ScheduleProfile.P3,
            force_load=True,
        )

    @pytest.mark.asyncio
    async def test_with_explicit_profile(self) -> None:
        """Explicit profile parameter is passed through."""
        wp_dp = _make_climate_wp_dp()
        device = _make_device(wp_dp=wp_dp)

        await get_climate_schedule(device=device, profile="P2")

        wp_dp.get_schedule_profile.assert_awaited_once_with(
            profile=ScheduleProfile.P2,
            force_load=True,
        )


# ---------------------------------------------------------------------------
# set_climate_schedule_weekday
# ---------------------------------------------------------------------------


class TestSetClimateScheduleWeekday:
    """Tests for set_climate_schedule_weekday."""

    @pytest.mark.asyncio
    async def test_raises_for_non_climate_device(self) -> None:
        """TypeError when device has non-climate week profile."""
        wp_dp = _make_wp_dp()
        device = _make_device(wp_dp=wp_dp)

        with pytest.raises(TypeError, match="does not support climate schedules"):
            await set_climate_schedule_weekday(
                device=device,
                profile="P1",
                weekday="MONDAY",
                base_temperature=17.0,
                simple_weekday_list=[],
            )

    @pytest.mark.asyncio
    async def test_sets_weekday_data(self) -> None:
        """Correctly converts and passes weekday data."""
        wp_dp = _make_climate_wp_dp()
        device = _make_device(wp_dp=wp_dp)
        periods = [{"starttime": "06:00", "endtime": "08:00", "temperature": 21.0}]

        await set_climate_schedule_weekday(
            device=device,
            profile="P1",
            weekday="MONDAY",
            base_temperature=17.0,
            simple_weekday_list=periods,
        )

        wp_dp.set_schedule_weekday.assert_awaited_once()
        call_kwargs = wp_dp.set_schedule_weekday.call_args.kwargs
        assert call_kwargs["profile"] == ScheduleProfile.P1
        assert call_kwargs["weekday"].value == "MONDAY"


# ---------------------------------------------------------------------------
# set_climate_active_profile
# ---------------------------------------------------------------------------


class TestSetClimateActiveProfile:
    """Tests for set_climate_active_profile."""

    def test_raises_for_non_climate_device(self) -> None:
        """TypeError when device has non-climate week profile."""
        wp_dp = _make_wp_dp()
        device = _make_device(wp_dp=wp_dp)

        with pytest.raises(TypeError, match="does not support climate schedules"):
            set_climate_active_profile(device=device, profile="P1")

    def test_sets_active_profile(self) -> None:
        """Correctly sets the active profile."""
        wp_dp = _make_climate_wp_dp()
        device = _make_device(wp_dp=wp_dp)

        set_climate_active_profile(device=device, profile="P2")

        wp_dp.set_current_schedule_profile.assert_called_once_with(
            profile=ScheduleProfile.P2,
        )


# ---------------------------------------------------------------------------
# get_device_schedule
# ---------------------------------------------------------------------------


class TestGetDeviceSchedule:
    """Tests for get_device_schedule."""

    @pytest.mark.asyncio
    async def test_includes_schedule_enabled(self) -> None:
        """schedule_enabled is passed through from the data point."""
        enabled_map = {"ch1": True, "ch2": False}
        wp_dp = _make_wp_dp(schedule_enabled=enabled_map)
        device = _make_device(wp_dp=wp_dp)

        result = await get_device_schedule(device=device)

        assert result.schedule_enabled == {"ch1": True, "ch2": False}

    @pytest.mark.asyncio
    async def test_raises_for_device_without_schedule(self) -> None:
        """ValueError when device has no week_profile_data_point."""
        device = _make_device(wp_dp=None)

        with pytest.raises(ValueError, match="does not support schedules"):
            await get_device_schedule(device=device)

    @pytest.mark.asyncio
    async def test_returns_device_schedule_data(self) -> None:
        """Returns DeviceScheduleData with correct fields."""
        schedule = {"MONDAY": [{"start": "06:00", "channel": "ch1"}]}
        wp_dp = _make_wp_dp(schedule_data=schedule, max_entries=8, schedule_domain="light")
        device = _make_device(wp_dp=wp_dp)

        result = await get_device_schedule(device=device)

        assert isinstance(result, DeviceScheduleData)
        assert result.schedule_data == schedule
        assert result.max_entries == 8
        assert result.schedule_domain == "light"
        assert result.schedule_enabled is None
        assert result.supported_schedule_fields == []

    @pytest.mark.asyncio
    async def test_returns_supported_schedule_fields(self) -> None:
        """supported_schedule_fields are serialised as a sorted string list."""
        wp_dp = _make_wp_dp(
            supported_schedule_fields=frozenset({ScheduleField.WEEKDAY, ScheduleField.FIXED_HOUR, ScheduleField.LEVEL}),
        )
        device = _make_device(wp_dp=wp_dp)

        result = await get_device_schedule(device=device)

        # sorted alphabetically → ["FIXED_HOUR", "LEVEL", "WEEKDAY"]
        assert result.supported_schedule_fields == ["FIXED_HOUR", "LEVEL", "WEEKDAY"]


# ---------------------------------------------------------------------------
# set_device_schedule
# ---------------------------------------------------------------------------


class TestSetDeviceSchedule:
    """Tests for set_device_schedule."""

    @pytest.mark.asyncio
    async def test_raises_for_device_without_schedule(self) -> None:
        """ValueError when device has no week_profile_data_point."""
        device = _make_device(wp_dp=None)

        with pytest.raises(ValueError, match="does not support schedules"):
            await set_device_schedule(device=device, schedule_data={})

    @pytest.mark.asyncio
    async def test_sets_schedule_data(self) -> None:
        """Passes schedule data to the data point."""
        wp_dp = _make_wp_dp()
        device = _make_device(wp_dp=wp_dp)
        schedule = {"MONDAY": [{"start": "06:00", "channel": "ch1"}]}

        await set_device_schedule(device=device, schedule_data=schedule)

        wp_dp.set_schedule.assert_awaited_once_with(schedule_data=schedule)


# ---------------------------------------------------------------------------
# set_schedule_enabled
# ---------------------------------------------------------------------------


class TestSetScheduleEnabled:
    """Tests for set_schedule_enabled."""

    @pytest.mark.asyncio
    async def test_disables_schedule(self) -> None:
        """Calls set_schedule_enabled with enabled=False."""
        wp_dp = _make_wp_dp(schedule_enabled={"ch1": True})
        device = _make_device(wp_dp=wp_dp)

        await set_schedule_enabled(device=device, enabled=False)

        wp_dp.set_schedule_enabled.assert_awaited_once_with(enabled=False, channel_key=None)

    @pytest.mark.asyncio
    async def test_enables_schedule(self) -> None:
        """Calls set_schedule_enabled with enabled=True."""
        wp_dp = _make_wp_dp(schedule_enabled={"ch1": False})
        device = _make_device(wp_dp=wp_dp)

        await set_schedule_enabled(device=device, enabled=True)

        wp_dp.set_schedule_enabled.assert_awaited_once_with(enabled=True, channel_key=None)

    @pytest.mark.asyncio
    async def test_raises_for_device_without_schedule(self) -> None:
        """ValueError when device has no week_profile_data_point."""
        device = _make_device(wp_dp=None)

        with pytest.raises(ValueError, match="does not support schedules"):
            await set_schedule_enabled(device=device, enabled=True)

    @pytest.mark.asyncio
    async def test_raises_when_enable_disable_not_supported(self) -> None:
        """ValueError when schedule_enabled is None (feature not supported)."""
        wp_dp = _make_wp_dp(schedule_enabled=None)
        device = _make_device(wp_dp=wp_dp)

        with pytest.raises(ValueError, match="does not support schedule enable/disable"):
            await set_schedule_enabled(device=device, enabled=True)

    @pytest.mark.asyncio
    async def test_with_channel_key(self) -> None:
        """Passes channel_key through to the data point."""
        wp_dp = _make_wp_dp(schedule_enabled={"ch1": True, "ch2": False})
        device = _make_device(wp_dp=wp_dp)

        await set_schedule_enabled(device=device, enabled=True, channel_key="ch2")

        wp_dp.set_schedule_enabled.assert_awaited_once_with(enabled=True, channel_key="ch2")
