from textual.app import App
from examtracker.database import (
    create_database_engine,
)
from sqlalchemy.orm import Session
from examtracker.screens.semesterscreen import SemesterScreen

class ExamTracker(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen(SemesterScreen())

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.db_engine = create_database_engine("test.db")
        self.db_session = Session(self.db_engine)

    def quit(self) -> None:
        self.db_session.close()
        self.exit()
