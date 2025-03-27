import sys
from PyQt6.QtWidgets import QApplication

from TSA.sponsor.settings_manager import SettingsManager
from TSA.config import SETTINGS_PATH
from TSA.sponsor.init_logger import init_logger
from TSA.ui.main_ui import TSAController

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