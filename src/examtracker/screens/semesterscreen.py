from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from textual import on
from textual.app import ComposeResult, Screen
from textual.widgets import DataTable, Footer, Header

from examtracker.database import (
    add_semester,
    get_all_semester,
    get_semester_by_name,
    remove_semester_by_name,
)
from examtracker.screens.classscreen import ClassScreen
from examtracker.screens.inputscreens import SingleInputScreen
from examtracker.textual_utils.vimtable import VimTable


class AddSemesterScreen(SingleInputScreen):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label_text = "Add new semester"

    def on_mount(self) -> None:
        self.input_button.focus()
        self.input_button.placeholder = "semester name"
        self.input_button.value = ""

    def submit(self) -> None:
        name = self.input_button.value.strip()
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


class EditSemesterScreen(SingleInputScreen):

    def __init__(self, semester_name: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.semester_name = semester_name
        self.label_text = "Edit semester"

    def on_mount(self) -> None:
        semester = get_semester_by_name(self.db_session, self.semester_name)
        self.input_button.value = semester.name
        self.input_button.focus()

    def submit(self) -> None:
        name = self.input_button.value.strip()
        if not name:
            return
        semester = get_semester_by_name(self.db_session, self.semester_name)
        try:
            semester.name = name
            self.db_session.commit()
        except IntegrityError:
            # TODO add error message for unique constraint
            self.db_session.rollback()
            pass

        self.app.pop_screen()


class SemesterScreen(Screen):
    BINDINGS = [
        ("a", "add", "Add semester"),
        ("e", "edit", "Edit semester"),
        ("ctrl+r", "remove", "Remove semester"),
    ]

    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        self.semester_table: VimTable = VimTable()
        self.semester_table.add_columns("Name")
        self.semester_table.cursor_type = "row"
        self.semester_table.border_title = "semester overview"
        yield self.semester_table
        yield Footer()

    def on_mount(self) -> None:
        self.db_session = self.app.db_session  # type: ignore
        self.refresh_table()
        self.semester_table.focus()

    def refresh_table(self) -> None:
        self.semester_table.clear()
        for sem in get_all_semester(self.db_session):
            self.semester_table.add_row(sem.name)

    def action_edit(self) -> None:
        row_index = self.semester_table.cursor_row
        if row_index is None:
            return

        semester_name = self.semester_table.get_row_at(row_index)[0]
        self.app.push_screen(EditSemesterScreen(semester_name))

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

    @on(VimTable.RowSelected)
    def open_class(self, event: DataTable.RowSelected) -> None:
        row_index = self.semester_table.cursor_row
        if row_index is None:
            return

        semester_name = self.semester_table.get_row_at(row_index)[0]
        self.app.push_screen(ClassScreen(semester_name))
