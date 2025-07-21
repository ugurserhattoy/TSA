import sys
from PyQt6.QtWidgets import QApplication, QToolTip
from PyQt6.QtGui import QFont, QIcon
from config import SETTINGS_PATH, ICON_PATH
from models.settings_model import SettingsManager
from controllers.main_controller import TSAController
from utils.init_logger import init_logger


def main():
    settings_manager = SettingsManager(SETTINGS_PATH)
    log_level = settings_manager.get_log_level()
    rotation_limit = settings_manager.get_log_rotation_limit()
    init_logger(log_level, rotation_limit)

    app = QApplication(sys.argv)
    # app.setFont(QFont('', 14))
    app.setWindowIcon(QIcon(ICON_PATH))
    QToolTip.setFont(QFont("", 16))
    # app.setStyleSheet("QToolTip { font-size: 16px; color: #fff; background: #222; }")
    window = TSAController()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
