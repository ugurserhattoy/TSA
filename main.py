import sys

# import os
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from PyQt6.QtWidgets import QApplication, QToolTip
from PyQt6.QtGui import QFont
from config import SETTINGS_PATH
from models.settings_model import SettingsManager
from controllers.main_controller import TSAController
from utils.init_logger import init_logger

# print(sys.path)


def main():
    settings_manager = SettingsManager(SETTINGS_PATH)
    log_level = settings_manager.get_log_level()
    rotation_limit = settings_manager.get_log_rotation_limit()
    init_logger(log_level, rotation_limit)

    app = QApplication(sys.argv)
    # app.setFont(QFont('', 14))
    QToolTip.setFont(QFont("", 16))
    # app.setStyleSheet("QToolTip { font-size: 16px; color: #fff; background: #222; }")
    window = TSAController()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
