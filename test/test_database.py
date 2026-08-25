from contextlib import contextmanager

import pytest
from hypothesis import given, settings
from hypothesis.strategies import floats, integers, text
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

# Import your database functions and schema
# Ensure 'examtracker' is in your python path
from examtracker.database import (
    add_class_to_semester,
    add_exam_to_class,
    add_semester,
    create_tables,
    get_all_classes_for_semester,
    get_all_exams_for_class,
    get_all_semester,
    get_class_by_id,
    get_exam_by_id,
    get_semester_by_name,
    remove_class_by_id,
    remove_exam_by_id,
    remove_semester_by_name,
)

# --- Database Setup Logic ---


@contextmanager
def temp_db():
    """
    Creates a fresh, in-memory database for every Hypothesis iteration.
    This prevents data leakage between tests and satisfies Hypothesis health checks.
    """
    # Using :memory: is significantly faster for property-based testing
    engine = create_engine("sqlite:///:memory:")
    # Base.metadata.create_all(engine)
    create_tables(engine)
    with Session(engine) as session:
        yield session


# Helper to filter out null bytes which SQLite cannot store in strings
valid_text = text(min_size=1).filter(lambda x: "\x00" not in x)

# ------------- Semester tests -------------


@given(name=valid_text)
@settings(deadline=None)
def test_add_get_semester(name: str) -> None:
    with temp_db() as session:
        add_semester(session, name)
        session.commit()

        retrieved = get_semester_by_name(session, name)
        assert retrieved.name == name


def test_get_nonexistant_semester() -> None:
    with temp_db() as session:
        with pytest.raises(Exception):  # SQLAlchemy raises NoResultFound for .one()
            get_semester_by_name(session, "Does Not Exist")


def test_get_all_semester_logic() -> None:
    with temp_db() as session:
        add_semester(session, "Sem1")
        add_semester(session, "Sem2")
        session.commit()

        semesters = get_all_semester(session)
        assert len(semesters) == 2


@given(name=valid_text)
@settings(deadline=None)
def test_semester_name_uniqueness(name: str) -> None:
    """
    Property-based test to ensure no two semesters can share the same generated name.
    """
    with temp_db() as session:
        # First insertion
        add_semester(session, name)
        session.commit()

        # Second insertion of the exact same name
        with pytest.raises(IntegrityError):
            add_semester(session, name)


# ------------- Class tests -------------


@given(name=valid_text)
@settings(deadline=None)
def test_add_get_class(name: str) -> None:
    with temp_db() as session:
        # Setup: Classes require a parent Semester
        add_semester(session, "Base Semester")
        sem = get_semester_by_name(session, "Base Semester")

        add_class_to_semester(session, name, sem)
        session.commit()

        # Verify via relationship
        classes = get_all_classes_for_semester(session, sem)
        assert any(c.name == name for c in classes)


@given(name=valid_text, score=floats())
@settings(deadline=None)
def test_add_get_class_with_score(name: str, score: float) -> None:
    with temp_db() as session:
        # Setup: Classes require a parent Semester
        add_semester(session, "Base Semester")
        sem = get_semester_by_name(session, "Base Semester")

        add_class_to_semester(session, name, sem, score)
        session.commit()

        # Verify via relationship
        classes = get_all_classes_for_semester(session, sem)
        assert any(c.name == name for c in classes)


def test_get_nonexistant_class() -> None:
    with temp_db() as session:
        with pytest.raises(Exception):
            get_class_by_id(session, 999)


# ------------- Exam tests -------------


@given(
    name=valid_text,
    max_points=floats(
        min_value=0, max_value=10000, allow_infinity=False, allow_nan=False
    ),
    scored_points=floats(
        min_value=0, max_value=10000, allow_infinity=False, allow_nan=False
    ),
    notes=text(),
)
@settings(deadline=None)
def test_add_get_exam(
    name: str, max_points: float, scored_points: float, notes: str
) -> None:
    with temp_db() as session:
        # Setup Hierarchy: Semester -> Class
        add_semester(session, "S1")
        sem = get_semester_by_name(session, "S1")
        add_class_to_semester(session, "C1", sem)
        cls = sem.classes[0]

        add_exam_to_class(session, name, max_points, scored_points, notes, cls)
        session.commit()

        # Verify exam data
        exams = get_all_exams_for_class(session, cls)
        assert len(exams) == 1
        assert exams[0].name == name
        assert exams[0].max_points == max_points
        assert exams[0].scored_points == scored_points
        assert exams[0].notes == notes


