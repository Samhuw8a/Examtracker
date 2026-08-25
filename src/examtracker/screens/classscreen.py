from __future__ import annotations

import math

from sqlalchemy.orm import Session
from textual import on
from textual.app import ComposeResult, Screen
from textual.widgets import DataTable, Footer, Header

from examtracker.database import (
    add_class_to_semester,
    get_all_classes_for_semester,
    get_class_by_id,
    get_semester_by_name,
    remove_class_by_id,
)
from examtracker.screens.examscreen import ExamScreen
from examtracker.screens.inputscreens import MultiInputScreen
from examtracker.textual_utils.vimtable import VimTable


class AddClassScreen(MultiInputScreen):
    def __init__(self, semester_name: str, **kwargs) -> None:
        super().__init__(2, **kwargs)
        self.semester_name = semester_name
        self.label_text = f"Add class to: {self.semester_name}"

    def on_mount(self) -> None:
        self.buttons[0].placeholder = "class name"
        self.buttons[0].value = ""
        self.buttons[1].placeholder = "exam_score"
        self.buttons[1].value = ""
        self.buttons[0].focus()

    # Submit on Enter from any Input
    def submit(self) -> None:
        name = self.buttons[0].value.strip()
        exam_score = self.buttons[1].value.strip()
        try:
            score = float(exam_score)
        except ValueError:
            score = None
        if not name:
            return  # Require class name
        semester = get_semester_by_name(self.db_session, self.semester_name)
        # Add the class
        add_class_to_semester(self.db_session, name, semester, score)  # type: ignore
        self.db_session.commit()

        # Pop the screen and return
        self.app.pop_screen()


class EditClassScreen(MultiInputScreen):
    def __init__(self, class_id: int, **kwargs) -> None:
        super().__init__(2, **kwargs)
        self.class_id = class_id
        self.label_text = "Edit class"

    def on_mount(self) -> None:
        class_obj = get_class_by_id(self.db_session, self.class_id)
        self.buttons[0].value = class_obj.name
        if class_obj.exam_grade is not None:
            self.buttons[1].value = str(class_obj.exam_grade)
        else:
            self.buttons[1].value = ""
        self.buttons[0].focus()

    # Submit on Enter from any Input
    def submit(self) -> None:
        name = self.buttons[0].value.strip()
        exam_score = self.buttons[1].value.strip()
        try:
            score = float(exam_score)
        except ValueError:
            score = None

        if isinstance(score, float) and not math.isfinite(score):
            score = None
        if not name:
            return  # Require class name

        class_obj = get_class_by_id(self.db_session, self.class_id)
        # Add the class
        class_obj.name = name
        class_obj.exam_grade = score
        self.db_session.commit()

        # Pop the screen and return
        self.app.pop_screen()


class ClassScreen(Screen):
    """
    Shows all the classes for a given semester
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("a", "add", "Add class"),
        ("e", "edit", "Edit class"),
        ("ctrl+r", "remove", "Remove class"),
    ]

    def __init__(self, semester_name: str) -> None:
        super().__init__()
        self.db_session: Session = self.app.db_session  # type: ignore
        self.semester_name = semester_name

    def compose(self) -> ComposeResult:
        yield Header()
        self.class_table: VimTable = VimTable()
        self.class_table.add_columns("ID", "Name", "Exam grade")
        self.class_table.cursor_type = "row"
        self.class_table.border_title = f"classes for: {self.semester_name}"
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

    def action_edit(self) -> None:
        row_index = self.class_table.cursor_row
        if row_index is None:
            return
        if not self.class_table.is_valid_row_index(row_index):
            return

        class_id = self.class_table.get_row_at(row_index)[0]
        self.app.push_screen(EditClassScreen(class_id))

    def refresh_table(self) -> None:
        semester = get_semester_by_name(self.db_session, self.semester_name)

        self.class_table.clear()
        for cls in get_all_classes_for_semester(self.db_session, semester):
            score = cls.exam_grade
            str_score = ""
            if score is not None:
                str_score = cls.exam_grade
            self.class_table.add_row(cls.class_id, cls.name, str_score)

    def on_screen_resume(self) -> None:
        self.refresh_table()

    @on(VimTable.RowSelected)
    def open_exam(self, event: DataTable.RowSelected) -> None:
        row_index = self.class_table.cursor_row
        if row_index is None:
            return

        class_id = self.class_table.get_row_at(row_index)[0]
        self.app.push_screen(ExamScreen(class_id))
