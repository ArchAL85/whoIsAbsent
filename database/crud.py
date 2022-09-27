import datetime
from sqlalchemy import or_, and_

from database.db import SessionLocal
from database.models import *

from edu_tatar.auth import EduTatar
from config import ADMIN


def load_data_from_edu_tatar():
    """Выполняется только для загрузки или обновления данных"""
    school = EduTatar(ADMIN)
    if school.connected()[0] == 'Ok':
        employee = school.get_users()
        cabinets = school.get_cabinets()
        classes = school.get_students_classes()
        students = school.get_students()

        role_id = {'Заместители': 1, 'Учитель': 4, 'Классные руководители': 6, 'Административный работник': 7,
                   'Воспитатели': 5, 'Прочие пользователи': 7, 'Специалисты': 7, 'Ученик': 8}
        session = SessionLocal()
        last = 0
        for role, users in employee.items():
            add_employee = [
                Users(user_id=count,
                      edu_tatar_id=user[3],
                      surname=user[0],
                      name=user[1],
                      middlename=user[2]) for count, user in enumerate(users, last)
            ]
            add_role = [
                User_role(user_id=count,
                          role_id=role_id[role]) for count in range(last, last + len(users))
            ]
            last += len(users)
            session.add_all(add_employee)
            session.add_all(add_role)
        add_cabinets = [
            Cabinets(number=cabinet[0],
                     floor=cabinet[2],
                     description=cabinet[1]) for cabinet in cabinets
        ]
        session.add_all(add_cabinets)
        add_classes = [
            Classes(
                class_id=class_[0],
                number=class_[1],
                literal=class_[2]
            ) for class_ in classes
        ]
        session.add_all(add_classes)
        for class_, users in students.items():
            add_students = [
                Users(
                    edu_tatar_id=edu_id,
                    surname=user[0],
                    name=user[1],
                    middlename=user[2]
                ) for edu_id, user in users.items()
            ]
            session.add_all(add_students)
        session.commit()


def load_schedule():
    """Выполняется только для загрузки или обновления расписания"""
    session = SessionLocal()
    school = EduTatar(ADMIN)
    add_lessons = []
    if school.connected()[0] == 'Ok':
        schedule = school.get_schedule()
        for class_ in schedule.keys():
            for day_of_week, lessons in schedule[class_].items():
                for i in range(len(lessons)):
                    user = get_user_by_name(lessons[i][1])
                    if type(user) == Users:
                        lesson = Schedule(
                            lesson=lessons[i][0],
                            day_of_week=day_of_week,
                            index_number=i,
                            teacher_id=user.edu_tatar_id,
                            class_id=class_
                            )
                    else:
                        for u in user:
                            lesson = Schedule(
                                lesson=lessons[i][0],
                                day_of_week=day_of_week,
                                index_number=i,
                                teacher_id=u.edu_tatar_id,
                                class_id=class_
                            )
                    add_lessons.append(lesson)
        session.add_all(add_lessons)
        session.commit()


def set_student_role():
    school = EduTatar(ADMIN)
    students = school.get_students()
    session = SessionLocal()
    for class_, students in students.items():
        add_role = [
            User_role(
                user_id=get_user(edu_id=student_id).user_id,
                role_id=8
            ) for student_id in students.keys()
        ]
        session.add_all(add_role)
    session.commit()


def set_student_class():
    school = EduTatar(ADMIN)
    students = school.get_students()
    session = SessionLocal()
    for class_, students in students.items():
        add_class = [
            User_class(
                user_id=get_user(edu_id=student_id).user_id,
                class_id=get_class_id(class_)
            ) for student_id in students.keys()
        ]
        session.add_all(add_class)
    session.commit()


def get_user_by_name(name: str):
    session = SessionLocal()
    name = name.split()
    if len(name) == 2:
        return session.query(Users).filter(Users.surname == name[0], Users.name == name[1]).first()
    if len(name) == 3:
        return session.query(Users).filter(Users.surname == name[0], Users.name == name[1], Users.middlename == name[2]).first()
    if len(name) > 3:
        return session.query(Users).filter(
            or_(and_(Users.surname == name[0], Users.name == name[1], Users.middlename == name[2]),
                and_(Users.surname == name[0], Users.name == name[1], Users.middlename == name[2]))).all()


def get_students_list(class_id):
    school = EduTatar(ADMIN)
    students = school.get_students()
    session = SessionLocal()
    for class_, students in students.items():
        pass
    session.commit()


def get_user(surname=None, name=None, middlename=None, edu_id=None, telegram_id=None, user_id=None):
    """По указанному набору данных возвращает пользователя.
    Для edu_tatar_id, user_id и telegram_id возвращается 1 пользователь"""

    session = SessionLocal()
    user = session.query(Users)
    if edu_id:
        return user.filter(Users.edu_tatar_id == edu_id).first()
    if surname and name and middlename:
        return user.filter(Users.surname == surname, Users.name == name, Users.middlename == middlename).all()
    if surname and name:
        return user.filter(Users.surname == surname, Users.name == name).all()
    if telegram_id:
        return user.filter(Users.telegram_id == telegram_id).first()
    if user_id:
        return user.filter(Users.user_id == user_id).first()


def get_class_id(class_: str):
    """Получаем ID класса, по его обозначению"""
    number = class_[:-1]
    literal = class_[-1]
    session = SessionLocal()
    return session.query(Classes).filter(Classes.number == number, Classes.literal == literal).first().class_id


set_student_class()
