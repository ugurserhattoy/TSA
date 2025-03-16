import sys, os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QHBoxLayout, QCheckBox, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sponsor.csv_manager import CSVManager
from sponsor.transform_db import TransformDB

DB_PATH = "data/sponsorship.db"

class TSAApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_data()
        # Initialize TableManager before UI
        self.table_manager = TableManager()
        
        self.initUI()
        self.table_manager.setup_table(self.layout)
        self.load_data_page()

    def init_data(self):
        csv_manager = CSVManager()
        csv_manager.download_csv()
        transform_db = TransformDB()
        df = transform_db.clean_and_transform_csv()
        transform_db.save_as_sqlite(df)
        self.conn = sqlite3.connect(transform_db.db_path)

    def initUI(self):
        self.setWindowTitle("TSA - Track Sponsored Applications")
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

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

        # Navigation Buttons
        self.page_info_label = QLabel("Page 1 of 1")
        self.next_button = QPushButton("Next Page")
        self.prev_button = QPushButton("Previous Page")
        self.prev_button.clicked.connect(self.load_prev_page)
        self.next_button.clicked.connect(self.load_next_page)
        self.result_count_label = QLabel("")
        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addStretch()
        nav_layout.addWidget(self.page_info_label)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_button)
        self.layout.addLayout(nav_layout)
        self.layout.addWidget(self.result_count_label)
        self.table_manager.table.verticalHeader().setVisible(True)
        self.table_manager.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table_manager.table.setWordWrap(False)
        self.table_manager.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table_manager.table.verticalHeader().setDefaultSectionSize(24)
        self.table_manager.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.table_manager.adjust_column_widths(self.table_manager.table.viewport().width())

    def apply_filter(self):
        self.current_page = 0
        self.load_data_page()

    def load_data_page(self):
        offset = self.current_page * self.page_size
        query = """
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
            query += " WHERE " + " AND ".join(filters)

        query += " LIMIT ? OFFSET ?"
        params.extend([self.page_size, offset])

        count_query = "SELECT COUNT(*) FROM sponsors"
        count_params = []

        if filters:
            count_query += " WHERE " + " AND ".join(filters)
            count_params = params[:-2]  # exclude LIMIT and OFFSET

        count_cursor = self.conn.cursor()
        count_cursor.execute(count_query, count_params)
        total_results = count_cursor.fetchone()[0]

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        self.table_manager.table.setRowCount(len(rows))

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data[:-1]):
                self.table_manager.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            checkbox = QCheckBox()
            checkbox.setChecked(bool(row_data[-1]))
            checkbox.stateChanged.connect(lambda state, row=offset + row_idx: self.toggle_applied(row))
            self.table_manager.table.setCellWidget(row_idx, 5, checkbox)

        total_pages = max(1, (total_results + self.page_size - 1) // self.page_size)
        self.page_info_label.setText(f"Page {self.current_page + 1} of {total_pages}")
        self.result_count_label.setText(f"Total Results: {total_results}")

        for row_idx in range(len(rows)):
            item = self.table_manager.table.verticalHeaderItem(row_idx)
            if item is None:
                item = QTableWidgetItem()
                self.table_manager.table.setVerticalHeaderItem(row_idx, item)
            item.setText(str(offset + row_idx + 1))
        self.table_manager.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        print("QUERY:", query)
        print("PARAMS:", params)
        print(f"📄 Loaded page {self.current_page + 1}")

    def load_next_page(self):
        self.current_page += 1
        self.load_data_page()

    def load_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data_page()

    def toggle_applied(self, row_idx):
        org_item = self.table_manager.table.item(row_idx % self.page_size, 0)
        if org_item:
            organisation_name = org_item.text()
            checkbox = self.table_manager.table.cellWidget(row_idx % self.page_size, 5)
            applied_value = 1 if checkbox.isChecked() else 0

            cursor = self.conn.cursor()
            cursor.execute("UPDATE sponsors SET applied=? WHERE organisation_name=?", (applied_value, organisation_name))
            self.conn.commit()

            print(f"Updated '{organisation_name}' to {'applied' if applied_value else 'not applied'}")

class TableManager:
    def __init__(self):
        self.table = QTableWidget()

    def setup_table(self, parent_layout):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Organisation", "City", "County", "Type & Rating", "Route", "Applied"])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Set minimum widths for each column
        self.table.setColumnWidth(0, 200)  # Organisation
        header.setMinimumSectionSize(60)
        header.resizeSection(0, 200)
        header.resizeSection(1, 140)
        header.resizeSection(2, 140)
        header.resizeSection(3, 160)
        header.resizeSection(4, 160)
        header.resizeSection(5, 60)

        # Allow the table to stretch across the window by assigning stretch factors
        header.setStretchLastSection(False)

        parent_layout.addWidget(self.table)

    def adjust_column_widths(self, table_width):
        fixed_columns_width = 60  # Applied column
        remaining_width = table_width - fixed_columns_width
        # Distribute remaining width proportionally
        self.table.setColumnWidth(0, max(200, int(remaining_width * 0.3)))  # Organisation
        self.table.setColumnWidth(1, max(120, int(remaining_width * 0.15)))  # City
        self.table.setColumnWidth(2, max(120, int(remaining_width * 0.15)))  # County
        self.table.setColumnWidth(3, max(140, int(remaining_width * 0.2)))  # Type & Rating
        self.table.setColumnWidth(4, max(140, int(remaining_width * 0.2)))  # Route

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TSAApp()
    window.show()
    sys.exit(app.exec())