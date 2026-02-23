from hypothesis import given
from hypothesis.strategies import integers, text


# ------------- Semester tests -------------
@given(text())
def test_add_get_semester(name: str) -> None:
    pass


def test_get_nonexistant_semester() -> None:
    pass


# ------------- Class tests -------------
@given(text())
def test_add_get_class(name: str) -> None:
    pass


def test_get_nonexistant_class() -> None:
    pass


# ------------- Exam tests -------------
@given(name=text(), max_points=integers(), scored_points=integers())
def test_add_get_exam(name: str, max_points: int, scored_points: int) -> None:
    pass


def test_get_nonexistant_exam() -> None:
    pass
