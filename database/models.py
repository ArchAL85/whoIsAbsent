from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, VARCHAR, DATETIME
from sqlalchemy.orm import relationship
from database.db import Base


class Reasons(Base):
    __tablename__ = "Reasons"

    reason_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    title = Column(VARCHAR(50), nullable=False)
    description = Column(String, nullable=False)


class Users(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    telegram_id = Column(Integer)
    edu_tatar_id = Column(Integer)
    surname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    middlename = Column(String)

    def get_name(self):
        return f"{self.surname} {self.name}"


class Absent(Base):
    __tablename__ = "Absents"

    absent_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    reason_id = Column(Integer, ForeignKey("Reasons.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.id"), nullable=False)
    date = Column(DATETIME, default=now())


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    teaching_class = Column(Integer, ForeignKey("school_classes.id"), nullable=False)
    date = Column(String, nullable=False)


class SchoolClass(Base):
    __tablename__ = "school_classes"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    class_number = Column(Integer, nullable=False)
    liter = Column(VARCHAR(1), nullable=False)

    students = relationship("Student", back_populates="school_class")


class Schedule(Base):
    __tablename__ = "schedule"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    day_of_week = Column(String, nullable=False)
    index_number = Column(Integer, nullable=False)
    teaching_class = Column(Integer, ForeignKey("school_classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)


class Subjects(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    title = Column(String, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    surname = Column(String, nullable=False)
    name = Column(String, nullable=False)
    patronymic = Column(String, nullable=False)
    telegram_id = Column(Integer, unique=True)

    link = relationship("InvitationLink", back_populates="teacher")

    def get_full_name(self):
        return f"{self.surname} {self.name} {self.patronymic}"


class InvitationLink(Base):
    __tablename__ = "invitation_links"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    for_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    code = Column(String, nullable=False)
    is_used = Column(Boolean, nullable=False, default=False)

    teacher = relationship("Teacher", back_populates="link")
