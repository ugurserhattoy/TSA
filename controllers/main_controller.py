"""
main_ui.py

This module serves as the Controller in the MVC architecture.
It manages the main window of the application, handles user interactions,
coordinates data filtering, pagination and
updating the "applied" status via checkboxes.

Key Components:
- TableView: Manages the display and structure of the data table
- DataManager: Handles database interactions
- NavigationManager: Manages pagination and result information display
- MenuManager: Controls menu-related actions and signals
- LogsViewer: Displays log file content in a separate window

The TSAController class is the main entry point,
tying together UI initialization and application logic.
"""

import platform
import logging
# from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QShortcut, QColor, QBrush
from PyQt6.QtWidgets import (
    QMainWindow,
    QTableWidgetItem,
    QHeaderView,
)
from config import DB_PATH, SETTINGS_PATH, VERSION, RES_SETTINGS
from models.settings_model import SettingsManager
from views.main_view import MainView
# from views.table_view import TableView
from views.navigation_view import NavigationManager
from views.menu_view import MenuManager
from views.logs_viewer import LogsViewer
from views.settings_view import SettingsUI
from views.update_view import UpdateView
from controllers.data_controller import DataManager
from utils.update_checker import fetch_latest_release


logger = logging.getLogger()


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
        logger.info("DB Path: %s", DB_PATH)
        super().__init__()
        self.setWindowTitle("TSA - Track Sponsored Applications")
        self.setGeometry(*RES_SETTINGS)
        self.data_manager = DataManager()
        self.conn = self.data_manager.prepare_database()
        self.data_manager.conn = self.conn

        # Initialize SettingsManager
        self.settings = SettingsManager(SETTINGS_PATH)

        self.logs_viewer = None
        self.settings_ui = None
        self.current_page = 0

        self.view = MainView()
        self.setCentralWidget(self.view)

        self.page_size = 50

        # Connect filter inputs and button
        self.view.city_input.returnPressed.connect(self.apply_filter)
        self.view.org_input.returnPressed.connect(self.apply_filter)
        self.view.apply_filter_button.clicked.connect(self.apply_filter)
        self.view.sponsor_table.cellDoubleClicked.connect(self.open_applications_view)

        self.configure_table()

        # Navigation
        self.navigation_manager = NavigationManager(
            self.view.sponsor_navigation_layout,
            # self.apply_filter,
            self.load_next_page,
            self.load_prev_page,
        )

        # Menu
        self.menu_manager = MenuManager(self)
        self.menu_manager.logs_requested.connect(self.show_logs_viewer)
        self.menu_manager.settings_requested.connect(self.show_settings_ui)
        # self.menu_manager.help_requested.connect(self.show_help_viewer)

        # Keyboard shortcuts for pagination
        platform_name = platform.system()

        if platform_name == "Darwin":  # macOS
            prev_shortcut = QShortcut(QKeySequence("Meta+B"), self.view)
            next_shortcut = QShortcut(QKeySequence("Meta+N"), self.view)
        else:  # Windows or Linux
            prev_shortcut = QShortcut(QKeySequence("Alt+B"), self.view)
            next_shortcut = QShortcut(QKeySequence("Alt+N"), self.view)

        prev_shortcut.activated.connect(self.load_prev_page)
        next_shortcut.activated.connect(self.load_next_page)
        # Applications organisation city pair
        self.application_pairs: set = self.data_manager.get_applications_pairs()

        self.load_data_page()  # Initial data load after UI setup

        # Release check
        if self.settings.get_check_for_release():
            self.check_for_release()
        

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
            SELECT organisation_name, town_city, county, type_and_rating, route
            FROM sponsors
        """
        filters = []
        params = []

        city = self.view.city_input.text().strip()
        if city:
            if len(city) == 1:
                filters.append("LOWER(town_city) LIKE ?")
                params.append(f"{city.lower()}%")
            else:
                filters.append("LOWER(town_city) LIKE ?")
                params.append(f"%{city.lower()}%")

        org = self.view.org_input.text().strip()
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
        self.view.stacked_widget.setCurrentWidget(self.view.sponsor_widget)

    def resizeEvent(self, event):
        """
        Handles window resize events to adjust column widths dynamically.
        """
        super().resizeEvent(event)
        self.adjust_main_col_widths()
        self.adjust_applications_col_widths()
    
    def adjust_main_col_widths(self):
        self.view.sponsor_table_view.adjust_main_column_widths(
            self.view.sponsor_table.viewport().width()
        )

    def adjust_applications_col_widths(self):
        self.view.applications_table_view.adjust_applications_column_widths(
            self.view.applications_table.viewport().width()
        )

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
        self.view.sponsor_table.setRowCount(len(rows))

        self.view.sponsor_table.setColumnCount(5)
        self.view.sponsor_table.setHorizontalHeaderLabels(
            ["Organisation", "City", "County", "Type & Rating", "Route"]
        )

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                if len(str(value)) > 16:
                    item.setToolTip(str(value))
                self.view.sponsor_table.setItem(row_idx, col_idx, item)

        self.highlight_applied_rows()

        page_info = f"Page {self.current_page + 1}"
        result_info = f"{total_results} results"
        logger.debug("Page info: %s, Result info: %s", page_info, result_info)
        self.navigation_manager.set_page_info(page_info)
        self.navigation_manager.set_result_info(result_info)

        for row_idx in range(len(rows)):
            item = self.view.sponsor_table.verticalHeaderItem(row_idx)
            if item is None:
                item = QTableWidgetItem()
                self.view.sponsor_table.setVerticalHeaderItem(row_idx, item)
            item.setText(str(offset + row_idx + 1))
        self.view.sponsor_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )

    def highlight_applied_rows(self):
        for row_idx in range(self.view.sponsor_table.rowCount()):
            org_item = self.view.sponsor_table.item(row_idx, 0)
            city_item = self.view.sponsor_table.item(row_idx, 1)
            if not org_item or not city_item:
                continue
            org = org_item.text()
            city = city_item.text()
            if (org, city) in self.application_pairs: # Applied
                color = "#2A4520" if row_idx % 2 == 0 else "#49693C"
                for col in range(self.view.sponsor_table.columnCount()):
                    item = self.view.sponsor_table.item(row_idx, col)
                    if item:
                        item.setBackground(QColor(color))
            else: # Default
                for col in range(self.view.sponsor_table.columnCount()):
                    item = self.view.sponsor_table.item(row_idx, col)
                    if item:
                        item.setBackground(QBrush())

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
    
    def open_applications_view(self, row, col):
        self.current_org_row = row
        self.current_org_col = col
        org_item = self.view.sponsor_table.item(row, 0)
        city_item = self.view.sponsor_table.item(row, 1)
        if org_item and city_item:
            self.current_organisation_name = org_item.text()
            self.current_city = city_item.text()
            # print(f"Applications for {organisation_name} ({city})")  # !TEST
            # TableView’s applications table setup func
            self.view.set_applications_mode(True)
            self.view.applications_table_view.setup_applications_table()
            # Run query to parse applications
            applications = self.data_manager.get_applications(
                self.current_organisation_name,
                self.current_city
            )
            self.view.applications_table_view.table.setRowCount(len(applications))
            # app_row = (id, organisation, city, role, date, contact, note)
            for row_idx, app_row in enumerate(applications):
                for col_idx, value in enumerate(app_row):
                    item = QTableWidgetItem(str(value))
                    self.view.applications_table_view.table.setItem(row_idx, col_idx, item)

            # Set applications widget as current
            self.view.stacked_widget.setCurrentWidget(self.view.applications_widget)
            self.adjust_applications_col_widths()

            # Connect back button
            try:
                self.view.back_button.clicked.disconnect()
                self.view.edit_button.clicked.disconnect()
                self.view.add_new_button.clicked.disconnect()
                self.view.delete_button.clicked.disconnect()
                self.view.applications_table_view.table.cellDoubleClicked.disconnect()
            except TypeError:
                pass
            self.view.back_button.clicked.connect(self.app_back_button_clicked)
            self.view.add_new_button.clicked.connect(self.add_application)
            self.view.edit_button.clicked.connect(self.edit_application)
            self.view.delete_button.clicked.connect(self.delete_application)
            self.view.applications_table_view.table.cellDoubleClicked.connect(self.edit_application)

    def show_sponsor_table(self):
        """Shows main table screen"""
        self.view.stacked_widget.setCurrentIndex(0)
        self.highlight_applied_rows()

    def app_back_button_clicked(self):
        self.show_sponsor_table()
        self.adjust_main_col_widths()
    
    def add_application(self):
        """
        Opens a dialog to add a new application for the selected organisation.
        """
        org = self.current_organisation_name
        city = self.current_city

        # ApplicationFormView adlı dialog açılacak
        from views.application_form_view import ApplicationFormView
        dialog = ApplicationFormView(org, city)
        if dialog.exec():
            data = dialog.get_form_data()
            self.data_manager.add_application(org, city, **data)
            self.application_pairs.add((org, city))
            self.open_applications_view(self.current_org_row, self.current_org_col)

    def edit_application(self):
        """Opens a dialog to edit the selected application entry."""
        selected_row = self.view.applications_table_view.table.currentRow()
        if selected_row < 0:
            return  # No Selection No Action
        table = self.view.applications_table_view.table
        # if row is None:
        #     selected_row = table.currentRow()
        # else:
        #     selected_row = row
        def get_cell_text(row, col):
            item = table.item(row, col)
            return item.text() if item else ""
        id = get_cell_text(selected_row, 0)
        org = get_cell_text(selected_row, 1)
        city = get_cell_text(selected_row, 2)
        role = get_cell_text(selected_row, 3)
        date = get_cell_text(selected_row, 4)
        contact = get_cell_text(selected_row, 5)
        note = get_cell_text(selected_row, 6)

        from views.application_form_view import ApplicationFormView
        dialog = ApplicationFormView(org, city, role, date, contact, note)
        if dialog.exec():
            data = dialog.get_form_data()
            self.data_manager.update_application(id, org, city, **data)
            self.open_applications_view(self.current_org_row, self.current_org_col)

    def delete_application(self):
        """
        Deletes the selected application entry.
        """
        table = self.view.applications_table_view.table
        selected_row = table.currentRow()
        if selected_row < 0:
            return  # No Selection No Action
        id_item = table.item(selected_row, 0)
        if id_item is None:
            return  # No ID found, do nothing
        id = id_item.text()
        org = table.item(selected_row, 1).text()
        city = table.item(selected_row, 2).text()
        role = table.item(selected_row, 3).text()

        # Optionally, onay için bir QMessageBox ekleyebilirsin
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Delete Application",
            "Are you sure you want to delete this application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_application(id, org, role)
            self.application_pairs.discard((org, city))
            # Table update
            self.open_applications_view(self.current_org_row, self.current_org_col)

    def check_for_release(self):
        """
        Checks for the latest release on GitHub
        and shows popup to view release notes and download button.
        """
        latest = fetch_latest_release()
        if not latest:
            # API might not be reachable silenced
            return
        latest_version = latest["tag"].lstrip("v")
        current_version = VERSION.lstrip("v")

        def version_tuple(version):
            return tuple(map(int, version.split(".")))

        if version_tuple(latest_version) > version_tuple(current_version):
            changelog = latest.get("changelog", "")
            asset = latest.get("asset", "")
            download_url = asset if asset else latest["html_url"]

            UpdateView.show_update_popup(self, latest_version, download_url, changelog)

    # Settings
    def show_settings_ui(self):
        """Opens the settings UI window for log preferences."""
        print("[DEBUG] show_settings_ui triggered")
        current_log_level = self.settings.get_log_level()
        rotation_limit = self.settings.get_log_rotation_limit()
        current_update_check = self.settings.get_check_for_release()

        self.settings_ui = SettingsUI(
            current_log_level, rotation_limit, current_update_check
        )
        self.settings_ui.settings_saved.connect(self.apply_settings)
        self.settings_ui.show()

    def apply_settings(self, log_level: str, rotation_limit: int, update_check: bool):
        """Handles saving settings from the UI."""
        self.settings.set_log_level(log_level)
        self.settings.set_log_rotation_limit(rotation_limit)
        self.settings.set_check_for_release(update_check)
        logger.info(
            "Settings updated: level=%s, rotation=%s, release_check=%s",
            log_level,
            rotation_limit,
            update_check,
        )

    # def toggle_applied(self, row_idx, state):
    #     """
    #     Triggered when a checkbox is toggled.

    #     Updates the 'applied' status of the corresponding sponsor in the database,
    #     based on the checkbox state.
    #     """
    #     # if not self.conn:
    #     #     print("[TOGGLE DEBUG] self.conn is None!")
    #     # else:
    #     #     print("[TOGGLE DEBUG] self.conn is VALID")

    #     org_item = self.view.sponsor_table.item(row_idx % self.page_size, 0)
    #     city_item = self.view.sponsor_table.item(row_idx % self.page_size, 1)

    #     if org_item and city_item:
    #         organisation_name = org_item.text()
    #         city = city_item.text()

    #         current_status = 1 if state == Qt.CheckState.Checked.value else 0
    #         self.data_manager.toggle_applied(organisation_name, city, current_status)

    #         logger.info(
    #             "Updated '%s' to %s",
    #             organisation_name,
    #             'applied' if current_status else 'not applied',
    #         )
