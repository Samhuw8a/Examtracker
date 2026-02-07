from examtracker.database_scheme import Exam, Base, Class, Semester

from sqlalchemy import create_engine, Engine  # type:ignore
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///test.db", echo=True)


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def get_semester_by_name(session: Session) -> Semester:
    return NotImplemented


def get_class_by_name(session: Session) -> Semester:
    return NotImplemented


def add_class_to_semester(
    session: Session, class_obj: Class, semster_obj: Semester
) -> None:
    return NotImplemented


def add_exam_to_class(session: Session, exam_obj: Exam, class_obj: Class) -> None:
    return NotImplemented
