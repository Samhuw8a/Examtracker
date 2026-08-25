"""
Defining the database tables and entries
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import (  # type: ignore
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Exam(Base):
    __tablename__ = "exams"
    exam_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    max_points: Mapped[float]
    scored_points: Mapped[float]
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.class_id"))
    class_: Mapped["Class"] = relationship(back_populates="exams")  # type:ignore

    def __repr__(self) -> str:
        return f"ID:{self.exam_id}|name:{self.name}|{self.max_points}|{self.scored_points}|Class:{self.class_id}"


class Class(Base):
    __tablename__ = "classes"
    class_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    exam_grade: Mapped[float | None]
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester.semester_id"))
    semester: Mapped["Semester"] = relationship(back_populates="classes")  # type:ignore

    exams: Mapped[list["Exam"]] = relationship(
        back_populates="class_",
        cascade="all, delete-orphan",
    )  # type: ignore

    def __repr__(self) -> str:
        return f"ID:{self.class_id}|name:{self.name}|Semester:{self.semester_id}"


class Semester(Base):
    __tablename__ = "semester"
    semester_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    classes: Mapped[list["Class"]] = relationship(
        back_populates="semester",
        cascade="all, delete-orphan",
    )  # type: ignore

    def __repr__(self) -> str:
        return f"ID:{self.semester_id}|name:{self.name}"
