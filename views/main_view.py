from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QStackedWidget,
)
from PyQt6.QtCore import Qt
from views.table_view import TableView
from utils.ui_helpers import button_style


class MainView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_panel = None
        self.city_input = None
        self.org_input = None
        self.apply_filter_button = None
        self.actions_panel = None
        self.back_button = None
        self.edit_button = None
        self.add_new_button = None
        self.sponsor_table_view = None
        self.sponsor_table = None
        self.applications_table_view = None
        self.applications_table = None
        self.sponsor_navigation_layout = None
        self.sponsor_navigation_widget = None
        self.applications_navigation_widget = None
        self.delete_button = None
        self.init_ui()

    def init_ui(self):
        self.top_layout_sponsor()
        self.top_layout_applications()
        self.table_sponsor()
        self.table_applications()
        self.bottom_layout_sponsor()
        self.bottom_layout_applications()

        # --- Sponsor Widget ---
        self.sponsor_widget = QWidget()
        sponsor_layout = QVBoxLayout()
        sponsor_layout.addWidget(self.filter_panel)
        sponsor_layout.addWidget(self.sponsor_table)
        sponsor_layout.addWidget(self.sponsor_navigation_widget)
        self.sponsor_widget.setLayout(sponsor_layout)

        # --- Applications Widget ---
        self.applications_widget = QWidget()
        applications_layout = QVBoxLayout()
        applications_layout.addWidget(self.actions_panel)
        applications_layout.addWidget(self.applications_table)
        applications_layout.addWidget(self.applications_navigation_widget)
        self.applications_widget.setLayout(applications_layout)

        # --- Stacked Widget: Screen Transition ---
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.sponsor_widget)
        self.stacked_widget.addWidget(self.applications_widget)

        # --- Main Layout ---
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def top_layout_sponsor(self):
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

    def top_layout_applications(self):
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

    def table_sponsor(self):
        self.sponsor_table_view = TableView()
        self.sponsor_table_view.setup_main_table()
        self.sponsor_table = self.sponsor_table_view.table
        self.sponsor_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def table_applications(self):
        self.applications_table_view = TableView()
        self.applications_table = self.applications_table_view.table

    def bottom_layout_sponsor(self):
        self.sponsor_navigation_layout = QHBoxLayout()
        self.sponsor_navigation_widget = QWidget()
        self.sponsor_navigation_widget.setLayout(self.sponsor_navigation_layout)

    def bottom_layout_applications(self):
        applications_navigation_layout = QHBoxLayout()
        self.applications_navigation_widget = QWidget()
        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(button_style("red", 150))
        self.applications_navigation_widget.setLayout(applications_navigation_layout)
        applications_navigation_layout.addStretch()
        applications_navigation_layout.addWidget(self.delete_button)
        applications_navigation_layout.addStretch()

    def showEvent(self, event):
        super().showEvent(event)
        # Set table to width
        self.sponsor_table_view.adjust_main_column_widths(
            self.sponsor_table_view.table.width()
        )
