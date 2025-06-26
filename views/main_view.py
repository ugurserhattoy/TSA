from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel,
    QTableWidget, QStackedWidget, QSpacerItem, QSizePolicy
)
from views.table_view import TableView
from utils.ui_helpers import button_style

class MainView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # --- Top Layout: Filter Panel ---
        self.filter_panel = QWidget()
        filter_layout = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Filter by City")
        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("Filter by Organisation")
        self.apply_filter_button = QPushButton("Apply Filter")
        self.apply_filter_button.setStyleSheet(button_style("blue"))
        filter_layout.addWidget(QLabel("City:"))
        filter_layout.addWidget(self.city_input)
        filter_layout.addWidget(QLabel("Organisation:"))
        filter_layout.addWidget(self.org_input)
        filter_layout.addWidget(self.apply_filter_button)
        self.filter_panel.setLayout(filter_layout)

        # --- Top Layout: Applications Panel ---
        self.actions_panel = QWidget()
        actions_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet(button_style())
        self.edit_button = QPushButton("Edit")
        self.edit_button.setStyleSheet(button_style("lblue"))
        self.add_new_button = QPushButton("Add New")
        self.add_new_button.setStyleSheet(button_style("blue"))
        actions_layout.addWidget(self.back_button)
        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.add_new_button)
        self.actions_panel.setLayout(actions_layout)
        self.actions_panel.hide()  # Default hidden

        # --- Table: Sponsor Table ---
        self.sponsor_table_view = TableView()
        self.sponsor_table_view.setup_main_table()
        self.sponsor_table = self.sponsor_table_view.table

        # --- Table: Applications ---
        self.applications_table_view = TableView()
        self.applications_table = self.applications_table_view.table

        # --- Sponsor Navigation Layout ---
        self.sponsor_navigation_layout = QHBoxLayout()
        self.sponsor_navigation_widget = QWidget()
        self.sponsor_navigation_widget.setLayout(self.sponsor_navigation_layout)

        # --- Applications Bottom Layout ---
        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(button_style("red", 150))
        self.delete_button.hide()  # Hidden

        # --- Applications Navigation Layout ---
        self.applications_navigation_layout = QHBoxLayout()
        self.applications_navigation_widget = QWidget()
        self.applications_navigation_widget.setLayout(self.applications_navigation_layout)
        self.applications_navigation_layout.addStretch()
        self.applications_navigation_layout.addWidget(self.delete_button)
        self.applications_navigation_layout.addStretch()

        # --- Sponsor Widget ---
        self.sponsor_widget = QWidget()
        sponsor_layout = QVBoxLayout()
        sponsor_layout.addWidget(self.sponsor_table)
        sponsor_layout.addWidget(self.sponsor_navigation_widget)
        self.sponsor_widget.setLayout(sponsor_layout)

        # --- Applications Widget ---
        self.applications_widget = QWidget()
        applications_layout = QVBoxLayout()
        applications_layout.addWidget(self.applications_table)
        applications_layout.addWidget(self.applications_navigation_widget)
        self.applications_widget.setLayout(applications_layout)

        # --- Stacked Widget: Screen Transition ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.sponsor_widget)
        self.stacked_widget.addWidget(self.applications_widget)
        # 0: sponsor_widget, 1: applications_widget

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.filter_panel)
        main_layout.addWidget(self.actions_panel)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def set_applications_mode(self, enabled):
        if enabled:
            self.filter_panel.hide()
            self.actions_panel.show()
            self.delete_button.show()
        else:
            self.filter_panel.show()
            self.actions_panel.hide()
            self.delete_button.hide()
    