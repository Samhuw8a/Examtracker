from textual.app import ComposeResult, Screen
from textual.widgets import Footer, Header, DataTable, Input
from examtracker.database import (
    get_all_classes_for_semester,
    get_semester_by_name,
    add_class_to_semester,
    remove_class_by_name,
)

from textual import on
from sqlalchemy.orm import Session

from examtracker.screens.examscreen import ExamScreen


class AddClassScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, semester_name: str, **kwargs):
        super().__init__(**kwargs)
        self.semester_name = semester_name

    def compose(self) -> ComposeResult:
        yield Header()
        # Inputs for the class
        self.name_input = Input(placeholder="Class Name", id="name")
        yield self.name_input
        yield Footer()

    def on_mount(self) -> None:
        self.name_input.focus()

    # Submit on Enter from any Input
    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.submit()

    def submit(self) -> None:
        name = self.name_input.value.strip()
        if not name:
            return  # Require class name

        session = self.app.db_session  # type: ignore
        semester = get_semester_by_name(session, self.semester_name)

        # Add the class
        add_class_to_semester(session, name, semester)  # type: ignore
        session.commit()

        # Pop the screen and return
        self.app.pop_screen()


class ClassScreen(Screen):
    """
    Shows all the classes for a given semester
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("a", "add", "Add semester"),
        ("r", "remove", "Remove semester"),
    ]

    def __init__(self, semester_name: str) -> None:
        super().__init__()
        self.db_session: Session = self.app.db_session  # type: ignore
        self.semester_name = semester_name

    def compose(self) -> ComposeResult:
        yield Header()
        self.class_table: DataTable = DataTable()
        self.class_table.add_columns("Name")
        self.class_table.cursor_type = "row"
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
        row = self.class_table.get_row_at(row_index)
        class_name = row[0]
        remove_class_by_name(self.db_session, class_name)
        self.db_session.commit()
        self.refresh_table()

    def refresh_table(self) -> None:
        semester = get_semester_by_name(self.db_session, self.semester_name)

        self.class_table.clear()
        for cls in get_all_classes_for_semester(self.db_session, semester):
            self.class_table.add_row(cls.name)

    def on_screen_resume(self) -> None:
        # Called when returning from AddSemesterScreen
        self.refresh_table()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Open a new ExamScreen for the selected class
        """
        row_index = self.class_table.cursor_row
        if row_index is None:
            return

        class_name = self.class_table.get_row_at(row_index)[0]
        self.app.push_screen(ExamScreen(class_name))
