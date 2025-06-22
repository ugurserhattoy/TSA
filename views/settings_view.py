from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QComboBox,
    QSpinBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QCheckBox,
)
from PyQt6.QtCore import pyqtSignal


class SettingsUI(QWidget):
    settings_saved = pyqtSignal(str, int, bool)

    # log_level, rotation_limit, update_check
    def __init__(
        self,
        current_log_level: str,
        current_rotation_limit: int,
        current_update_check: bool,
    ):
        super().__init__()
        self.setWindowTitle("Settings")

        # Log Level
        self.log_level_label = QLabel("Log Level:")
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        if current_log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            self.log_level_combo.setCurrentText(current_log_level)

        # Rotation Limit
        self.rotation_label = QLabel("Log Rotation Limit:")
        self.rotation_spin = QSpinBox()
        self.rotation_spin.setRange(1, 20)
        self.rotation_spin.setValue(current_rotation_limit)

        # Update Check
        self.update_check_box = QCheckBox("Check for updates on startup")
        self.update_check_box.setChecked(current_update_check)

        # Buttons
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button.clicked.connect(self.close)

        # Layout
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.log_level_label)
        form_layout.addWidget(self.log_level_combo)
        form_layout.addWidget(self.rotation_label)
        form_layout.addWidget(self.rotation_spin)
        form_layout.addWidget(self.update_check_box)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        form_layout.addLayout(button_layout)

        self.setLayout(form_layout)

    def save_settings(self):
        log_level = self.log_level_combo.currentText()
        rotation_limit = self.rotation_spin.value()
        auto_update_check = self.update_check_box.isChecked()
        self.settings_saved.emit(log_level, rotation_limit, auto_update_check)
        QMessageBox.information(
            self, "Settings Saved", "Settings have been saved successfully."
        )
        self.close()
