from textual.app import App, ComposeResult
from sqlalchemy.orm import Session
from examtracker.screens.semesterscreen import SemesterScreen
from examtracker.settings import Settings
from sqlalchemy import Engine  # type:ignore


class ExamTracker(App):
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit"),
    ]
    # CSS_PATH = "/Users/samuel/Repositories/Examtracker/data/style.css"

    def compose(self) -> ComposeResult:
        yield SemesterScreen()

    def on_mount(self) -> None:
        self.push_screen(SemesterScreen())
        self.stylesheet.read(self.config.css_path)

    def __init__(self, db_engine: Engine, config: Settings, **kwargs) -> None:
        super().__init__(**kwargs)
        self.db_session = Session(db_engine)
        self.config = config

    def quit(self) -> None:
        self.db_session.commit()
        self.db_session.close()
        self.exit()

    def pop_screen(self):
        # Only pop if there is more than 1 screen (not including the blank screen)
        if len(self.screen_stack) > 2:
            super().pop_screen()
        else:
            # Ignore pop on base screen
            pass
