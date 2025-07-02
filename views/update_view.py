import webbrowser
from PyQt6.QtWidgets import (
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QLabel,
)


class UpdateView:
    @staticmethod
    def show_update_popup(parent, latest_version, download_url, changelog_html):
        while True:
            msg = QMessageBox(parent)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("New Version Released!")
            text = (
                f"A new version (v{latest_version}) is available!\n\n"
                "Would you like to download the latest release or view the release notes?"
            )
            msg.setText(text)
            # icon_path = os.path.join(os.path.dirname(__file__), "../data/tsa_icon.png")
            download_btn = msg.addButton("Download", QMessageBox.ButtonRole.YesRole)
            changelog_btn = msg.addButton(
                "View Changelog", QMessageBox.ButtonRole.ActionRole
            )
            cancel_btn = msg.addButton("Cancel", QMessageBox.ButtonRole.NoRole)
            msg.setDefaultButton(download_btn)

            msg.exec()
            clicked = msg.clickedButton()
            if clicked == download_btn:
                webbrowser.open(download_url)
            elif clicked == changelog_btn:
                UpdateView.show_changelog_popup(parent, changelog_html)
            elif clicked == cancel_btn:
                break

    @staticmethod
    def show_changelog_popup(parent, changelog_html):
        dlg = QDialog(parent)
        dlg.setWindowTitle("Release Notes")
        layout = QVBoxLayout()
        label = QLabel("<b>Release Notes</b>")
        layout.addWidget(label)
        changelog = QTextEdit()
        changelog.setReadOnly(True)
        changelog.setHtml(changelog_html)
        layout.addWidget(changelog)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)
        dlg.resize(800, 600)
        dlg.setLayout(layout)
        dlg.exec()
