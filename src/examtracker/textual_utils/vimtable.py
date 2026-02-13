from textual.widgets import DataTable


class VimTable(DataTable):

    BINDINGS = [
        ("j", "cursor_down"),
        ("k", "cursor_up"),
        ("l", "select_cursor"),
        ("h", "app.pop_screen"),
    ]
