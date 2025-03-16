from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class NavigationManager:
    def __init__(self, parent_layout, load_next_callback, load_previous_callback):
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
        nav_layout.addWidget(self.result_info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        parent_layout.addLayout(nav_layout)

    def update_page_info(self, current_page, total_rows, page_size):
        total_pages = (total_rows + page_size - 1) // page_size
        self.page_info_label.setText(f"Page {current_page + 1} of {total_pages}")
        self.result_info_label.setText(f"{total_rows} results")
