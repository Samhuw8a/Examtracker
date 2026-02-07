from sqlalchemy.orm import Mapped, mapped_column  # type:ignore
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, relationship  # type:ignore

from typing import List


class Base(DeclarativeBase):
    pass


class Exam(Base):
    __tablename__ = "exams"
    exam_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(5))
    max_points: Mapped[int]
    scored_points: Mapped[int]
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.class_id"))


class Class(Base):
    __tablename__ = "classes"
    class_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(10), unique=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester.semester_id"))
    exams: Mapped[List["Exam"]] = relationship()  # type: ignore


class Semester(Base):
    __tablename__ = "semester"
    semester_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(10), unique=True)
    classes: Mapped[List["Class"]] = relationship()  # type: ignore
