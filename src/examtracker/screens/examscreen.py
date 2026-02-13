from textual.app import ComposeResult, Screen
from textual.widgets import Footer, Header, DataTable, Input, Label
from examtracker.database import (
    get_all_exams_for_class,
    get_class_by_id,
    add_exam_to_class,
    remove_exam_by_id,
    get_exam_by_id,
)
from textual.containers import Vertical
from textual import on


class EditExamScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, exam_id: int, **kwargs):
        super().__init__(**kwargs)
        self.exam_id = exam_id
        self.db_session = self.app.db_session  # type:ignore

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label("Edit Exam")
            # Inputs for the class
            self.name_input = Input(placeholder="Exam Name", id="name")
            yield self.name_input

            self.max_input = Input(placeholder="Exam Max Points (optional)", id="max")
            yield self.max_input
            self.score_input = Input(
                placeholder="Exam Scored Points (optional)", id="score"
            )
            yield self.score_input

        yield Footer()

    def on_mount(self) -> None:
        exam = get_exam_by_id(self.db_session, self.exam_id)

        self.name_input.value = exam.name
        self.max_input.value = str(exam.max_points)
        self.score_input.value = str(exam.scored_points)

        self.name_input.focus()

    @on(Input.Submitted)
    def submit(self) -> None:
        name = self.name_input.value.strip()
        if not name:
            return  # Require class name

        # Optional exam points
        try:
            max_points = int(self.max_input.value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            max_points = 0

        try:
            scored_points = int(self.score_input.value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            scored_points = 0

        exam = get_exam_by_id(self.db_session, self.exam_id)
        exam.name = name
        exam.max_points = max_points
        exam.scored_points = scored_points

        self.db_session.commit()

        self.app.pop_screen()


class AddExamScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, class_id: int, **kwargs):
        super().__init__(**kwargs)
        self.class_id = class_id
        self.db_session = self.app.db_session  # type: ignore
        self.class_name = get_class_by_id(self.db_session, self.class_id).name

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label(f"Add Exam to: {self.class_name}")
            # Inputs for the class
            self.name_input = Input(placeholder="Exam Name", id="name")
            yield self.name_input

            # Optional exam fields
            self.max_input = Input(placeholder="Exam Max Points (optional)", id="max")
            yield self.max_input
            self.score_input = Input(
                placeholder="Exam Scored Points (optional)", id="score"
            )
            yield self.score_input

        yield Footer()

    def on_mount(self) -> None:
        self.name_input.focus()

    @on(Input.Submitted)
    def submit(self) -> None:
        name = self.name_input.value.strip()
        if not name:
            return  # Require class name

        try:
            max_points = int(self.max_input.value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            max_points = 0

        try:
            scored_points = int(self.score_input.value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            scored_points = 0

        class_obj = get_class_by_id(self.db_session, self.class_id)

        # Add the class
        add_exam_to_class(self.db_session, name, max_points, scored_points, class_obj)
        self.db_session.commit()

        # Pop the screen and return
        self.app.pop_screen()


class ExamScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("a", "add", "Add exam"),
        ("ctrl+r", "remove", "Remove exam"),
    ]

    def __init__(self, class_id: int, **kwargs):
        super().__init__(**kwargs)
        self.class_id = class_id
        self.db_session = self.app.db_session  # type: ignore
        self.class_name = get_class_by_id(self.db_session, self.class_id).name

    def compose(self) -> ComposeResult:
        yield Header()

        self.exam_table: DataTable = DataTable()
        self.exam_table.add_columns("ID", "Name", "Max_points", "Scored_points", "%")
        self.exam_table.cursor_type = "row"
        self.exam_table.border_title = f"Exams completed for: {self.class_name}"
        yield self.exam_table

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_table()
        self.exam_table.focus()

    def action_add(self) -> None:
        self.app.push_screen(AddExamScreen(self.class_id))

    def action_remove(self) -> None:
        row_index = self.exam_table.cursor_row
        if row_index is None:
            return
        if not self.exam_table.is_valid_row_index(row_index):
            return
        row = self.exam_table.get_row_at(row_index)
        exam_id = row[0]
        remove_exam_by_id(self.db_session, exam_id)
        self.db_session.commit()
        self.refresh_table()

    def refresh_table(self) -> None:
        class_obj = get_class_by_id(self.db_session, self.class_id)

        self.exam_table.clear()
        for cls in get_all_exams_for_class(self.db_session, class_obj):
            if cls.max_points == 0:
                proc = 0.0
            else:
                proc = (cls.scored_points / cls.max_points) * 100

            self.exam_table.add_row(
                cls.exam_id, cls.name, cls.max_points, cls.scored_points, proc
            )

    def on_screen_resume(self) -> None:
        # Called when returning from AddSemesterScreen
        self.refresh_table()

    @on(DataTable.RowSelected)
    def edit_exam(self, event: DataTable.RowSelected) -> None:
        row_index = self.exam_table.cursor_row
        if row_index is None:
            return

        exam_id = self.exam_table.get_row_at(row_index)[0]
        self.app.push_screen(EditExamScreen(exam_id))
