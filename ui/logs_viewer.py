import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton
from PyQt6.QtGui import QFont, QTextCursor
from config import LOG_FILE


class LogsViewer(QDialog):
    """
    Dialog window to display the application's log output.

    Features:
    - Displays logs from the configured log file.
    - Refresh button to reload log content.
    - Automatically scrolls to the bottom on load.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs Viewer")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 11))
        layout.addWidget(self.log_text)

        self.refresh_button = QPushButton("Refresh Logs")
        self.refresh_button.clicked.connect(self.load_logs)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)
        self.load_logs()

    def load_logs(self):
        """
        Loads and displays the contents of the log file in the text area.
        Scrolls to the bottom after loading.
        Displays an error if log file cannot be read.
        """
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = f.read()
                    self.log_text.setPlainText(logs)
                    self.log_text.moveCursor(QTextCursor.MoveOperation.End)
            except IOError as err:
                self.display_error_message(f"Failed to read log file:\n{err}")
        else:
            self.display_error_message("No log file found.")

    def display_error_message(self, message: str):
        """
        Displays the given error message in the log view text area.
        """
        self.log_text.setPlainText(message)
