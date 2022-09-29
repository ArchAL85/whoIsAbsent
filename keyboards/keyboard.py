from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import crud


def start():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(
            text=f"Отметить отсутствующих",
            callback_data=f"main_absent"),
        InlineKeyboardButton(
            text=f"Оставить заявку на ремонт",
            callback_data=f"main_repair"),
    )
    return kb


def classes():
    kb = InlineKeyboardMarkup(row_width=2)
    class_ = crud.get_classes_list()
    buttons = [
        InlineKeyboardButton(
            text=f'{one[0]}{one[1]}',
            callback_data=f"class_{one[2]}"
        ) for one in class_
    ]

    kb.add(*buttons)
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"to_main")
    )
    return kb


def students(class_):
    kb = InlineKeyboardMarkup()
    all_students = crud.get_students_list(class_)
    absent_id = crud.get_absent_list(class_)
    buttons = [
        InlineKeyboardButton(
            text=f'{"🔴" if student[1] in absent_id else "⚪️"}{student[0]}',
            callback_data=f'student_{student[1]}_{class_}_{student[0].split()[0]} {student[0].split()[1][0]}.'
                          f'_{1 if student[1] in absent_id else 0}'
        ) for student in all_students
    ]
    kb.add(*buttons)
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"main_absent"
        ),
        InlineKeyboardButton(
            text=f'В начало',
            callback_data=f"to_main"
        )
    )
    kb.add(
        InlineKeyboardButton(
            text=f'Готово',
            callback_data=f"save_{class_}"
        )
    )
    return kb


def reasons(class_, user):
    kb = InlineKeyboardMarkup(row_width=2)
    all_reasons = crud.get_reasons()
    buttons = [
        InlineKeyboardButton(
            text=f'{reason[0]}',
            callback_data=f'reason_{reason[1]}_{user}_{class_}'
        ) for reason in all_reasons
    ]
    kb.add(*buttons)
    kb.add(
        InlineKeyboardButton(
            text=f'Отменить',
            callback_data=f"class_{class_}"
        )
    )
    return kb


def first_lesson(class_):
    kb = InlineKeyboardMarkup(row_width=2)
    button = crud.get_classes_by_id(class_)
    kb.add(
        InlineKeyboardButton(
            text=f'Отметить отсутствующих в {button[1]}{button[2]}',
            callback_data=f"class_{button[0]}"
        ))
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"to_main")
    )
    return kb
