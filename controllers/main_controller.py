"""
main_ui.py

This module serves as the Controller in the MVC architecture.
It manages the main window of the application, handles user interactions,
coordinates data filtering, pagination,
updating applications and highlight it on the main table.

Key Components:
- TableView: Manages the display and structure of the data table
- DataManager: Handles database interactions
- NavigationManager: Manages pagination and result information display
- MenuManager: Controls menu-related actions and signals
- LogsViewer: Displays log file content in a separate window

The TSAController class is the main entry point,
tying together UI initialization and application logic.
"""

import logging

from PyQt6.QtGui import QColor, QBrush
from PyQt6.QtWidgets import (
    QMainWindow,
    QTableWidgetItem,
)
from config import DB_PATH, SETTINGS_PATH, VERSION, RES_SETTINGS
from models.settings_model import SettingsManager
from views.application_view import ApplicationFormView
from views.application_view import confirm_delete
from views.main_view import MainView
from views.navigation_view import NavigationManager
from views.menu_view import MenuManager
from views.logs_viewer import LogsViewer
from views.settings_view import SettingsUI
from views.update_view import UpdateView
from controllers.data_controller import DataManager
from controllers.action_handlers import (
    setup_main_shortcuts,
    setup_applications_shortcuts,
    setup_main_enter_action,
    get_cell_text,
)
from utils.update_checker import fetch_latest_release


logger = logging.getLogger()


