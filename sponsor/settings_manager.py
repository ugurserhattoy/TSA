import json
import os

class SettingsManager:
    """
    Manages application settings, including reading and writing configuration options.
    Currently supports log rotation limit settings.
    """

    DEFAULT_SETTINGS = {
        "log_rotation_limit": 5,
        "log_level": "INFO"
    }

    def __init__(self, config_path):
        self.config_path = config_path
        self.settings = self.load_settings()

    def load_settings(self):
        """
        Load settings from a JSON file or use defaults if not found.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return self.DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """
        Save the current settings to the JSON file.
        """
        with open(self.config_path, "w") as f:
            json.dump(self.settings, f, indent=4)

    def get_log_rotation_limit(self):
        """
        Get the configured log rotation limit.
        """
        return self.settings.get("log_rotation_limit", self.DEFAULT_SETTINGS["log_rotation_limit"])

    def get_log_level(self):
        """
        Get the configured log level.
        """
        return self.settings.get("log_level", self.DEFAULT_SETTINGS["log_level"])

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