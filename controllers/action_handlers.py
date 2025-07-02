import platform
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidget, QLineEdit
from PyQt6.QtGui import QKeySequence, QShortcut

shortcut_list = []


def get_cell_text(table, row, col):
    item = table.item(row, col)
    return item.text() if item else ""


def setup_main_shortcuts(view, prev_cb, next_cb, focus_table_cb):
    """Sets shortcuts up"""
    platform_name = platform.system()
    if platform_name == "Darwin":  # macOS
        prev_seq = "Meta+B"
        next_seq = "Meta+N"
        focus_seq = "Meta+F"
    else:
        prev_seq = "Ctrl+B"
        next_seq = "Ctrl+N"
        focus_seq = "Ctrl+F"

    prev_shortcut = QShortcut(QKeySequence(prev_seq), view)
    next_shortcut = QShortcut(QKeySequence(next_seq), view)
    focus_city_shortcut = QShortcut(QKeySequence(focus_seq), view)
    focus_table_shortcut = QShortcut(Qt.Key.Key_Escape, view)

    prev_shortcut.activated.connect(prev_cb)
    next_shortcut.activated.connect(next_cb)
    focus_city_shortcut.activated.connect(lambda: focus_org_input(view))
    focus_table_shortcut.activated.connect(focus_table_cb)

    clear_shortcuts()
    global shortcut_list
    shortcut_list = [
        prev_shortcut,
        next_shortcut,
        focus_city_shortcut,
        focus_table_shortcut,
    ]


def setup_applications_shortcuts(view, back_cb, edit_cb, add_new_cb, del_cb):
    back_shortcut_esc = QShortcut(QKeySequence(Qt.Key.Key_Escape), view)
    back_shortcut_bs = QShortcut(QKeySequence(Qt.Key.Key_Backspace), view)
    edit_shortcut = QShortcut(QKeySequence(Qt.Key.Key_E), view)
    add_shortcut = QShortcut(QKeySequence(Qt.Key.Key_A), view)
    del_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Delete), view)

    back_shortcut_esc.activated.connect(back_cb)
    back_shortcut_bs.activated.connect(back_cb)
    edit_shortcut.activated.connect(edit_cb)
    add_shortcut.activated.connect(add_new_cb)
    del_shortcut.activated.connect(del_cb)
    clear_shortcuts()
    global shortcut_list
    shortcut_list = [
        back_shortcut_esc,
        back_shortcut_bs,
        edit_shortcut,
        add_shortcut,
        del_shortcut,
    ]


def clear_shortcuts():
    # global shortcut_list
    if shortcut_list:
        for shortcut in shortcut_list:
            shortcut.setParent(None)


def focus_org_input(view):
    view.sponsor_table.clearSelection()
    view.org_input.setFocus()


def setup_enter_action(table: QTableWidget, open_row_callback):
    """
    Enter pressed on table will trigger action
    Args:
        table: QTableWidget instance
        open_row_callback: Function to activate with selected row
    """
    enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), table)
    enter_shortcut.activated.connect(
        lambda: trigger_row_action(table, open_row_callback)
    )


def make_focus_in_event(original_event, enable_fn):
    def focus_in(event):
        enable_fn()
        original_event(event)

    return focus_in


def make_focus_out_event(original_event, disable_fn):
    def focus_out(event):
        disable_fn()
        original_event(event)

    return focus_out


def setup_main_enter_action(
    table: QTableWidget, open_row_callback, city_input: QLineEdit, org_input: QLineEdit
):
    """
    Enter pressed on table will trigger action
    Args:
        table: QTableWidget instance
        open_row_callback: Function to activate with selected row
        city_input: QLineEdit (for city filter)
        org_input: QLineEdit (for org filter)
    """
    enter_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), table)
    enter_shortcut.setEnabled(False)

    def enable_shortcut():
        enter_shortcut.setEnabled(True)

    def disable_shortcut():
        enter_shortcut.setEnabled(False)

    # Enabled when table focused
    table.focusInEvent = make_focus_in_event(table.focusInEvent, enable_shortcut)
    table.focusOutEvent = make_focus_out_event(table.focusOutEvent, disable_shortcut)
    city_input.focusInEvent = make_focus_in_event(
        city_input.focusInEvent, disable_shortcut
    )
    org_input.focusInEvent = make_focus_in_event(
        org_input.focusInEvent, disable_shortcut
    )

    enter_shortcut.activated.connect(
        lambda: trigger_row_action(table, open_row_callback)
    )


def trigger_row_action(table: QTableWidget, callback):
    """
    Triggers callback func on selected row
    Args:
        table: QTableWidget instance
        callback: Function to process
    """
    row = table.currentRow()
    col = table.currentColumn()
    if row >= 0:
        callback(row, col)
