import sys
# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from PyQt6.QtWidgets import QApplication
from config import SETTINGS_PATH
from models.settings_model import SettingsManager
from utils.init_logger import init_logger
from controllers.main_controller import TSAController

# print(sys.path)

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
