from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import (
    QTableWidgetItem,
)
from views.application_view import ApplicationFormView, confirm_delete
from controllers.action_handlers import get_cell_text


class ApplicationController(QObject):
    def __init__(
        self, data_manager, main_view, application_pairs, open_applications_view_cb
    ):
        super().__init__()
        self.data_manager = data_manager
        self.main_view = main_view
        self.application_pairs = application_pairs  # set
        self.av = main_view.application_view
        self.open_applications_view_cb = open_applications_view_cb

    def fill_applications_table(self, applications, name=None):
        suffix = f"_{name}" if name else ""
        if name == "all":
            table = getattr(self.main_view, f"applications_table{suffix}")
        else:
            table = getattr(self.av, f"applications_table{suffix}")
        table.setRowCount(len(applications))
        for row_idx, app_row in enumerate(applications):
            for col_idx, value in enumerate(app_row):
                item = QTableWidgetItem(str(value))
                if col_idx == 6 and str(value).strip():
                    item.setToolTip(str(value))
                table.setItem(row_idx, col_idx, item)

    def setup_applications_signals(
        self,
        only_applications_checked,
        app_back_button_cb,
        edit_application_cb,
        add_application_cb,
        delete_application_cb,
    ):
        view = self.main_view
        # Disconnect previous connections to avoid duplicate calls
        try:
            self.av.back_button.clicked.disconnect()
            self.av.edit_button.clicked.disconnect()
            self.av.add_new_button.clicked.disconnect()
            self.av.delete_button.clicked.disconnect()
            self.av.applications_table.cellDoubleClicked.disconnect()
        except TypeError:
            pass
        if only_applications_checked:
            try:
                view.applications_table_all.cellDoubleClicked.disconnect()
            except TypeError:
                pass
            view.applications_table_all.cellDoubleClicked.connect(edit_application_cb)
        else:
            self.av.back_button.clicked.connect(app_back_button_cb)
            self.av.add_new_button.clicked.connect(add_application_cb)
            self.av.edit_button.clicked.connect(edit_application_cb)
            self.av.delete_button.clicked.connect(delete_application_cb)
            self.av.applications_table.cellDoubleClicked.connect(edit_application_cb)

    def add_application(
        self,
        org,
        city,
        current_org_row,
        current_org_col,
    ):
        dialog = ApplicationFormView(org, city)
        if dialog.exec():
            data = dialog.get_form_data()
            self.data_manager.add_application(org, city, **data)
            self.application_pairs.add((org, city))
            self.open_applications_view_cb(current_org_row, current_org_col)

    def edit_application(
        self,
        only_applications_checked,
        current_org_row,
        current_org_col,
        load_applications_page_cb,
    ):
        view = self.main_view
        table = (
            view.applications_table_all
            if only_applications_checked
            else self.av.applications_table
        )
        selected_row = table.currentRow()
        if selected_row < 0:
            return
        application_id = get_cell_text(table, selected_row, 0)
        org = get_cell_text(table, selected_row, 1)
        city = get_cell_text(table, selected_row, 2)
        role = get_cell_text(table, selected_row, 3)
        date = get_cell_text(table, selected_row, 4)
        contact = get_cell_text(table, selected_row, 5)
        note = get_cell_text(table, selected_row, 6)

        dialog = ApplicationFormView(org, city, role, date, contact, note)
        if dialog.exec():
            data = dialog.get_form_data()
            self.data_manager.update_application(application_id, org, city, **data)
            if only_applications_checked:
                load_applications_page_cb()
            else:
                self.open_applications_view_cb(current_org_row, current_org_col)

    def delete_application(
        self,
        current_org_row,
        current_org_col,
    ):
        table = self.av.applications_table_view.table
        selected_row = table.currentRow()
        if selected_row < 0:
            return
        id_item = table.item(selected_row, 0)
        if id_item is None:
            return
        application_id = id_item.text()
        org = table.item(selected_row, 1).text()
        city = table.item(selected_row, 2).text()
        role = table.item(selected_row, 3).text()

        if confirm_delete(self.main_view, org, role):
            self.data_manager.delete_application(application_id, org, role)
            if not self.data_manager.get_applications(org, city):
                self.application_pairs.discard((org, city))
            self.open_applications_view_cb(current_org_row, current_org_col)

    def show_applications_view(self):
        self.av.applications_table_view.setup_applications_table()
        self.main_view.stacked_widget.setCurrentIndex(1)
        self.av.applications_table_view.adjust_applications_column_widths(
            self.av.applications_table.viewport().width()
        )


# Note: The following method is commented out because it is not used in the current code
# It was originally intended to create a QTableWidgetItem, but it is not necessary
# since we can directly use QTableWidgetItem from PyQt6.QtWidgets.
# Uncomment if needed in the future.
# def _create_table_item(self, value):
#     from PyQt6.QtWidgets import QTableWidgetItem
#     return QTableWidgetItem(value)
