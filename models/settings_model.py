import json
import os
import logging
from json import JSONDecodeError
from config import DEFAULT_SETTINGS


class SettingsManager:
    """
    Manages application settings, including reading and writing configuration options.
    Currently supports log rotation limit settings.
    """

    def __init__(self, config_path):
        self.config_path = config_path
        self.settings = self.load_settings()
        self.logger = logging.getLogger()

    def load_settings(self):
        """
        Load settings from a JSON file or create it with defaults if not found.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, JSONDecodeError) as err:
                self.logger.error("❌ JSON file not loaded: %s", err)
                raise

        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        default_copy = DEFAULT_SETTINGS.copy()
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(default_copy, f, indent=4)
        return default_copy
        # return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """
        Save the current settings to the JSON file.
        """
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)

    def get_check_for_release(self):
        """
        Get if auto check for release enabled
        """
        return self.settings.get(
            "check_for_release", DEFAULT_SETTINGS["check_for_release"]
        )

    def get_log_rotation_limit(self):
        """
        Get the configured log rotation limit.
        """
        return self.settings.get(
            "log_rotation_limit", DEFAULT_SETTINGS["log_rotation_limit"]
        )

    def get_log_level(self):
        """
        Get the configured log level.
        """
        return self.settings.get("log_level", DEFAULT_SETTINGS["log_level"])

    def set_check_for_release(self, auto_check):
        """
        Update auto check for release choice and update
        """
        self.settings["check_for_release"] = auto_check
        self.save_settings()

    def set_log_rotation_limit(self, limit):
        """
        Update the log rotation limit and save it.
        """
        self.settings["log_rotation_limit"] = limit
        self.save_settings()

    def set_log_level(self, level):
        """
        Update the log level and save it.
        """
        self.settings["log_level"] = level
        self.save_settings()
