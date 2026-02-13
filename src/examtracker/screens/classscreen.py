from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult, Screen
from textual.containers import Vertical
from textual.widgets import DataTable, Footer, Header, Input, Label

from examtracker.database import (
    add_class_to_semester,
    get_all_classes_for_semester,
    get_semester_by_name,
    remove_class_by_id,
)
from examtracker.screens.examscreen import ExamScreen
from examtracker.textual_utils.vimtable import VimTable


class AddClassScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, semester_name: str, **kwargs):
        super().__init__(**kwargs)
        self.semester_name = semester_name
        self.db_session = self.app.db_session  # type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label(f"Add Class to: {self.semester_name}")
            # Inputs for the class
            self.name_input = Input(placeholder="Class Name", id="name")
            yield self.name_input
        yield Footer()

    def on_mount(self) -> None:
        self.name_input.focus()

    # Submit on Enter from any Input
    @on(Input.Submitted)
    def submit(self) -> None:
        name = self.name_input.value.strip()
        if not name:
            return  # Require class name

        semester = get_semester_by_name(self.db_session, self.semester_name)

        # Add the class
        try:
            add_class_to_semester(self.db_session, name, semester)  # type: ignore
            self.db_session.commit()
        except IntegrityError:
            # TODO add error message for unique constraint
            self.db_session.rollback()
            pass

        # Pop the screen and return
        self.app.pop_screen()


class ClassScreen(Screen):
    """
    Shows all the classes for a given semester
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("a", "add", "Add semester"),
        ("ctrl+r", "remove", "Remove semester"),
    ]

    def __init__(self, semester_name: str) -> None:
        super().__init__()
        self.db_session: Session = self.app.db_session  # type: ignore
        self.semester_name = semester_name

    def compose(self) -> ComposeResult:
        yield Header()
        self.class_table: VimTable = VimTable()
        self.class_table.add_columns("ID", "Name")
        self.class_table.cursor_type = "row"
        self.class_table.border_title = f"Classes for: {self.semester_name}"
        yield self.class_table
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_table()

    def action_add(self) -> None:
        self.app.push_screen(AddClassScreen(self.semester_name))

    def action_remove(self) -> None:
        row_index = self.class_table.cursor_row
        if row_index is None:
            return
        if not self.class_table.is_valid_row_index(row_index):
            return
        row = self.class_table.get_row_at(row_index)
        class_id = row[0]
        remove_class_by_id(self.db_session, class_id)
        self.db_session.commit()
        self.refresh_table()

    def refresh_table(self) -> None:
        semester = get_semester_by_name(self.db_session, self.semester_name)

        self.class_table.clear()
        for cls in get_all_classes_for_semester(self.db_session, semester):
            self.class_table.add_row(cls.class_id, cls.name)

    def on_screen_resume(self) -> None:
        # Called when returning from AddSemesterScreen
        self.refresh_table()

    @on(VimTable.RowSelected)
    def open_exam(self, event: DataTable.RowSelected) -> None:
        row_index = self.class_table.cursor_row
        if row_index is None:
            return

        class_id = self.class_table.get_row_at(row_index)[0]
        self.app.push_screen(ExamScreen(class_id))
