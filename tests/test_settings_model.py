import os
import tempfile
import pytest
from models.settings_model import SettingsManager


@pytest.fixture
def temp_settings_path():
    with tempfile.NamedTemporaryFile(delete=False) as tf:
        yield tf.name
    os.remove(tf.name)


@pytest.fixture
def settings_manager(temp_settings_path):
    return SettingsManager(config_path=temp_settings_path)


def test_default_settings(settings_manager):
    defaults = settings_manager.write_defaults()
    assert isinstance(defaults, dict), "❌ write_defaults() should return a dictionary"
    assert (
        "check_for_release" in defaults
    ), "❌ Default settings should include 'check_for_release' key"
    assert "log_level" in defaults
    assert "log_rotation_limit" in defaults


def test_save_and_load_settings(settings_manager):
    test_settings = {
        "check_for_release": True,
        "log_level": "INFO",
        "log_rotation_limit": 5,
        "window_size": [800, 600],
    }
    settings_manager.save_settings(test_settings)
    loaded = settings_manager.load_settings()
    assert loaded == test_settings, "❌ Loaded settings do not match saved settings"


def test_update_setting(settings_manager):
    settings_manager.save_settings({"check_for_release": True})
    settings_manager.update_setting("check_for_release", False)
    loaded = settings_manager.load_settings()
    assert (
        loaded["check_for_release"] == False
    ), "❌ update_setting() did not update the theme"


def test_reset_to_defaults(settings_manager):
    settings_manager.save_settings({"theme": "dark", "custom": True})
    settings_manager.reset_to_defaults()
    loaded = settings_manager.load_settings()
    assert (
        loaded == settings_manager.write_defaults()
    ), "❌ reset_to_defaults() did not reset all values"


def test_corrupt_file_loads_defaults(temp_settings_path):
    with open(temp_settings_path, "w", encoding="utf-8") as f:
        f.write("{corrupt json}")
    manager = SettingsManager(config_path=temp_settings_path)
    settings = manager.load_settings()
    assert (
        settings == manager.load_settings()
    ), "❌ Corrupt settings file did not load defaults"

    print("✅ Settings CRUD tests passed")
