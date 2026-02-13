from textual.app import ComposeResult, Screen
from textual.widgets import Footer, Header, DataTable, Input, Label
from examtracker.database import (
    get_all_semester,
    add_semester,
    remove_semester_by_name,
)
from textual import on
from textual.containers import Vertical
from examtracker.screens.classscreen import ClassScreen
from sqlalchemy.exc import IntegrityError


class AddSemesterScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.db_session = self.app.db_session  # type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label("Add new Semester")
            self.input = Input(
                placeholder="Semester name (e.g. Fall 2026)",
                id="semester_name",
            )
            yield self.input
        yield Footer()

    def on_mount(self) -> None:
        self.input.focus()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.submit()

    def submit(self) -> None:
        name = self.input.value.strip()
        if not name:
            return
        try:
            add_semester(self.db_session, name)
            self.db_session.commit()
        except IntegrityError:
            # TODO add error message for unique constraint
            self.db_session.rollback()
            pass

        self.app.pop_screen()


class SemesterScreen(Screen):
    BINDINGS = [
        ("a", "add", "Add semester"),
        ("ctrl+r", "remove", "Remove semester"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.db_session = self.app.db_session  # type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        self.semester_table: DataTable = DataTable()
        self.semester_table.add_columns("Name")
        self.semester_table.cursor_type = "row"
        self.semester_table.border_title = "Semester Overview"
        yield self.semester_table
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_table()
        self.semester_table.focus()

    def refresh_table(self) -> None:
        self.semester_table.clear()
        for sem in get_all_semester(self.db_session):
            self.semester_table.add_row(sem.name)

    def action_add(self) -> None:
        self.app.push_screen(AddSemesterScreen())

    def action_remove(self) -> None:
        row_index = self.semester_table.cursor_row
        if row_index is None:
            return
        if not self.semester_table.is_valid_row_index(row_index):
            return
        row = self.semester_table.get_row_at(row_index)
        semester_name = row[0]

        remove_semester_by_name(self.db_session, semester_name)  # type:ignore
        self.db_session.commit()
        self.refresh_table()

    def on_screen_resume(self) -> None:
        self.refresh_table()

    @on(DataTable.RowSelected)
    def open_class(self, event: DataTable.RowSelected) -> None:
        row_index = self.semester_table.cursor_row
        if row_index is None:
            return

        semester_name = self.semester_table.get_row_at(row_index)[0]
        self.app.push_screen(ClassScreen(semester_name))
