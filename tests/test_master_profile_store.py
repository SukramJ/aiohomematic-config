"""Tests for MASTER paramset easymode profile store."""

from unittest.mock import patch

from aiohomematic.easymode_data import ChannelMetadata, MasterProfileDef, ProfileParamConstraint, SenderTypeMetadata

from aiohomematic_config.master_profile_store import MasterProfileStore, ResolvedMasterProfile


def _make_channel_metadata(
    *,
    sender_type: str = "SENDER",
    profiles: tuple[MasterProfileDef, ...] = (),
) -> ChannelMetadata:
    """Create a ChannelMetadata with the given profiles."""
    return ChannelMetadata(
        channel_type="TEST_CHANNEL",
        sender_types={sender_type: SenderTypeMetadata(profiles=profiles)},
    )


def _fixed(value: int | float | str) -> ProfileParamConstraint:
    return ProfileParamConstraint(constraint_type="fixed", value=value)


def _range(
    *,
    default: int | float | None = None,
    min_value: int | float | None = None,
    max_value: int | float | None = None,
) -> ProfileParamConstraint:
    return ProfileParamConstraint(
        constraint_type="range",
        default=default,
        min_value=min_value,
        max_value=max_value,
    )


def _list_constraint(*values: int | float | str) -> ProfileParamConstraint:
    return ProfileParamConstraint(constraint_type="list", values=values)