class TSAController(QMainWindow):
    """
    Main controller class for the TSA application.

    Initializes the main window, sets up UI components,
    connects user interactions to logic,
    and handles loading and updating sponsor and application data.
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
        self.current_organisation_name = None
        self.current_city = None
        self.current_org_row = None
        self.current_org_col = None

        self.view = MainView()
        self.setCentralWidget(self.view)

        self.page_size = 50

        # Connect filter inputs and button
        self.view.city_input.returnPressed.connect(self.apply_filter)
        self.view.org_input.returnPressed.connect(self.apply_filter)
        self.view.apply_filter_button.clicked.connect(self.apply_filter)
        self.view.sponsor_table.cellDoubleClicked.connect(self.open_applications_view)
        setup_main_enter_action(
            self.view.sponsor_table,
            self.open_applications_view,
            self.view.city_input,
            self.view.org_input,
        )

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
        self.menu_manager.check_release_requested.connect(self.check_for_release)
        # self.menu_manager.help_requested.connect(self.show_help_viewer)

        # Keyboard shortcuts
        setup_main_shortcuts(
            self.view,
            self.load_prev_page,
            self.load_next_page,
            # self.view.city_input.setFocus,
            self.view.sponsor_table.setFocus,
        )
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

    def resizeEvent(self, event):
        """
        Handles window resize events to adjust column widths dynamically.
        """
        super().resizeEvent(event)
        self.adjust_main_col_widths()
        self.adjust_applications_col_widths()

    def configure_table(self):
        """
        Applies styling and layout configuration to the table widget.
        Adjusts headers and section sizes.
        """
        self.view.stacked_widget.setCurrentIndex(0)

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

        Also highlights applied organisations
        """
        offset = self.current_page * self.page_size
        query, params, count_query, count_params = self.build_query()
        total_results = self.get_total_results(count_query, count_params)
        rows = self.fetch_rows(query, params)
        self.fill_sponsor_table(rows)
        self.highlight_applied_rows()
        self.set_navigation_info(total_results)
        self.set_vertical_headers(len(rows), offset)

    def get_total_results(self, count_query, count_params):
        count_cursor = self.conn.cursor()
        count_cursor.execute(count_query, count_params)
        return count_cursor.fetchone()[0]

    def fetch_rows(self, query, params):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def fill_sponsor_table(self, rows):
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

    def set_navigation_info(self, total_results):
        page_info = f"Page {self.current_page + 1}"
        result_info = f"{total_results} results"
        logger.debug("Page info: %s, Result info: %s", page_info, result_info)
        self.navigation_manager.set_page_info(page_info)
        self.navigation_manager.set_result_info(result_info)

    def set_vertical_headers(self, num_rows, offset):
        for row_idx in range(num_rows):
            item = self.view.sponsor_table.verticalHeaderItem(row_idx)
            if item is None:
                item = QTableWidgetItem()
                self.view.sponsor_table.setVerticalHeaderItem(row_idx, item)
            item.setText(str(offset + row_idx + 1))

    def highlight_applied_rows(self):
        for row_idx in range(self.view.sponsor_table.rowCount()):
            org_item = self.view.sponsor_table.item(row_idx, 0)
            city_item = self.view.sponsor_table.item(row_idx, 1)
            if not org_item or not city_item:
                continue
            org = org_item.text()
            city = city_item.text()
            if (org, city) in self.application_pairs:  # Applied
                color = "#2A4520" if row_idx % 2 == 0 else "#49693C"
                for col in range(self.view.sponsor_table.columnCount()):
                    item = self.view.sponsor_table.item(row_idx, col)
                    if item:
                        item.setBackground(QColor(color))
            else:  # Default
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
        self.set_current_organisation(row, col)
        self.show_applications_view()
        applications = self.data_manager.get_applications(
            self.current_organisation_name, self.current_city
        )
        self.fill_applications_table(applications)
        self.setup_applications_signals()
        setup_applications_shortcuts(
            self.view,
            self.app_back_button_clicked,
            self.edit_application,
            self.add_application,
            self.delete_application,
        )
        # setup_enter_action(self.view.applications_table, self.edit_application)

    def set_current_organisation(self, row, col):
        org_item = self.view.sponsor_table.item(row, 0)
        city_item = self.view.sponsor_table.item(row, 1)
        if org_item and city_item:
            self.current_organisation_name = org_item.text()
            self.current_city = city_item.text()
            self.current_org_row = row
            self.current_org_col = col
        else:
            self.current_organisation_name = None
            self.current_city = None

    def fill_applications_table(self, applications):
        table = self.view.applications_table_view.table
        table.setRowCount(len(applications))
        for row_idx, app_row in enumerate(applications):
            for col_idx, value in enumerate(app_row):
                item = QTableWidgetItem(str(value))
                if col_idx == 6 and str(value).strip():
                    item.setToolTip(str(value))
                table.setItem(row_idx, col_idx, item)

    def setup_applications_signals(self):
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
        self.view.applications_table_view.table.cellDoubleClicked.connect(
            self.edit_application
        )

    def show_applications_view(self):
        self.view.applications_table_view.setup_applications_table()
        self.view.stacked_widget.setCurrentIndex(1)
        self.adjust_applications_col_widths()

    def show_sponsor_table(self):
        """Shows main table screen"""
        # self.current_organisation_name = None
        # self.current_city = None
        self.configure_table()
        self.highlight_applied_rows()

    def app_back_button_clicked(self):
        self.show_sponsor_table()
        self.adjust_main_col_widths()
        setup_main_shortcuts(
            self.view,
            self.load_prev_page,
            self.load_next_page,
            # self.view.city_input.setFocus,
            self.view.sponsor_table.setFocus,
        )

    def add_application(self):
        """
        Opens a dialog to add a new application for the selected organisation.
        """
        org = self.current_organisation_name
        city = self.current_city

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

        application_id = get_cell_text(table, selected_row, 0)
        org = get_cell_text(table, selected_row, 1)
        city = get_cell_text(table, selected_row, 2)
        role = get_cell_text(table, selected_row, 3)
        date = get_cell_text(table, selected_row, 4)
        contact = get_cell_text(table, selected_row, 5)
        note = get_cell_text(table, selected_row, 6)

        dialog = ApplicationFormView(org, city, role, date, contact, note)
        if dialog.exec():
            data = dialog.get_form_data()
            self.data_manager.update_application(application_id, org, city, **data)
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
        application_id = id_item.text()
        org = table.item(selected_row, 1).text()
        city = table.item(selected_row, 2).text()
        role = table.item(selected_row, 3).text()

        if confirm_delete(self):
            self.data_manager.delete_application(application_id, org, role)
            if not self.data_manager.get_applications(org, city):
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
