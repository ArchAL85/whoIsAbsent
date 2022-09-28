from docxtpl import DocxTemplate
import datetime as dt
import random
from database import crud


def get_int_time(date: dt.datetime = dt.datetime(2022, 9, 26, 0, 0, 0)):
    x = (date - dt.datetime(1970, 1, 1, 0, 0, 0)).total_seconds()
    return int(x)


def generate_code() -> str:
    code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    code = ''
    for i in range(random.randint(10, 15)):
        code += random.choice(code_chars)
    return code


def create_report():
    doc = DocxTemplate("special/Absent.docx")
    replace = {'а': 'a', 'А': 'a', 'б': 'b', 'Б': 'b', 'в': 'c', 'В': 'c'}
    classes = crud.get_classes_list()
    context = {}
    all_students = 0
    all_in_lyceum = 0
    for class_ in classes:
        students_count = crud.get_class_count(class_[2])
        key = f'{replace[class_[1]]}_{class_[0]}'
        key_all = key + '_all'
        key_absent = key + '_absent'
        all_students += students_count[0]
        all_in_lyceum += students_count[1]
        context[key] = students_count[0] - students_count[1]
        context[key_all] = students_count[0]
        users_absent = crud.get_absent_users_by_class(class_[2])
        context[key_absent] = ', '.join([f'{one[0]} ({one[1]})' for one in users_absent])
    context['all_in_lyceum'] = all_students - all_in_lyceum
    context['all_students'] = all_students
    context['date'] = dt.datetime.now().strftime("%d.%m.%Y")
    doc.render(context)
    file_name = f'{dt.datetime.now().strftime("%d.%m.%Y")}.docx'
    doc.save(file_name)
    return file_name
