"""Tests for the ProfileStore."""

from __future__ import annotations

import pytest

from aiohomematic_config import ProfileStore


@pytest.fixture
def store() -> ProfileStore:
    """Return a fresh ProfileStore instance."""
    return ProfileStore()


class TestGetProfiles:
    """Tests for ProfileStore.get_profiles."""

    async def test_caching(self, store: ProfileStore) -> None:
        """Test that repeated calls use cached data."""
        profiles1 = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
        )
        profiles2 = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
        )
        assert profiles1 is not None
        assert profiles2 is not None
        assert len(profiles1) == len(profiles2)

    async def test_default_values_from_range(self, store: ProfileStore) -> None:
        """Test that default values are set from range constraints."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
        )
        assert profiles is not None
        dimmer_on = next((p for p in profiles if p.id == 1), None)
        assert dimmer_on is not None
        assert dimmer_on.default_values["SHORT_ON_LEVEL"] == 1.0
        assert dimmer_on.default_values["LONG_DIM_MAX_LEVEL"] == 1.0

    async def test_editable_params_only_range(self, store: ProfileStore) -> None:
        """Test that only range constraints appear in editable_params."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
        )
        assert profiles is not None
        dimmer_on = next((p for p in profiles if p.id == 1), None)
        assert dimmer_on is not None
        # Range params should be editable
        assert "SHORT_ON_LEVEL" in dimmer_on.editable_params
        assert "LONG_DIM_MAX_LEVEL" in dimmer_on.editable_params
        # Fixed params should NOT be in editable
        assert "SHORT_PROFILE_ACTION_TYPE" not in dimmer_on.editable_params
        assert "SHORT_JT_ON" not in dimmer_on.editable_params

    async def test_expert_profile_has_empty_params(self, store: ProfileStore) -> None:
        """Test that expert profile (id=0) has no editable/fixed params."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
        )
        assert profiles is not None
        expert = next((p for p in profiles if p.id == 0), None)
        assert expert is not None
        assert expert.editable_params == []
        assert expert.fixed_params == {}
        assert expert.default_values == {}

    async def test_fixed_params_set_correctly(self, store: ProfileStore) -> None:
        """Test that fixed constraints appear in fixed_params."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
        )
        assert profiles is not None
        dimmer_on = next((p for p in profiles if p.id == 1), None)
        assert dimmer_on is not None
        assert dimmer_on.fixed_params["SHORT_PROFILE_ACTION_TYPE"] == 1.0
        assert dimmer_on.fixed_params["SHORT_JT_ON"] == 3.0
        assert dimmer_on.fixed_params["LONG_PROFILE_ACTION_TYPE"] == 3.0

    async def test_get_profiles_locale_fallback(self, store: ProfileStore) -> None:
        """Test that unknown locale falls back to English."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
            locale="fr",
        )
        assert profiles is not None
        dimmer_on = next((p for p in profiles if p.id == 1), None)
        assert dimmer_on is not None
        # Falls back to English
        assert dimmer_on.name == "Dimmer - on"

    async def test_get_profiles_resolved_locale_de(self, store: ProfileStore) -> None:
        """Test that profiles resolve with German labels."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
            locale="de",
        )
        assert profiles is not None
        dimmer_on = next((p for p in profiles if p.id == 1), None)
        assert dimmer_on is not None
        assert dimmer_on.name == "Dimmer - ein"

    async def test_get_profiles_resolved_locale_en(self, store: ProfileStore) -> None:
        """Test that profiles resolve with English labels."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
            locale="en",
        )
        assert profiles is not None
        dimmer_on = next((p for p in profiles if p.id == 1), None)
        assert dimmer_on is not None
        assert dimmer_on.name == "Dimmer - on"
        assert "brightness" in dimmer_on.description.lower()

    async def test_load_existing_receiver_type(self, store: ProfileStore) -> None:
        """Test that profiles are loaded for a known receiver/sender pair."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
        )
        assert profiles is not None
        assert len(profiles) >= 2
        # First profile should be Expert (id=0)
        assert profiles[0].id == 0
        assert profiles[0].name == "Expert"

    async def test_load_nonexistent_receiver_type(self, store: ProfileStore) -> None:
        """Test that None is returned for unknown receiver types."""
        profiles = await store.get_profiles(
            receiver_channel_type="NONEXISTENT_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
        )
        assert profiles is None

    async def test_load_nonexistent_sender_type(self, store: ProfileStore) -> None:
        """Test that None is returned for unknown sender types."""
        profiles = await store.get_profiles(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="NONEXISTENT_SENDER",
        )
        assert profiles is None


