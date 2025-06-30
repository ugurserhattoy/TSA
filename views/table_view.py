from PyQt6.QtWidgets import QTableWidget, QHeaderView, QVBoxLayout
from config import RES_SETTINGS


class TableView:
    """View class responsible for setting up and managing the sponsor table display."""

    def __init__(self) -> None:
        """Initializes the QTableWidget used to display sponsor data."""
        self.table = QTableWidget()

    def connect_double_click(self, callback):
        """Allows external code (controller) to react to row double-clicks."""
        self.table.cellDoubleClicked.connect(callback)

    def setup_main_table(self) -> None:
        """Sets up the main table"""
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Organisation", "City", "County", "Type & Rating", "Route"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        # Set minimum widths for each column
        # self.table.setColumnWidth(0, 200)  # Organisation
        header.setMinimumSectionSize(60)

        # Allow the table to stretch across the window by assigning stretch factors
        header.setStretchLastSection(False)
        # self.adjust_main_column_widths(self.table.width())

    def setup_applications_table(self):
        """Sets up the applications table"""
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Organisation", "City", "Role", "Date", "Contact", "Note"
        ])
        self.table.setColumnHidden(0, True) # ID hidden
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setWordWrap(False)

        header = self.table.horizontalHeader()
        # header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)   # Organisation
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)   # City
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)   # Role
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)   # Date
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Interactive)   # Contact
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)       # Note
        
        header.setMinimumSectionSize(60)
        # self.adjust_applications_column_widths(self.table.width())
        # header.setStretchLastSection(True)

    def adjust_main_column_widths(self, table_width: int) -> None:
        self.table.setColumnWidth(0, int(table_width * 0.25)) # Org
        self.table.setColumnWidth(1, int(table_width * 0.15))# City
        self.table.setColumnWidth(2, int(table_width * 0.15))# County
        self.table.setColumnWidth(3, int(table_width * 0.225)) # Type&Rating
        self.table.setColumnWidth(4, int(table_width * 0.225)) # Route
    
    def adjust_applications_column_widths(self, table_width: int) -> None:
        self.table.setColumnWidth(1, int(table_width * 0.15)) # Org
        self.table.setColumnWidth(2, int(table_width * 0.1))# City
        self.table.setColumnWidth(3, int(table_width * 0.15)) # Role
        self.table.setColumnWidth(4, min(int(table_width * 0.15), 125)) # Date
        self.table.setColumnWidth(5, int(table_width * 0.12)) # Contact
        self.table.setColumnWidth(6, int(table_width * 0.25))# Note
