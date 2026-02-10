from textual.app import App
from sqlalchemy.orm import Session
from examtracker.screens.semesterscreen import SemesterScreen
from examtracker.settings import Settings
from sqlalchemy import Engine  # type:ignore


class ExamTracker(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen(SemesterScreen())

    def __init__(self, db_engine: Engine, **kwargs) -> None:
        super().__init__(**kwargs)
        self.db_session = Session(db_engine)

    def quit(self) -> None:
        self.db_session.close()
        self.exit()