class TestMatchActiveProfile:
    """Tests for ProfileStore.match_active_profile."""

    async def test_match_active_profile_dimmer_on(self, store: ProfileStore) -> None:
        """Test matching 'Dimmer - on' profile correctly."""
        # Provide all fixed params from profile 1 so matching succeeds
        values = {
            "SHORT_PROFILE_ACTION_TYPE": 1.0,
            "SHORT_JT_ON": 3.0,
            "SHORT_JT_OFF": 1.0,
            "SHORT_JT_OFFDELAY": 3.0,
            "SHORT_JT_ONDELAY": 1.0,
            "SHORT_JT_RAMPOFF": 2.0,
            "SHORT_JT_RAMPON": 2.0,
            "LONG_PROFILE_ACTION_TYPE": 3.0,
            "LONG_JT_ON": 3.0,
            "LONG_JT_OFF": 1.0,
            "LONG_JT_OFFDELAY": 3.0,
            "LONG_JT_ONDELAY": 1.0,
            "LONG_JT_RAMPOFF": 2.0,
            "LONG_JT_RAMPON": 2.0,
            "LONG_MULTIEXECUTE": 1.0,
        }
        result = await store.match_active_profile(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
            current_values=values,
        )
        assert result == 1

    async def test_match_active_profile_expert_fallback(self, store: ProfileStore) -> None:
        """Test that unknown value combinations fall back to Expert (0)."""
        values = {
            "SHORT_PROFILE_ACTION_TYPE": 99,
            "LONG_PROFILE_ACTION_TYPE": 99,
        }
        result = await store.match_active_profile(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
            current_values=values,
        )
        assert result == 0

    async def test_match_active_profile_not_active(self, store: ProfileStore) -> None:
        """Test matching 'inactive' profile (action_type=0)."""
        values = {
            "SHORT_PROFILE_ACTION_TYPE": 0.0,
            "LONG_PROFILE_ACTION_TYPE": 0.0,
        }
        result = await store.match_active_profile(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
            current_values=values,
        )
        # Profile 5 is "inactive" in the real parsed data
        assert result == 5

    async def test_match_profile_dimmer_off(self, store: ProfileStore) -> None:
        """Test matching 'Dimmer - off' profile."""
        # Profile 2 has SHORT_PROFILE_ACTION_TYPE=1 like profile 1,
        # but different JT values (JT_OFF=6 vs 1, JT_ON=4 vs 3, etc.)
        values = {
            "SHORT_PROFILE_ACTION_TYPE": 1.0,
            "SHORT_JT_ON": 4.0,
            "SHORT_JT_OFF": 6.0,
            "SHORT_JT_OFFDELAY": 5.0,
            "SHORT_JT_ONDELAY": 6.0,
            "SHORT_JT_RAMPOFF": 6.0,
            "SHORT_JT_RAMPON": 4.0,
            "LONG_PROFILE_ACTION_TYPE": 4.0,
            "LONG_JT_ON": 4.0,
            "LONG_JT_OFF": 6.0,
            "LONG_JT_OFFDELAY": 5.0,
            "LONG_JT_ONDELAY": 6.0,
            "LONG_JT_RAMPOFF": 6.0,
            "LONG_JT_RAMPON": 4.0,
            "LONG_MULTIEXECUTE": 1.0,
        }
        result = await store.match_active_profile(
            receiver_channel_type="DIMMER_VIRTUAL_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
            current_values=values,
        )
        assert result == 2

    async def test_match_unknown_receiver_returns_expert(self, store: ProfileStore) -> None:
        """Test that unknown receiver types return Expert (0)."""
        result = await store.match_active_profile(
            receiver_channel_type="NONEXISTENT_RECEIVER",
            sender_channel_type="SWITCH_TRANSCEIVER",
            current_values={"FOO": 1},
        )
        assert result == 0
