from PyQt6.QtWidgets import QTableWidget, QHeaderView, QVBoxLayout


class TableView:
    """View class responsible for setting up and managing the sponsor table display."""

    def __init__(self) -> None:
        """Initializes the QTableWidget used to display sponsor data."""
        self.table = QTableWidget()

    def setup_table(self, parent_layout: QVBoxLayout) -> None:
        """
        Sets up the table with headers, configuration, and adds it to the layout.

        Args:
            parent_layout (QVBoxLayout): The layout to which the table is added.
        """
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["Organisation", "City", "County", "Type & Rating", "Route", "Applied"]
        )
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Set minimum widths for each column
        self.table.setColumnWidth(0, 200)  # Organisation
        header.setMinimumSectionSize(60)
        header.resizeSection(0, 200)
        header.resizeSection(1, 120)
        header.resizeSection(2, 120)
        header.resizeSection(3, 140)
        header.resizeSection(4, 140)
        header.resizeSection(5, 80)

        # Allow the table to stretch across the window by assigning stretch factors
        header.setStretchLastSection(False)

        parent_layout.addWidget(self.table)

    def adjust_column_widths(self, table_width: int) -> None:
        """
        Adjusts the widths of the columns based on the current table width.

        Args:
            table_width (int): The width of the table's viewport.
        """
        fixed_columns_width = 80  # Applied column
        remaining_width = table_width - fixed_columns_width
        # Distribute remaining width proportionally
        self.table.setColumnWidth(
            0, max(200, int(remaining_width * 0.3))
        )  # Organisation
        self.table.setColumnWidth(1, max(100, int(remaining_width * 0.15)))  # City
        self.table.setColumnWidth(2, max(100, int(remaining_width * 0.15)))  # County
        self.table.setColumnWidth(
            3, max(120, int(remaining_width * 0.2))
        )  # Type & Rating
        self.table.setColumnWidth(4, max(120, int(remaining_width * 0.2)))  # Route
