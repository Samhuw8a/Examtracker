from __future__ import annotations

from textual import on
from textual.app import ComposeResult, Screen
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, Label


class SingleInputScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]
    input_button: Input = Input()
    label_text: str = ""

    def __init__(self) -> None:
        super().__init__()
        self.db_session = self.app.db_session  # type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label(self.label_text)
            yield self.input_button
        yield Footer()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.submit()  # type: ignore


class TrippleInputScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]
    input_button1: Input = Input()
    input_button2: Input = Input()
    input_button3: Input = Input()
    label_text: str = ""

    def __init__(self) -> None:
        super().__init__()
        self.db_session = self.app.db_session  # type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label(self.label_text)
            yield self.input_button1
            yield self.input_button2
            yield self.input_button3
        yield Footer()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.submit()  # type: ignore


class DoubleInputScreen(Screen):
    BINDINGS = [
        ("escape", "app.pop_screen", "Cancel"),
    ]
    input_button1: Input = Input()
    input_button2: Input = Input()
    label_text: str = ""

    def __init__(self) -> None:
        super().__init__()
        self.db_session = self.app.db_session  # type: ignore

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label(self.label_text)
            yield self.input_button1
            yield self.input_button2
        yield Footer()

    @on(Input.Submitted)
    def input_submitted(self, event: Input.Submitted) -> None:
        self.submit()  # type: ignore
