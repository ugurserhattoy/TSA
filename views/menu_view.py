"""
This module defines the MenuManager class,
which handles the creation of the application's menu bar and its menus,
including tools, settings, help, and about.
It also defines signals for handling menu item interactions.
"""

from PyQt6.QtWidgets import (
    QMenuBar, QMenu, QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QObject, pyqtSignal
from utils.menu_utils import read_md_file_to_html


class MenuManager(QObject):
    """
    Manages the menu bar and its menus in the application.

    Signals:
        logs_requested: Emitted when the Logs menu item is selected.
        settings_requested: Placeholder signal for future Settings menu interaction.
        help_requested: Placeholder signal for future Help menu interaction.
        about_requested: Placeholder signal for future About menu interaction.
    """

    logs_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    help_requested = pyqtSignal()
    about_requested = pyqtSignal()

    def __init__(self, parent):
        """
        Initializes the MenuManager with the parent widget and sets up the menu bar.
        """
        super().__init__()
        self.parent = parent
        self.menu_bar = QMenuBar()
        self.create_menus()

    def create_menus(self):
        """
        Creates and attaches all top-level menus to the menu bar.
        """
        self.create_tools_menu()
        self.create_settings_menu()
        self.create_help_menu()  # Placeholder for future use
        self.create_about_menu()  # Placeholder for future use

        self.parent.setMenuBar(self.menu_bar)
        print(
            "[DEBUG] FINAL MENU HEADERS:",
            [action.text() for action in self.menu_bar.actions()],
        )

    def create_tools_menu(self):
        """
        Creates the Tools menu and connects the Logs action to its signal.
        """
        tools_menu = QMenu("Tools", self.parent)
        view_logs_action = QAction("Logs", self.parent)
        view_logs_action.triggered.connect(self.logs_requested.emit)
        tools_menu.addAction(view_logs_action)
        self.menu_bar.addMenu(tools_menu)

    def create_settings_menu(self):
        """
        Creates the Settings menu with a placeholder action.
        """
        settings_menu = QMenu("Settings", self.parent)
        settings_action = QAction("Settings", self.parent)
        settings_action.triggered.connect(self.settings_requested.emit)
        settings_menu.addAction(settings_action)
        self.menu_bar.addMenu(settings_menu)
        print(
            "[DEBUG] Added Settings menu:",
            [action.text() for action in self.menu_bar.actions()],
        )
        print("MENU OBJECT:", settings_menu.title(), "| OBJ TYPE:", type(settings_menu))
        print("[DEBUG] Settings menu created:", settings_menu.title())

    def create_help_menu(self):
        """
        Creates the Help menu with a placeholder action.
        """
        help_menu = QMenu("Help", self.parent)
        placeholder = QAction("Coming soon...", self.parent)
        placeholder.setEnabled(False)
        help_menu.addAction(placeholder)
        self.menu_bar.addMenu(help_menu)

    def create_about_menu(self):
        """
        Creates the About menu with a placeholder action.
        """
        about_menu = QMenu("About", self.parent)
        about_action = QAction("About This App", self.parent)
        about_action.setEnabled(False)
        about_menu.addAction(about_action)

        user_agreement_action = QAction("User Agreement", self.parent)
        user_agreement_action.triggered.connect(
            lambda: self.show_md_dialog("data/user_agreement.md", "User Agreement")
        )
        about_menu.addAction(user_agreement_action)
        self.menu_bar.addMenu(about_menu)

    def show_md_dialog(self, file_path, title):
        html = read_md_file_to_html(file_path)
        dlg = QDialog(self.parent)
        dlg.setWindowTitle(title)
        layout = QVBoxLayout()
        # label = QLabel("<b>User Agreement</b>")
        # layout.addWidget(label)
        _text = QTextEdit()
        _text.setReadOnly(True)
        _text.setHtml(html)
        layout.addWidget(_text)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.resize(800, 600)
        dlg.setLayout(layout)
        dlg.exec()
