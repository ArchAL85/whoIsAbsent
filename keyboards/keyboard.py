from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import crud


def start():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(
            text=f"Отметить отсутствующих",
            callback_data=f"main_absent"),
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
    buttons = [
        InlineKeyboardButton(
            text=f'{student[0]}',
            callback_data=f'student_{student[1]}_{class_}_{student[0]}'
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
    return kb


def reasons(class_, user):
    kb = InlineKeyboardMarkup()
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

