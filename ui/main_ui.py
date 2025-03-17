import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QHBoxLayout, QCheckBox, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
from TSA.ui.table_manager import TableManager
from TSA.ui.data_manager import DataManager
from TSA.ui.navigation_manager import NavigationManager
from TSA.config import DB_PATH

class TSAApp(QWidget):
    def __init__(self):
        print("Database path:", DB_PATH)
        super().__init__()
        self.data_manager = DataManager()
        self.conn = self.data_manager.prepare_database()
        # Initialize TableManager before UI
        self.table_manager = TableManager()
        
        self.initUI()
        self.load_data_page()

    def initUI(self):
        self.setWindowTitle("TSA - Track Sponsored Applications")
        self.setGeometry(100, 100, 800, 600)

        self.layout: QVBoxLayout = QVBoxLayout()
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

        self.configure_table()

        # Navigation
        self.navigation_manager = NavigationManager(
            self.layout,
            # self.apply_filter,
            self.load_next_page,
            self.load_prev_page
        )

    def build_query(self):
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
        self.table_manager.table.verticalHeader().setVisible(True)
        self.table_manager.table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table_manager.table.setWordWrap(False)
        self.table_manager.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.table_manager.table.verticalHeader().setDefaultSectionSize(24)
        self.table_manager.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.layout.addWidget(self.table_manager.table)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.table_manager.adjust_column_widths(self.table_manager.table.viewport().width())

    def apply_filter(self):
        self.current_page = 0
        self.load_data_page()

    def load_data_page(self):
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
            checkbox.stateChanged.connect(lambda state, row=offset + row_idx: self.toggle_applied(row))
            self.table_manager.table.setCellWidget(row_idx, 5, checkbox)

        self.navigation_manager.update_page_info(self.current_page, total_results, self.page_size)

        for row_idx in range(len(rows)):
            # print(f"Row {row_idx}: {row_data}")
            item = self.table_manager.table.verticalHeaderItem(row_idx)
            if item is None:
                item = QTableWidgetItem()
                self.table_manager.table.setVerticalHeaderItem(row_idx, item)
            item.setText(str(offset + row_idx + 1))
        self.table_manager.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # print("QUERY:", query)
        # print("PARAMS:", params)
        # print(f"📄 Loaded page {self.current_page + 1}")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TSAApp()
    window.show()
    sys.exit(app.exec())