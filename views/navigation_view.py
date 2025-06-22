from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class NavigationManager:
    """
    Manages the navigation controls including pagination buttons and result info display.

    This class provides an interface for navigating through paginated results,
    allowing users to move to the previous or next page and displaying
    the current page number along with the total number of results.

    Attributes:
        page_info_label (QLabel): Displays the current page number.
        result_info_label (QLabel): Displays the total number of results.
        previous_button (QPushButton): Button to navigate to the previous page.
        next_button (QPushButton): Button to navigate to the next page.
    """

    def __init__(self, parent_layout, load_next_callback, load_previous_callback):
        """
        Initializes the navigation UI elements and connects button signals.

        Args:
            parent_layout (QLayout): The layout to which the navigation layout is added.
            load_next_callback (function): Callback for the next page button.
            load_previous_callback (function): Callback for the previous page button.
        """
        self.page_info_label = QLabel("Page 1")
        self.result_info_label = QLabel("0 results")

        self.previous_button = QPushButton("Previous Page")
        self.previous_button.setFixedWidth(150)
        self.previous_button.clicked.connect(load_previous_callback)

        self.next_button = QPushButton("Next Page")
        self.next_button.setFixedWidth(150)
        self.next_button.clicked.connect(load_next_callback)

        nav_layout = QVBoxLayout()

        nav_buttons_layout = QHBoxLayout()
        nav_buttons_layout.addWidget(self.previous_button)
        nav_buttons_layout.addStretch()
        nav_buttons_layout.addWidget(self.page_info_label)
        nav_buttons_layout.addStretch()
        nav_buttons_layout.addWidget(self.next_button)

        nav_layout.addLayout(nav_buttons_layout)
        nav_layout.addWidget(
            self.result_info_label, alignment=Qt.AlignmentFlag.AlignCenter
        )

        parent_layout.addLayout(nav_layout)

    def set_page_info(self, page_text: str):
        """
        Updates the label to display the current page information.

        Args:
            page_text (str): The text to display as page information.
        """
        self.page_info_label.setText(page_text)

    def set_result_info(self, result_text: str):
        """
        Updates the label to display the number of results.

        Args:
            result_text (str): The text to display as result information.
        """
        self.result_info_label.setText(result_text)
