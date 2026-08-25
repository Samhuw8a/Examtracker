from __future__ import annotations

from textual import on
from textual.app import ComposeResult, Screen
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Label


class MultiInputScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]
    label_text: str = ""

    def __init__(self, n: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.buttons: list[Input] = []
        self.db_session = self.app.db_session  # type: ignore
        for i in range(n):
            self.buttons.append(Input())

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label(self.label_text)
            for i in range(len(self.buttons)):
                yield self.buttons[i]
        yield Footer()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.submit()  # type: ignore
