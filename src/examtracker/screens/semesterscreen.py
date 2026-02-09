from textual.app import  ComposeResult, Screen
from textual.widgets import Footer, Header, DataTable, Input
from examtracker.database import (
    get_all_semester,
    add_semester,
    remove_semester_by_name,
)
from textual import on
from examtracker.screens.classscreen import ClassScreen

class AddSemesterScreen(Screen):
    def __init__(self)->None:
        super().__init__()
        self.db_session = self.app.db_session #type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
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
        add_semester(self.db_session, name) 
        self.db_session.commit()
        self.app.pop_screen()


class SemesterScreen(Screen):
    BINDINGS = [
        ("a", "add", "Add semester"),
        ("r", "remove", "Remove semester"),
    ]


    def __init__(self)->None:
        super().__init__()
        self.db_session = self.app.db_session #type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        self.semester_table: DataTable = DataTable(classes="semester_list")
        self.semester_table.add_columns("Name")
        self.semester_table.cursor_type = "row"
        self.refresh_table()
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
        row = self.semester_table.get_row_at(row_index)
        semester_name = row[0]

        remove_semester_by_name(self.db_session, semester_name)  # type:ignore
        self.db_session.commit()
        self.refresh_table()

    def on_screen_resume(self) -> None:
        self.refresh_table()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_index = self.semester_table.cursor_row
        if row_index is None:
            return

        semester_name = self.semester_table.get_row_at(row_index)[0]
        self.app.push_screen(ClassScreen(semester_name))