class TestMasterProfileStoreGetProfiles:
    """Test MasterProfileStore.get_profiles()."""

    def test_returns_none_for_unknown_channel_type(self) -> None:
        store = MasterProfileStore()
        result = store.get_profiles(
            channel_type="NONEXISTENT_CHANNEL",
            sender_type="SENDER",
        )
        assert result is None

    def test_returns_none_for_unknown_sender_type(self) -> None:
        meta = _make_channel_metadata(
            sender_type="SENDER_A",
            profiles=(MasterProfileDef(id=1, name_key="Profile 1"),),
        )
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.get_profiles(
                channel_type="TEST_CHANNEL",
                sender_type="UNKNOWN_SENDER",
            )
        assert result is None

    def test_returns_none_when_no_profiles(self) -> None:
        meta = _make_channel_metadata(sender_type="SENDER", profiles=())
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.get_profiles(
                channel_type="TEST_CHANNEL",
                sender_type="SENDER",
            )
        assert result is None

    def test_returns_resolved_profiles(self) -> None:
        profiles = (
            MasterProfileDef(
                id=0,
                name_key="Expert",
                description="Expert mode",
                params={},
            ),
            MasterProfileDef(
                id=1,
                name_key="Standard",
                description="Standard mode",
                params={
                    "PARAM_A": _fixed(42),
                    "PARAM_B": _range(default=5, min_value=0, max_value=10),
                    "PARAM_C": _list_constraint(1, 2, 3),
                },
                visible_params=("PARAM_B",),
                hidden_params=("PARAM_A",),
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.get_profiles(
                channel_type="TEST_CHANNEL",
                sender_type="SENDER",
            )

        assert result is not None
        assert len(result) == 2

        expert = result[0]
        assert isinstance(expert, ResolvedMasterProfile)
        assert expert.id == 0
        assert expert.name == "Expert"
        assert expert.editable_params == []
        assert expert.fixed_params == {}

        standard = result[1]
        assert standard.id == 1
        assert standard.fixed_params == {"PARAM_A": 42}
        assert standard.editable_params == ["PARAM_B", "PARAM_C"]
        assert standard.default_values == {"PARAM_B": 5}
        assert standard.visible_params == ["PARAM_B"]
        assert standard.hidden_params == ["PARAM_A"]

    def test_visible_hidden_params_none_when_empty(self) -> None:
        profiles = (MasterProfileDef(id=1, name_key="Simple", params={}),)
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.get_profiles(
                channel_type="TEST_CHANNEL",
                sender_type="SENDER",
            )

        assert result is not None
        assert result[0].visible_params is None
        assert result[0].hidden_params is None


class TestMasterProfileStoreMatchActiveProfile:
    """Test MasterProfileStore.match_active_profile()."""

    def test_float_tolerance_matching(self) -> None:
        profiles = (
            MasterProfileDef(
                id=1,
                name_key="Float",
                params={"VAL": _fixed(1.0)},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            # int 1 should match float 1.0
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"VAL": 1},
            )
        assert result == 1

    def test_list_constraint_accepts_valid_value(self) -> None:
        profiles = (
            MasterProfileDef(
                id=1,
                name_key="Limited",
                params={"PARAM": _list_constraint(1, 2, 3)},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"PARAM": 2},
            )
        assert result == 1

    def test_list_constraint_rejects_invalid_value(self) -> None:
        profiles = (
            MasterProfileDef(
                id=1,
                name_key="Limited",
                params={"PARAM": _list_constraint(1, 2, 3)},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"PARAM": 99},
            )
        assert result == 0

    def test_matches_profile_with_fixed_constraints(self) -> None:
        profiles = (
            MasterProfileDef(id=0, name_key="Expert", params={}),
            MasterProfileDef(
                id=1,
                name_key="Standard",
                params={
                    "MODE": _fixed("AUTO"),
                    "LEVEL": _fixed(5),
                },
            ),
            MasterProfileDef(
                id=2,
                name_key="Manual",
                params={
                    "MODE": _fixed("MANUAL"),
                },
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            # Profile 1 matches (2 fixed constraints)
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"MODE": "AUTO", "LEVEL": 5},
            )
        assert result == 1

    def test_missing_current_value_skipped(self) -> None:
        """Parameters not in current_values should be skipped, not cause mismatch."""
        profiles = (
            MasterProfileDef(
                id=1,
                name_key="P1",
                params={"MISSING": _fixed(42)},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={},
            )
        # No fixed constraints matched (score=0), but also no mismatch
        # so it should still score 0, matching expert (best_score starts at -1)
        assert result == 1

    def test_most_specific_profile_wins(self) -> None:
        profiles = (
            MasterProfileDef(id=0, name_key="Expert", params={}),
            MasterProfileDef(
                id=1,
                name_key="Basic",
                params={"MODE": _fixed("AUTO")},
            ),
            MasterProfileDef(
                id=2,
                name_key="Advanced",
                params={
                    "MODE": _fixed("AUTO"),
                    "LEVEL": _fixed(10),
                },
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"MODE": "AUTO", "LEVEL": 10},
            )
        # Profile 2 has more fixed constraints matching
        assert result == 2

    def test_range_constraint_accepts_in_range(self) -> None:
        profiles = (
            MasterProfileDef(
                id=1,
                name_key="Ranged",
                params={"TEMP": _range(min_value=5.0, max_value=30.0)},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"TEMP": 20.0},
            )
        assert result == 1

    def test_range_constraint_rejects_above_max(self) -> None:
        profiles = (
            MasterProfileDef(
                id=1,
                name_key="Ranged",
                params={"TEMP": _range(min_value=5.0, max_value=30.0)},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"TEMP": 35.0},
            )
        assert result == 0

    def test_range_constraint_rejects_below_min(self) -> None:
        profiles = (
            MasterProfileDef(
                id=1,
                name_key="Ranged",
                params={"TEMP": _range(min_value=5.0, max_value=30.0)},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"TEMP": 3.0},
            )
        assert result == 0

    def test_returns_zero_for_unknown_channel(self) -> None:
        store = MasterProfileStore()
        result = store.match_active_profile(
            channel_type="NONEXISTENT",
            sender_type="SENDER",
            current_values={},
        )
        assert result == 0

    def test_returns_zero_for_unknown_sender(self) -> None:
        meta = _make_channel_metadata(
            sender_type="SENDER_A",
            profiles=(MasterProfileDef(id=1, name_key="P1"),),
        )
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="WRONG_SENDER",
                current_values={},
            )
        assert result == 0

    def test_returns_zero_when_no_profile_matches(self) -> None:
        profiles = (
            MasterProfileDef(id=0, name_key="Expert", params={}),
            MasterProfileDef(
                id=1,
                name_key="Standard",
                params={"MODE": _fixed("AUTO")},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"MODE": "MANUAL"},
            )
        assert result == 0

    def test_returns_zero_when_no_profiles(self) -> None:
        meta = _make_channel_metadata(sender_type="SENDER", profiles=())
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={},
            )
        assert result == 0

    def test_skips_profile_with_no_params(self) -> None:
        profiles = (
            MasterProfileDef(id=0, name_key="Expert", params={}),
            MasterProfileDef(id=1, name_key="Empty", params={}),
            MasterProfileDef(
                id=2,
                name_key="Real",
                params={"MODE": _fixed("ON")},
            ),
        )
        meta = _make_channel_metadata(sender_type="SENDER", profiles=profiles)
        with patch("aiohomematic_config.master_profile_store.get_channel_metadata", return_value=meta):
            store = MasterProfileStore()
            result = store.match_active_profile(
                channel_type="TEST",
                sender_type="SENDER",
                current_values={"MODE": "ON"},
            )
        assert result == 2
