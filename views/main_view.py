from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QStackedWidget,
    QCheckBox,
)
from PyQt6.QtCore import Qt
from views.table_view import TableView
from views.application_view import ApplicationView
from utils.ui_helpers import button_style


class MainView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_panel = None
        self.city_input = None
        self.org_input = None
        self.only_applications = None
        self.apply_filter_button = None

        self.application_view = ApplicationView()

        self.sponsor_table_view = None
        self.sponsor_table = None
        self.applications_table_all_view = None
        self.applications_table_all = None
        self.sponsor_navigation_layout = None
        self.sponsor_navigation_widget = None

        self.init_ui()

    def init_ui(self):
        self.top_layout_sponsor()
        self.table_sponsor()
        self.table_applications("all")
        self.bottom_layout_sponsor()

        # Sponsor Widget
        self.sponsor_widget = QWidget()
        sponsor_layout = QVBoxLayout()
        sponsor_layout.addWidget(self.filter_panel)
        sponsor_layout.addWidget(self.sponsor_table)
        sponsor_layout.addWidget(self.applications_table_all)
        self.applications_table_all.setVisible(False) # Hide by default
        sponsor_layout.addWidget(self.sponsor_navigation_widget)
        self.sponsor_widget.setLayout(sponsor_layout)

        # Stacked Widget: Screen Transition
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.sponsor_widget)
        self.stacked_widget.addWidget(self.application_view)

        # Main Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def top_layout_sponsor(self):
        self.filter_panel = QWidget()
        filter_layout = QHBoxLayout()
        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("Filter by Organisation")
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Filter by City")
        self.only_applications = QCheckBox("Applications")
        self.only_applications.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.apply_filter_button = QPushButton("Apply Filter")
        self.apply_filter_button.setStyleSheet(button_style("blue"))
        filter_layout.addWidget(QLabel("Organisation:"))
        filter_layout.addWidget(self.org_input)
        filter_layout.addWidget(QLabel("City:"))
        filter_layout.addWidget(self.city_input)
        filter_layout.addWidget(self.only_applications, 0)
        filter_layout.addWidget(self.apply_filter_button)
        self.filter_panel.setLayout(filter_layout)

    def table_sponsor(self):
        self.sponsor_table_view = TableView()
        self.sponsor_table_view.setup_main_table()
        self.sponsor_table = self.sponsor_table_view.table
        self.sponsor_table.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def table_applications(self, name=None):
        suffix = f"_{name}" if name else ""
        setattr(self, f"applications_table{suffix}_view", TableView())
        applications_table_view: TableView = getattr(
            self, f"applications_table{suffix}_view"
        )
        setattr(self, f"applications_table{suffix}", applications_table_view.table)

    def bottom_layout_sponsor(self):
        self.sponsor_navigation_layout = QHBoxLayout()
        self.sponsor_navigation_widget = QWidget()
        self.sponsor_navigation_widget.setLayout(self.sponsor_navigation_layout)

    def showEvent(self, event):
        super().showEvent(event)
        self.sponsor_table_view.adjust_main_column_widths(
            self.sponsor_table_view.table.width()
        )

    def show_applications_table(self, visible: bool):
        self.sponsor_table.setVisible(not visible)
        self.applications_table_all.setVisible(visible)