def test_get_nonexistant_exam() -> None:
    with temp_db() as session:
        with pytest.raises(Exception):
            get_exam_by_id(session, 888)


# ------------- Cascade and Specific Deletion Tests -------------


def test_remove_semester_cascades_to_classes_and_exams() -> None:
    """Tests that deleting a semester removes all nested classes and exams."""
    with temp_db() as session:
        # 1. Setup Hierarchy: Semester -> Class -> Exam
        add_semester(session, "Delete Cascade Test")
        sem = get_semester_by_name(session, "Delete Cascade Test")

        add_class_to_semester(session, "Nested Class", sem)
        cls = sem.classes[0]

        add_exam_to_class(session, "Nested Exam", 100, 90, "notes", cls)
        session.commit()

        # Capture IDs to verify deletion later
        class_id = cls.class_id
        exam_id = cls.exams[0].exam_id

        # 2. Action: Remove the parent Semester
        remove_semester_by_name(session, "Delete Cascade Test")
        session.commit()

        # 3. Verify: Semester is gone
        with pytest.raises(Exception):
            get_semester_by_name(session, "Delete Cascade Test")

        # 4. Verify: Children are gone (Assuming Cascade Delete is set in schema)
        with pytest.raises(Exception):
            get_class_by_id(session, class_id)
        with pytest.raises(Exception):
            get_exam_by_id(session, exam_id)


def test_remove_class_by_id_logic() -> None:
    """Tests that a class is removed without affecting the parent semester."""
    with temp_db() as session:
        add_semester(session, "Persistence Sem")
        sem = get_semester_by_name(session, "Persistence Sem")
        add_class_to_semester(session, "Target Class", sem)
        session.commit()

        class_id = sem.classes[0].class_id

        remove_class_by_id(session, class_id)
        session.commit()

        # Verify class is gone but semester remains
        with pytest.raises(Exception):
            get_class_by_id(session, class_id)
        assert get_semester_by_name(session, "Persistence Sem") is not None


def test_remove_exam_by_id_logic() -> None:
    """Tests that an exam is removed from its parent class."""
    with temp_db() as session:
        add_semester(session, "S1")
        sem = get_semester_by_name(session, "S1")
        add_class_to_semester(session, "C1", sem)
        cls = sem.classes[0]
        add_exam_to_class(session, "Final", 100, 100, "notes", cls)
        session.commit()

        exam_id = cls.exams[0].exam_id

        remove_exam_by_id(session, exam_id)
        session.commit()

        with pytest.raises(Exception):
            get_exam_by_id(session, exam_id)
        assert len(get_all_exams_for_class(session, cls)) == 0


# ------------- Integrity & Edge Case Tests -------------


def test_empty_relationships_return_empty_list() -> None:
    """Verifies that queries return empty lists instead of errors when no children exist."""
    with temp_db() as session:
        add_semester(session, "Empty Sem")
        sem = get_semester_by_name(session, "Empty Sem")

        # Should be empty list, not an exception
        assert get_all_classes_for_semester(session, sem) == []

        add_class_to_semester(session, "Empty Class", sem)
        cls = sem.classes[0]
        assert get_all_exams_for_class(session, cls) == []


@given(pts=floats(allow_infinity=False, allow_nan=False))  # Max 32-bit signed int
def test_exam_score_boundaries(pts: int) -> None:
    """Tests that the database handles large point values correctly."""
    with temp_db() as session:
        add_semester(session, "Boundary Sem")
        sem = get_semester_by_name(session, "Boundary Sem")
        add_class_to_semester(session, "Math", sem)
        cls = sem.classes[0]

        add_exam_to_class(session, "Big Score", pts, pts, "notes", cls)
        session.commit()

        exam = get_all_exams_for_class(session, cls)[0]
        assert exam.max_points == pts
