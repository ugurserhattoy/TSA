from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QDateTimeEdit,
    QMessageBox,
    QWidget,
)
from PyQt6.QtCore import QDateTime, QEvent, Qt
from PyQt6.QtGui import QIcon
from views.table_view import TableView
from utils.ui_helpers import button_style


class ApplicationView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Actions panel
        actions_panel = QWidget()
        actions_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.setStyleSheet(button_style())
        self.edit_button = QPushButton("Edit")
        self.edit_button.setStyleSheet(button_style("lblue"))
        self.add_new_button = QPushButton("Add New")
        self.add_new_button.setStyleSheet(button_style("blue"))
        actions_layout.addWidget(self.back_button)
        actions_layout.addWidget(self.edit_button)
        actions_layout.addWidget(self.add_new_button)
        actions_panel.setLayout(actions_layout)

        # Table
        self.applications_table_view = TableView()
        self.applications_table = self.applications_table_view.table

        # Bottom panel
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout()
        job_board_widget = QWidget()
        job_board_layout = QHBoxLayout()
        delete_button_widget = QWidget()
        delete_layout = QHBoxLayout()
        filler_widget = QWidget()
        filler_layout = QHBoxLayout()

        # Job board buttons
        self.linkedin_btn = QPushButton()
        self.linkedin_btn.setIcon(QIcon("assets/lin.png"))
        self.linkedin_btn.setToolTip("LinkedIn")
        self.linkedin_btn.setFixedSize(36, 36)
        self.linkedin_btn.setStyleSheet(button_style("white"))

        self.indeed_btn = QPushButton()
        self.indeed_btn.setIcon(QIcon("assets/ind.png"))
        self.indeed_btn.setToolTip("Indeed")
        self.indeed_btn.setFixedSize(36, 36)
        self.indeed_btn.setStyleSheet(button_style("white"))

        self.glassdoor_btn = QPushButton()
        self.glassdoor_btn.setIcon(QIcon("assets/glass.png"))
        self.glassdoor_btn.setToolTip("Glassdoor")
        self.glassdoor_btn.setFixedSize(36, 36)
        self.glassdoor_btn.setStyleSheet(button_style("white"))

        self.google_btn = QPushButton()
        self.google_btn.setIcon(QIcon("assets/g.png"))
        self.google_btn.setToolTip("Google")
        self.google_btn.setFixedSize(36, 36)
        self.google_btn.setStyleSheet(button_style("white"))

        # Add buttons to job board layout
        job_board_layout.addWidget(self.linkedin_btn)
        job_board_layout.addWidget(self.indeed_btn)
        job_board_layout.addWidget(self.glassdoor_btn)
        job_board_layout.addWidget(self.google_btn)
        job_board_widget.setLayout(job_board_layout)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(button_style("red", 180))
        delete_layout.addWidget(self.delete_button)
        delete_button_widget.setLayout(delete_layout)

        filler_widget.setLayout(filler_layout)

        bottom_layout.addWidget(
            job_board_widget,
            alignment=Qt.AlignmentFlag.AlignLeft,
            stretch=1
        )
        bottom_layout.addWidget(
            delete_button_widget,
            alignment=Qt.AlignmentFlag.AlignCenter,
            stretch=1
        )
        # bottom_layout.addStretch()
        bottom_layout.addWidget(filler_widget, stretch=1)
        bottom_widget.setLayout(bottom_layout)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(actions_panel)
        main_layout.addWidget(self.applications_table)
        main_layout.addWidget(bottom_widget)
        self.setLayout(main_layout)


class ApplicationFormView(QDialog):
    def __init__(self, organisation, city, role="", date=None, contact="", note=""):
        super().__init__()
        self.setWindowTitle("Application Form")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # Organisation (readonly)
        org_layout = QHBoxLayout()
        org_label = QLabel("Organisation:")
        self.org_input = QLineEdit(organisation)
        self.org_input.setReadOnly(True)
        org_layout.addWidget(org_label)
        org_layout.addWidget(self.org_input)
        layout.addLayout(org_layout)

        # City (readonly)
        city_layout = QHBoxLayout()
        city_label = QLabel("City:")
        self.city_input = QLineEdit(city)
        self.city_input.setReadOnly(True)
        city_layout.addWidget(city_label)
        city_layout.addWidget(self.city_input)
        layout.addLayout(city_layout)

        # Role
        role_layout = QHBoxLayout()
        role_label = QLabel("Role:")
        self.role_input = QLineEdit(role)
        self.role_input.installEventFilter(self)
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_input)
        layout.addLayout(role_layout)

        # Date
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        self.date_input = QDateTimeEdit()
        self.date_input.installEventFilter(self)
        self.date_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.date_input.setCalendarPopup(True)
        if date:
            self.date_input.setDateTime(QDateTime.fromString(date, "yyyy-MM-dd HH:mm"))
        else:
            self.date_input.setDateTime(QDateTime.currentDateTime())
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)

        # Contact
        contact_layout = QHBoxLayout()
        contact_label = QLabel("Contact:")
        self.contact_input = QLineEdit(contact)
        self.contact_input.installEventFilter(self)
        contact_layout.addWidget(contact_label)
        contact_layout.addWidget(self.contact_input)
        layout.addLayout(contact_layout)

        # Note
        note_label = QLabel("Note:")
        self.note_input = QTextEdit(note)
        self.note_input.installEventFilter(self)
        layout.addWidget(note_label)
        layout.addWidget(self.note_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.save_button = QPushButton("Save && Exit")
        self.save_button.setDefault(True)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

        # Signals
        self.back_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.accept)

    def get_form_data(self):
        return {
            "role": self.role_input.text(),
            "date": self.date_input.dateTime().toString("yyyy-MM-dd HH:mm"),
            "contact": self.contact_input.text(),
            "note": self.note_input.toPlainText(),
        }

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
        ):
            # Role, Date, Contact
            if obj == self.role_input:
                self.date_input.setFocus()
                return True
            if obj == self.date_input:
                self.contact_input.setFocus()
                return True
            if obj == self.contact_input:
                self.note_input.setFocus()
                return True
            if obj == self.note_input:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    return False
                self.save_button.setFocus()
                return True
        return super().eventFilter(obj, event)


def confirm_delete(parent=None):
    reply = QMessageBox.question(
        parent,
        "Delete Application",
        "Are you sure you want to delete this application?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    return reply == QMessageBox.StandardButton.Yes
