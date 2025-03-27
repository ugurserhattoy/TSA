"""
main_ui.py

This module serves as the Controller in the MVC architecture. It manages the main window of the application,
handles user interactions, coordinates data filtering, pagination, and updating the "applied" status via checkboxes.

Key Components:
- TableManager: Manages the display and structure of the data table
- DataManager: Handles database interactions
- NavigationManager: Manages pagination and result information display
- MenuManager: Controls menu-related actions and signals
- LogsViewer: Displays log file content in a separate window

The TSAController class is the main entry point, tying together UI initialization and application logic.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QHBoxLayout, QCheckBox, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
from TSA.ui.table_manager import TableManager
from TSA.ui.data_manager import DataManager
from TSA.ui.navigation_manager import NavigationManager
import logging
from TSA.config import DB_PATH
from TSA.ui.menu_manager import MenuManager
from TSA.ui.logs_viewer import LogsViewer

logger = logging.getLogger()

from PyQt6.QtWidgets import QMainWindow

class TSAController(QMainWindow):
    """
    Main controller class for the TSA application.

    Initializes the main window, sets up UI components, connects user interactions to logic,
    and handles loading and updating sponsor data.
    """
    def __init__(self):
        """
        Initializes the TSAController, sets up data and UI components.
        Establishes database connection and triggers the first data load.
        """
        # print("Database path:", DB_PATH)
        logger.info(f"DB Path: {DB_PATH}")
        super().__init__()
        self.data_manager = DataManager()
        self.conn = self.data_manager.prepare_database()
        self.data_manager.conn = self.conn
        # Initialize TableManager before UI
        self.table_manager = TableManager()
        
        self.initUI()
        self.load_data_page()  # Initial data load after UI setup

    def initUI(self):
        """
        Builds the main user interface: filter inputs, table display,
        navigation controls, and menu connections.
        """
        self.setWindowTitle("TSA - Track Sponsored Applications")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

        self.page_size = 50
        self.current_page = 0

        # Filter section
        self.filter_layout = QHBoxLayout()
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Filter by City")
        self.org_input = QLineEdit()
        self.org_input.setPlaceholderText("Filter by Organisation")
        self.filter_button = QPushButton("Apply Filter")
        self.filter_button.clicked.connect(self.apply_filter)

        self.filter_layout.addWidget(QLabel("City:"))
        self.filter_layout.addWidget(self.city_input)
        self.filter_layout.addWidget(QLabel("Organisation:"))
        self.filter_layout.addWidget(self.org_input)
        self.filter_layout.addWidget(self.filter_button)

        self.layout.addLayout(self.filter_layout)

        self.configure_table()

        # Navigation
        self.navigation_manager = NavigationManager(
            self.layout,
            # self.apply_filter,
            self.load_next_page,
            self.load_prev_page
        )

        # Menu
        self.menu_manager = MenuManager(self)
        self.menu_manager.logs_requested.connect(self.show_logs_viewer)
        # self.menu_manager.settings_requested.connect(self.show_settings_viewer)
        # self.menu_manager.help_requested.connect(self.show_help_viewer)

    def build_query(self):
        """
        Constructs the SQL query and parameters based on current filter inputs.

        Returns:
            - base_query (str): SELECT query with LIMIT/OFFSET
            - params (list): parameters for base_query
            - count_query (str): query for total result count
            - count_params (list): parameters for count_query
        """
        base_query = """
            SELECT organisation_name, town_city, county, type_and_rating, route, applied
            FROM sponsors
        """
        filters = []
        params = []

        city = self.city_input.text().strip()
        if city:
            if len(city) == 1:
                filters.append("LOWER(town_city) LIKE ?")
                params.append(f"{city.lower()}%")
            else:
                filters.append("LOWER(town_city) LIKE ?")
                params.append(f"%{city.lower()}%")

        org = self.org_input.text().strip()
        if org:
            if len(org) == 1:
                filters.append("LOWER(organisation_name) LIKE ?")
                params.append(f"{org.lower()}%")
            else:
                filters.append("LOWER(organisation_name) LIKE ?")
                params.append(f"%{org.lower()}%")

        if filters:
            base_query += " WHERE " + " AND ".join(filters)

        count_query = "SELECT COUNT(*) FROM sponsors"
        count_params = params.copy()
        if filters:
            count_query += " WHERE " + " AND ".join(filters)

        offset = self.current_page * self.page_size
        base_query += " LIMIT ? OFFSET ?"
        params.extend([self.page_size, offset])

        return base_query, params, count_query, count_params

    def configure_table(self):
        """
        Applies styling and layout configuration to the table widget.
        Adjusts headers and section sizes.
        """
        self.table_manager.table.verticalHeader().setVisible(True)
        self.table_manager.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_manager.table.setWordWrap(False)
        self.table_manager.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table_manager.table.verticalHeader().setDefaultSectionSize(24)
        self.table_manager.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.layout.addWidget(self.table_manager.table)

    def resizeEvent(self, event):
        """
        Handles window resize events to adjust column widths dynamically.
        """
        super().resizeEvent(event)
        self.table_manager.adjust_column_widths(self.table_manager.table.viewport().width())

    def apply_filter(self):
        self.current_page = 0
        self.load_data_page()

    def load_data_page(self):
        """
        Loads sponsor data for the current page and populates the table.

        Also sets checkbox states and attaches stateChanged handlers
        for each row's 'applied' field.
        """
        offset = self.current_page * self.page_size
        query, params, count_query, count_params = self.build_query()

        count_cursor = self.conn.cursor()
        count_cursor.execute(count_query, count_params)
        total_results = count_cursor.fetchone()[0]

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        # print("ROWS FETCHED:", rows)
        self.table_manager.table.setRowCount(len(rows))

        self.table_manager.table.setColumnCount(6)
        self.table_manager.table.setHorizontalHeaderLabels(["Organisation", "City", "County", "Type & Rating", "Route", "Applied"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data[:-1]):
                self.table_manager.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            checkbox = QCheckBox()
            checkbox.setChecked(bool(row_data[-1]))
            checkbox.stateChanged.connect(lambda state, row=row_idx: self.toggle_applied(row + offset, state))
            self.table_manager.table.setCellWidget(row_idx, 5, checkbox)

        page_info = f"Page {self.current_page + 1}"
        result_info = f"{total_results} results"
        logger.debug(f"Page info: {page_info}, Result info: {result_info}")
        self.navigation_manager.set_page_info(page_info)
        self.navigation_manager.set_result_info(result_info)

        for row_idx in range(len(rows)):
            item = self.table_manager.table.verticalHeaderItem(row_idx)
            if item is None:
                item = QTableWidgetItem()
                self.table_manager.table.setVerticalHeaderItem(row_idx, item)
            item.setText(str(offset + row_idx + 1))
        self.table_manager.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def load_next_page(self):
        self.current_page += 1
        self.load_data_page()

    def load_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data_page()

    def show_logs_viewer(self):
        self.logs_viewer = LogsViewer()
        self.logs_viewer.show()
        
    def toggle_applied(self, row_idx, state):
        """
        Triggered when a checkbox is toggled.

        Updates the 'applied' status of the corresponding sponsor in the database,
        based on the checkbox state.
        """
        # if not self.conn:
        #     print("[TOGGLE DEBUG] self.conn is None!")
        # else:
        #     print("[TOGGLE DEBUG] self.conn is VALID")

        org_item = self.table_manager.table.item(row_idx % self.page_size, 0)
        city_item = self.table_manager.table.item(row_idx % self.page_size, 1)
        print(f"org_item: {org_item} | city_item: {city_item}")

        print(f"[STATE DEBUG] Qt state: {int(state)} | interpreted as: {1 if state == Qt.CheckState.Checked.value else 0}")
        if org_item and city_item:
            organisation_name = org_item.text()
            city = city_item.text()

            print(f"org: {organisation_name} | city: {city}")
            current_status = 1 if state == Qt.CheckState.Checked.value else 0
            self.data_manager.toggle_applied(organisation_name, city, current_status)

            logger.info(f"Updated '{organisation_name}' to {'applied' if current_status else 'not applied'}")
