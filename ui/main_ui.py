import sys, os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QHBoxLayout, QCheckBox, QLabel
)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sponsor.csv_manager import CSVManager
from sponsor.transform_db import TransformDB

DB_PATH = "data/sponsorship.db"

class TSAApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_data()
        self.initUI()

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

        # Table
        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.layout.addWidget(self.table)

        # Next Page Button
        self.next_button = QPushButton("Next Page")
        self.next_button.clicked.connect(self.load_next_page)
        self.layout.addWidget(self.next_button)

        self.load_data_page()

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
            filters.append("LOWER(town_city) LIKE ?")
            params.append(f"%{city.lower()}%")

        org = self.org_input.text().strip()
        if org:
            filters.append("LOWER(organisation_name) LIKE ?")
            params.append(f"%{org.lower()}%")

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " LIMIT ? OFFSET ?"
        params.extend([self.page_size, offset])

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        self.table.setRowCount(len(rows))
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Organisation", "City", "County", "Type & Rating", "Route", "Applied"])

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data[:-1]):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            checkbox = QCheckBox()
            checkbox.setChecked(bool(row_data[-1]))
            checkbox.stateChanged.connect(lambda state, row=row_idx: self.toggle_applied(row))
            self.table.setCellWidget(row_idx, 5, checkbox)

        print("QUERY:", query)
        print("PARAMS:", params)
        print(f"📄 Loaded page {self.current_page + 1}")

    def load_next_page(self):
        self.current_page += 1
        self.load_data_page()

    def toggle_applied(self, row_idx):
        org_item = self.table.item(row_idx, 0)
        if org_item:
            organisation_name = org_item.text()
            checkbox = self.table.cellWidget(row_idx, 5)
            applied_value = 1 if checkbox.isChecked() else 0

            cursor = self.conn.cursor()
            cursor.execute("UPDATE sponsors SET applied=? WHERE organisation_name=?", (applied_value, organisation_name))
            self.conn.commit()

            print(f"Updated '{organisation_name}' to {'applied' if applied_value else 'not applied'}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TSAApp()
    window.show()
    sys.exit(app.exec())