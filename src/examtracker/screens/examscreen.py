import math

from rich.text import Text
from textual import on
from textual.app import ComposeResult, Screen
from textual.widgets import Footer, Header

from examtracker.database import (
    add_exam_to_class,
    get_all_exams_for_class,
    get_class_by_id,
    get_exam_by_id,
    remove_exam_by_id,
)
from examtracker.screens.inputscreens import MultiInputScreen
from examtracker.textual_utils.vimtable import VimTable


def proc_color(value: float) -> str:
    if value >= 75.0:
        return "#03fc20"
    elif value >= 50:
        return "#fcf003"
    else:
        return "#fc1c03"


class EditExamScreen(MultiInputScreen):
    def __init__(self, exam_id: int, **kwargs):
        super().__init__(4, **kwargs)
        self.label_text = "Edit exam"
        self.exam_id = exam_id
        self.db_session = self.app.db_session  # type: ignore

    def on_mount(self) -> None:
        exam = get_exam_by_id(self.db_session, self.exam_id)

        self.buttons[0].value = exam.name
        self.buttons[1].value = str(exam.max_points)
        self.buttons[2].value = str(exam.scored_points)
        self.buttons[3].value = str(exam.notes)

        self.buttons[0].focus()

    def submit(self) -> None:
        name = self.buttons[0].value.strip()
        if not name:
            return  # Require class name

        # Optional exam points
        try:
            max_points = float(self.buttons[1].value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            max_points = 0

        try:
            scored_points = float(self.buttons[2].value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            scored_points = 0
        if not math.isfinite(scored_points):
            scored_points = 0

        notes = self.buttons[3].value.strip()

        exam = get_exam_by_id(self.db_session, self.exam_id)
        exam.name = name
        exam.max_points = max_points
        exam.scored_points = scored_points
        exam.notes = notes

        self.db_session.commit()

        self.app.pop_screen()


class AddExamScreen(MultiInputScreen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, class_id: int, **kwargs):
        super().__init__(4, **kwargs)
        self.db_session = self.app.db_session  # type: ignore
        self.class_id = class_id
        self.class_name = get_class_by_id(self.db_session, self.class_id).name
        self.label_text = f"Add exam to: {self.class_name}"

    def on_mount(self) -> None:
        self.buttons[0].focus()
        self.buttons[0].placeholder = "Exam Name"
        self.buttons[1].placeholder = "Max Points"
        self.buttons[2].placeholder = "Scored Points"
        self.buttons[3].placeholder = "Additional Notes"

        self.buttons[0].value = ""
        self.buttons[1].value = ""
        self.buttons[2].value = ""
        self.buttons[3].value = ""

    def submit(self) -> None:
        name = self.buttons[0].value.strip()
        if not name:
            return  # Require class name

        try:
            max_points = float(self.buttons[1].value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            max_points = 0

        try:
            scored_points = float(self.buttons[2].value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            scored_points = 0

        if not math.isfinite(scored_points):
            scored_points = 0

        notes = self.buttons[3].value.strip()

        class_obj = get_class_by_id(self.db_session, self.class_id)

        # Add the class
        add_exam_to_class(
            self.db_session, name, max_points, scored_points, notes, class_obj
        )
        self.db_session.commit()

        # Pop the screen and return
        self.app.pop_screen()


class ExamScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("a", "add", "Add exam"),
        ("e", "edit", "Edit exam"),
        ("ctrl+r", "remove", "Remove exam"),
    ]

    def __init__(self, class_id: int, **kwargs):
        super().__init__(**kwargs)
        self.class_id = class_id
        self.db_session = self.app.db_session  # type: ignore
        self.class_name = get_class_by_id(self.db_session, self.class_id).name

    def compose(self) -> ComposeResult:
        yield Header()

        self.exam_table: VimTable = VimTable()
        self.exam_table.add_columns(
            "ID", "Name", "Max_points", "Scored_points", "%", "Additional Notes"
        )
        self.exam_table.cursor_type = "cell"
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
        for exm in get_all_exams_for_class(self.db_session, class_obj):
            if exm.max_points == 0:
                proc = 0.0
            else:
                proc = round((exm.scored_points / exm.max_points) * 100, 2)

            proc_text = Text(str(proc), style=proc_color(proc))
            self.exam_table.add_row(
                exm.exam_id,
                exm.name,
                exm.max_points,
                exm.scored_points,
                proc_text,
                exm.notes,
            )

    def on_screen_resume(self) -> None:
        # Called when returning from AddSemesterScreen
        self.refresh_table()

    @on(VimTable.CellSelected)
    def action_edit(self) -> None:
        row_index = self.exam_table.cursor_row
        if row_index is None:
            return
        if not self.exam_table.is_valid_row_index(row_index):
            return

        exam_id = self.exam_table.get_row_at(row_index)[0]
        self.app.push_screen(EditExamScreen(exam_id))
