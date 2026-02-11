from textual.app import App
from sqlalchemy.orm import Session
from examtracker.screens.semesterscreen import SemesterScreen
from examtracker.settings import Settings
from sqlalchemy import Engine  # type:ignore


class ExamTracker(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]
    CSS_PATH = "/Users/samuel/Repositories/Examtracker/data/style.css"

    def on_mount(self) -> None:
        self.push_screen(SemesterScreen())
        # self.stylesheet.read(self.config.css_path)

    def __init__(self, db_engine: Engine, config: Settings, **kwargs) -> None:
        super().__init__(**kwargs)
        self.db_session = Session(db_engine)
        self.config = config

    def quit(self) -> None:
        self.db_session.commit()
        self.db_session.close()
        self.exit()
