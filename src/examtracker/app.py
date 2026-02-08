from textual.app import App, ComposeResult, Screen
from textual.widgets import Footer, Header, DataTable, Input, Button
from examtracker.database import (
    create_database_engine,
    get_all_semester,
    add_semester,
    remove_semester_by_name,
    remove_class_by_name,
    get_all_classes_for_semester,
    get_semester_by_name,
    add_class_to_semester,
    get_all_exams_for_class,
    get_class_by_name,
    add_exam_to_class,
    remove_exam_by_id,
    get_exam_by_id,
)
from textual.containers import Vertical
from textual import on
from sqlalchemy.orm import Session


class EditExamScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
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

    def __init__(self, exam_id: int, **kwargs):
        super().__init__(**kwargs)
        self.exam_id = exam_id

    def on_mount(self) -> None:
        session = self.app.db_session  # type:ignore
        exam = get_exam_by_id(session, self.exam_id)

        self.name_input.value = exam.name
        self.max_input.value = str(exam.max_points)
        self.score_input.value = str(exam.scored_points)

        self.name_input.focus()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.submit()

    def submit(self) -> None:
        name = self.name_input.value.strip()
        if not name:
            return  # Require class name

        # Optional exam points
        try:
            max_points = int(self.max_input.value.strip())
            scored_points = int(self.score_input.value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            max_points = 0
            scored_points = 0

        session = self.app.db_session  # type: ignore
        exam = get_exam_by_id(session, self.exam_id)
        exam.name = name
        exam.max_points = max_points
        exam.scored_points = scored_points

        session.commit()

        # Pop the screen and return
        self.app.pop_screen()


class AddExamScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, class_name: str, **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
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

    # Submit on Enter from any Input
    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.submit()

    def submit(self) -> None:
        name = self.name_input.value.strip()
        if not name:
            return  # Require class name

        # Optional exam points
        try:
            max_points = int(self.max_input.value.strip())
            scored_points = int(self.score_input.value.strip())
        except ValueError:
            # Ignore invalid numbers for now
            max_points = 0
            scored_points = 0

        session = self.app.db_session  # type: ignore
        class_obj = get_class_by_name(session, self.class_name)

        # Add the class
        add_exam_to_class(session, name, max_points, scored_points, class_obj)
        session.commit()

        # Pop the screen and return
        self.app.pop_screen()


class ExamScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("a", "add", "Add exam"),
        ("r", "remove", "Remove exam"),
        ("q", "quit", "Quit"),
    ]

    def action_add(self) -> None:
        self.app.push_screen(AddExamScreen(self.class_name))

    def action_remove(self) -> None:
        row_index = self.exam_table.cursor_row
        if row_index is None:
            return
        row = self.exam_table.get_row_at(row_index)
        exam_id = row[0]
        remove_exam_by_id(self.app.db_session, exam_id)  # type: ignore
        self.app.db_session.commit()  # type:ignore
        self.refresh_table()

    def __init__(self, class_name: str, **kwargs):
        super().__init__(**kwargs)
        self.class_name = class_name

    def compose(self) -> ComposeResult:
        yield Header()

        self.exam_table: DataTable = DataTable()
        self.exam_table.add_columns("ID", "Name", "Max_points", "Scored_points", "%")
        self.exam_table.cursor_type = "row"
        yield self.exam_table

        yield Footer()

    def on_mount(self) -> None:
        self.refresh_table()
        self.exam_table.focus()

    def refresh_table(self) -> None:
        session = self.app.db_session
        class_obj = get_class_by_name(session, self.class_name)

        self.exam_table.clear()
        for cls in get_all_exams_for_class(session, class_obj):
            proc = (cls.scored_points / cls.max_points) * 100
            self.exam_table.add_row(
                cls.exam_id, cls.name, cls.max_points, cls.scored_points, proc
            )

    def on_screen_resume(self) -> None:
        # Called when returning from AddSemesterScreen
        self.refresh_table()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_index = self.exam_table.cursor_row
        if row_index is None:
            return

        exam_id = self.exam_table.get_row_at(row_index)[0]
        self.app.push_screen(EditExamScreen(exam_id))


class AddClassScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def __init__(self, semester_name: str, **kwargs):
        super().__init__(**kwargs)
        self.semester_name = semester_name

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
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
    BINDINGS = [
        ("escape", "app.pop_screen", "Back"),
        ("a", "add", "Add semester"),
        ("r", "remove", "Remove semester"),
        ("q", "quit", "Quit"),
    ]

    def refresh_table(self) -> None:
        session = self.app.db_session
        semester = get_semester_by_name(session, self.semester_name)

        self.class_table.clear()
        for cls in get_all_classes_for_semester(session, semester):
            self.class_table.add_row(cls.name)

    def on_screen_resume(self) -> None:
        # Called when returning from AddSemesterScreen
        self.refresh_table()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_index = self.class_table.cursor_row
        if row_index is None:
            return

        class_name = self.class_table.get_row_at(row_index)[0]
        self.app.push_screen(ExamScreen(class_name))


class AddSemesterScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
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

        add_semester(self.app.db_session, name)  # type:ignore
        self.app.db_session.commit()  # type:ignore

        # tell the previous screen to refresh
        self.app.pop_screen()


class SemesterScreen(Screen):
    BINDINGS = [
        ("a", "add", "Add semester"),
        ("r", "remove", "Remove semester"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        self.table: DataTable = DataTable(classes="semester_list")
        self.table.add_columns("Name")
        self.table.cursor_type = "row"
        yield self.table
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_table()
        self.table.focus()

    def refresh_table(self) -> None:
        self.table.clear()
        for sem in get_all_semester(self.app.db_session):  # type: ignore
            self.table.add_row(sem.name)

    def action_add(self) -> None:
        self.app.push_screen("add_semester")

    def action_remove(self) -> None:
        row_index = self.table.cursor_row
        if row_index is None:
            return
        row = self.table.get_row_at(row_index)
        semester_name = row[0]
        remove_semester_by_name(self.app.db_session, semester_name)  # type:ignore
        self.app.db_session.commit()  # type:ignore
        self.refresh_table()

    def on_screen_resume(self) -> None:
        # Called when returning from AddSemesterScreen
        self.refresh_table()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_index = self.table.cursor_row
        if row_index is None:
            return

        semester_name = self.table.get_row_at(row_index)[0]
        self.app.push_screen(ClassScreen(semester_name))


class ExamTracker(App):
    SCREENS = {
        "semester": SemesterScreen,
        "add_semester": AddSemesterScreen,
        "classes": ClassScreen,  # type:ignore
    }
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Footer()
        yield Header()

    def on_mount(self):
        self.db_engine = create_database_engine("test.db")
        self.db_session = Session(self.db_engine)
        self.install_screen(SemesterScreen(), name="Semesters")
        self.install_screen(AddSemesterScreen(), name="addSemesters")
        self.push_screen("semester")

    def quit(self) -> None:
        self.db_session.close()
        self.exit()
