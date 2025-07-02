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
)
from PyQt6.QtCore import QDateTime, QEvent, Qt


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
