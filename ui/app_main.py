import sys
from PyQt6.QtWidgets import QApplication
from config import SETTINGS_PATH
from sponsor.settings_manager import SettingsManager
from sponsor.init_logger import init_logger
from ui.main_ui import TSAController


def main():
    settings_manager = SettingsManager(SETTINGS_PATH)
    log_level = settings_manager.get_log_level()
    rotation_limit = settings_manager.get_log_rotation_limit()
    init_logger(log_level, rotation_limit)

    app = QApplication(sys.argv)
    window = TSAController()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
