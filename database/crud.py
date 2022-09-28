import datetime
from sqlalchemy import or_, and_, Date, cast, func
from datetime import date

from database.db import SessionLocal
from database.models import *

from edu_tatar.auth import EduTatar
from config import ADMIN
from special.funcforbot import generate_code


def add_role_reasons():
    """Добавляем все роли и причины отсутствия"""
    session = SessionLocal()
    role = [Role(role_id=1, title='Администратор', description='Административный работник'),
            Role(role_id=2, title='Секретарь', description='Секретарь учреждения'),
            Role(role_id=3, title='Сисадмин', description='Системный администратор'),
            Role(role_id=4, title='Учитель', description='Учитель'),
            Role(role_id=5, title='Воспитатель', description='Воспитатель'),
            Role(role_id=6, title='Классный руководитель', description='Классный руководитель'),
            Role(role_id=7, title='Сотрудник', description='Сотрудники без конкретной роли'),
            Role(role_id=8, title='Ученик', description='Ученики')]
    all_r = [[1, "ОРЗ, ОРВИ, ГРИПП", "ОРЗ, ОРВИ, грипп и аналогичные болезни"],
             [2, 'COVID-19', 'COVID-19 - если подтверждён'],
             [3, 'Болеет в Лицее', 'До приезда родителей или в изоляторе'],
             [4, 'По заявлению', 'По заявлению или уважительной причине'],
             [5, 'Олимпиада', "Участи в олимпиадах, конкурсах и т.д."],
             [6, 'Олимпиада в Лицее', "Участи в олимпиадах, конкурсах и т.д. но находится в Лицее"],
             [7, 'УТС', 'Уехал на сборы'],
             [8, 'УТС в Лицее', 'В Лицее на сборах или подготовке'],
             [9, 'Другое', 'Причина не известна']
             ]
    reason = [
        Reasons(reason_id=reason_id, title=title, description=description) for reason_id, title, description in all_r
    ]
    session.add_all(role)
    session.add_all(reason)
    session.commit()


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
        return session.query(Users).filter(Users.surname == name[0], Users.name == name[1],
                                           Users.middlename == name[2]).first()
    if len(name) > 3:
        return session.query(Users).filter(
            or_(and_(Users.surname == name[0], Users.name == name[1], Users.middlename == name[2]),
                and_(Users.surname == name[0], Users.name == name[1], Users.middlename == name[2]))).all()


def get_students_list(class_id):
    """Возвращает список учеников класса"""
    session = SessionLocal()
    students = session.query(User_class).filter(User_class.class_id == class_id).all()
    users = [[student.users.get_name(), student.users.user_id] for student in students]
    users.sort()
    return users


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


def get_classes_list():
    """Получить список классов [класс, буква, id]"""
    session = SessionLocal()
    classes = [[one.number, one.literal, one.class_id] for one in session.query(Classes).all()]
    classes.sort()
    return classes


def create_code_for_auth():
    """Создать коды для всех пользователей. Коды будут обновлены всем"""
    session = SessionLocal()
    users = session.query(Users)
    for user in users:
        users.filter(Users.edu_tatar_id == user.edu_tatar_id).update({'code': generate_code()})
    session.commit()


def get_user_list_with_role(role=None, not_role=None):
    """Получить список пользователей с конкретными ролями"""
    session = SessionLocal()
    if not_role:
        users = session.query(User_role).join(Users).filter(User_role.role_id != not_role)
    else:
        users = session.query(User_role).join(Users).filter(User_role.role_id == role)
    return [f'{user.users.get_name()} https://t.me/innolyceum_bot?start={user.users.code}' for user in users]


def user_code(code, telegram_id):
    session = SessionLocal()
    user = session.query(Users).filter(Users.code == code)
    curr_user = user.first()
    if curr_user:
        user.update({'telegram_id': telegram_id, 'code': ''})
        session.commit()
        return curr_user.get_name()
    else:
        return False


def user_by_telegram_id(telegram_id):
    session = SessionLocal()
    user = session.query(Users).filter(Users.telegram_id == telegram_id).first()
    if user:
        return user.get_name()
    else:
        return False


def get_reasons():
    """"Возвращает список причин [причина, id]"""
    session = SessionLocal()
    reasons = session.query(Reasons).all()
    return [[reason.title, reason.reason_id] for reason in reasons]


def get_absent_list(class_):
    """Возвращает список id - учеников класса, кто отсутствует сегодня"""
    session = SessionLocal()
    absent = session.query(Absents).join(Reasons).join(Users).join(User_class).join(Classes).filter(
        func.date(Absents.date) == datetime.now().date(), Classes.class_id == class_).all()
    absent = [one.user_id for one in absent]
    return absent


def save_absent(reason_id, user_id):
    """Сохранение отсутствующего"""
    session = SessionLocal()
    absent = Absents(reason_id=reason_id, user_id=user_id)
    session.add(absent)
    session.commit()
    session.refresh(absent)


def delete_absent(user_id):
    """Удаление отсутствующего"""
    session = SessionLocal()
    session.query(Absents).filter(func.date(Absents.date) == datetime.now().date(), Absents.user_id == user_id) \
        .delete(synchronize_session=False)
    session.commit()


def get_classes_by_id(class_id):
    """Получить классов (id, класс, буква) по ID"""
    session = SessionLocal()
    classes = session.query(Classes).filter(Classes.class_id == class_id).first()
    return classes.class_id, classes.number, classes.literal


def get_absent_users_by_class(class_id):
    """Возвращает список отсутствующих в классе вида [ФИ, причина, В лицее?]"""
    session = SessionLocal()
    absent = session.query(Absents).join(Reasons).join(Users).join(User_class).filter(
        func.date(Absents.date) == datetime.now().date(), User_class.class_id == class_id).all()
    absent = [[one.users.get_name(), one.reasons.title, one.reasons.in_or_out] for one in absent]
    return absent


def get_class_count(class_id):
    """Возвращает количество учеников в классе, количество отсутствующих, кто в лицее, кто вне лицея"""
    session = SessionLocal()
    class_count = session.query(User_class).filter(User_class.class_id == class_id).count()
    absent_count = session.query(Absents).join(Users).join(User_class).filter(
        func.date(Absents.date) == datetime.now().date(), User_class.class_id == class_id).count()
    absent_in = session.query(Absents).join(Reasons).join(Users).join(User_class).filter(
        func.date(Absents.date) == datetime.now().date(), User_class.class_id == class_id,
        Reasons.in_or_out == True).count()
    absent_out = session.query(Absents).join(Reasons).join(Users).join(User_class).filter(
        func.date(Absents.date) == datetime.now().date(), User_class.class_id == class_id,
        Reasons.in_or_out == False).count()
    return class_count, absent_count, absent_in, absent_out


def get_telegram_id(edu_id):
    """Возвращает телеграм ID по edu_id"""
    session = SessionLocal()
    user = session.query(Users).filter(Users.edu_tatar_id == edu_id).first()
    return user.telegram_id


def get_first_lesson_today():
    """Возвращает список учителей, у кого первый урок и в каком классе [edu_id, telegram_id, class_id]"""
    session = SessionLocal()
    day = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
    current_day = datetime.now()
    lessons = session.query(Schedule).filter(Schedule.index_number == 1,
                                             Schedule.day_of_week == day[datetime.weekday(current_day)]).all()
    return [[lesson.teacher_id, get_telegram_id(lesson.teacher_id), lesson.class_id] for lesson in lessons]

# add_role_reasons()
# load_data_from_edu_tatar()
# load_schedule()
# set_student_role()
# set_student_class()
# create_code_for_auth()
