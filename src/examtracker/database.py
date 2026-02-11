"""
Database related functions for getting and adding entries
"""

from examtracker.database_scheme import Exam, Base, Class, Semester

from sqlalchemy import create_engine, Engine, inspect  # type:ignore
from sqlalchemy.orm import Session

from typing import List


def create_database_engine(path: str) -> Engine:
    engine = create_engine("sqlite:////" + str(path), echo=False)
    inspector = inspect(engine)

    if not inspector.get_table_names():
        create_tables(engine)

    return engine


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(engine)


def get_semester_by_name(session: Session, name: str) -> Semester:
    return session.query(Semester).filter_by(name=name).one()


def add_semester(session: Session, name: str) -> None:
    semester_obj = Semester(name=name)
    session.add(semester_obj)
    session.flush


def get_class_by_id(session: Session, class_id: int) -> Semester:
    return session.query(Class).filter_by(class_id=class_id).one()


def get_exam_by_id(session: Session, exam_id: int) -> Semester:
    return session.query(Exam).filter_by(exam_id=exam_id).one()


def add_class_to_semester(
    session: Session, class_name: str, semster_obj: Semester
) -> None:
    class_obj = Class(name=class_name, semester_id=semster_obj.semester_id)
    session.add(class_obj)
    session.flush()


def add_exam_to_class(
    session: Session, name: str, max_points: int, scored_points: int, class_obj: Class
) -> None:
    exam_obj = Exam(
        name=name,
        max_points=max_points,
        scored_points=scored_points,
        class_id=class_obj.class_id,
    )
    session.add(exam_obj)
    session.flush()


def get_all_exams_for_class(session: Session, class_obj: Class) -> List[Exam]:
    return session.query(Exam).filter_by(class_id=class_obj.class_id).all()


def get_all_semester(session: Session) -> List[Semester]:
    return session.query(Semester).all()


def get_all_classes_for_semester(
    session: Session, semster_obj: Semester
) -> List[Semester]:
    return session.query(Class).filter_by(semester_id=semster_obj.semester_id).all()


def remove_semester_by_name(session: Session, name: str) -> None:
    sem = get_semester_by_name(session, name)
    session.delete(sem)  # type:ignore


def remove_class_by_id(session: Session, id: int) -> None:
    cls = get_class_by_id(session, id)
    session.delete(cls)  # type:ignore


def remove_exam_by_id(session: Session, exam_id: int) -> None:
    exam_obj = get_exam_by_id(session, exam_id)
    session.delete(exam_obj)  # type: ignore


def main() -> int:
    engine: Engine = create_database_engine("test.db")
    create_tables(engine)
    # session = Session(engine)
    # # add_semester(session, "FS25")
    # # remove_semester_by_name(session, "FS25")
    # # print(get_all_semester(session))
    # sem = get_semester_by_name(session, "HS24")
    # add_class_to_semester(session, "Eprog", sem)
    # # cls = get_class_by_name(session,"Eprog")
    # # print(get_all_exams_for_class(session, cls))
    # session.commit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
