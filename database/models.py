from sqlalchemy import Column, Integer, String, ForeignKey, VARCHAR, DateTime, PrimaryKeyConstraint, Boolean
from sqlalchemy.orm import relationship
from database.db import Base, engine
from datetime import datetime


class Reasons(Base):
    __tablename__ = "Reasons"

    reason_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    title = Column(VARCHAR(50), nullable=False)
    description = Column(String, nullable=False)
    in_or_out = Column(Boolean, nullable=False)

    absent = relationship('Absents', back_populates='reasons')


class Users(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    telegram_id = Column(Integer)
    edu_tatar_id = Column(VARCHAR(15))
    surname = Column(VARCHAR(15), nullable=False)
    name = Column(VARCHAR(15), nullable=False)
    middlename = Column(VARCHAR(15))
    code = Column(VARCHAR(15))

    absent = relationship('Absents', back_populates='users')
    classes = relationship('User_class', back_populates='users')
    cabinet = relationship("Cabinets", back_populates="users")
    role = relationship("User_role", back_populates="users")

    def get_name(self):
        return f"{self.surname} {self.name}"

    def get_full_name(self):
        return f"{self.surname} {self.name} {self.middlename}"


class Absents(Base):
    __tablename__ = "Absents"

    absent_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    reason_id = Column(Integer, ForeignKey("Reasons.reason_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    date = Column(DateTime, default=datetime.now().date())

    users = relationship('Users', back_populates='absent')
    reasons = relationship('Reasons', back_populates='absent')


class Classes(Base):
    __tablename__ = 'Classes'

    class_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    number = Column(Integer, nullable=False)
    literal = Column(VARCHAR(2), nullable=False)

    classes = relationship('User_class', back_populates='user_class')


class User_class(Base):
    __tablename__ = "User_class"

    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    class_id = Column(Integer, ForeignKey("Classes.class_id"), nullable=False)

    user_class = relationship("Classes", back_populates='classes')
    users = relationship('Users', back_populates='classes')

    __table_args__ = (
        PrimaryKeyConstraint(user_id, class_id),
    )


class Schedule(Base):
    __tablename__ = "Schedule"

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    lesson = Column(VARCHAR(50), nullable=False)
    day_of_week = Column(VARCHAR(15), nullable=False)
    index_number = Column(Integer, nullable=False)
    teacher_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    class_id = Column(Integer, ForeignKey("Classes.class_id"), nullable=False)


class Role(Base):
    __tablename__ = 'Role'

    role_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    title = Column(VARCHAR(50), nullable=False)
    description = Column(String)

    role = relationship('User_role', back_populates='about_role')


class User_role(Base):
    __tablename__ = "User_role"

    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    role_id = Column(Integer, ForeignKey("Role.role_id"), nullable=False)

    users = relationship('Users', back_populates='role')
    about_role = relationship('Role', back_populates='role')

    __table_args__ = (
        PrimaryKeyConstraint(user_id, role_id),
    )


class Cabinets(Base):
    __tablename__ = 'Cabinets'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    number = Column(VARCHAR(50), nullable=False)
    floor = Column(Integer, nullable=False)
    description = Column(String)
    user_id = Column(Integer, ForeignKey("Users.user_id"))

    users = relationship("Users", back_populates="cabinet")


class Task(Base):
    __tablename__ = 'Task'

    task_id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    start_date = Column(DateTime, default=datetime.now)
    client_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    end_date = Column(DateTime)
    employee = Column(Integer, ForeignKey("Users.user_id"))
    description = Column(String, nullable=False)
    role = Column(Integer)
    block = Column(VARCHAR(1))
    cabinet = Column(VARCHAR(50))
    get_date = Column(DateTime)
    postponed = Column(String)


# Base.metadata.create_all(engine)
