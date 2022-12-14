from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import crud
from config import admins, task_admins


def start(telegram_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(
            text=f"Отметить отсутствующих",
            callback_data=f"main_absent"),
        InlineKeyboardButton(
            text=f"Оставить заявку на ремонт",
            callback_data=f"main_repair"),
    )
    if telegram_id in admins or telegram_id in task_admins:
        kb.add(
            InlineKeyboardButton(
                text=f"Администрирование",
                callback_data=f"main_admin")
        )
    master_ids = [user.telegram_id for user in crud.get_all_masters()]
    if telegram_id in master_ids:
        kb.add(
            InlineKeyboardButton(
                text=f"Мои задачи",
                callback_data=f"main_tasks")
        )
    return kb


def classes() -> InlineKeyboardMarkup:
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


def students(class_) -> InlineKeyboardMarkup:
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


def reasons(class_, user) -> InlineKeyboardMarkup:
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


def first_lesson(class_) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    button = crud.get_classes_by_id(class_)
    kb.add(
        InlineKeyboardButton(
            text=f'Отметить отсутствующих в {button[0]}{button[1]}',
            callback_data=f"class_{button[2]}"
        ))
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"to_main")
    )
    return kb


def admin_panel() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(
            text=f'Уроки',
            callback_data=f"admin_lessons"
        ),
        InlineKeyboardButton(
            text=f'Отчёты',
            callback_data=f"admin_reports"
        ),
        InlineKeyboardButton(
            text=f'Заявки',
            callback_data=f"admin_tasks"
        )
    )
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"to_main")
    )
    return kb


def lessons_panel() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=4)
    buttons = [
        InlineKeyboardButton(
            text=f'{i + 1}',
            callback_data=f"lesson_{i}"
        ) for i in range(7)
    ]
    kb.add(*buttons)
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"main_admin"),
        InlineKeyboardButton(
            text=f'В начало',
            callback_data=f"to_main")
    )
    return kb


def kb_master() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    masters = crud.get_master()
    buttons = [
        InlineKeyboardButton(
            text=f'{master.title}',
            callback_data=f"master_{master.role_id}_{(crud.get_master_by_role(master.role_id))[0].user_id}"
        ) for master in masters
        ]
    kb.add(*buttons)
    kb.add(
        InlineKeyboardButton(
            text=f'Отправленные задачи',
            callback_data=f"task_list")
    )
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"to_main")
    )
    return kb


def task_list(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(
            text=f'Отменить заявку',
            callback_data=f"delete_task_{task_id}")
    )
    return kb


def task_go_back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"task_to_main")
    )
    return kb


def go_back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"to_main")
    )
    return kb


def blocks() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton(
            text=f'А',
            callback_data=f"cab_a"),
        InlineKeyboardButton(
            text=f'Б',
            callback_data=f"cab_b"),
        InlineKeyboardButton(
            text=f'В',
            callback_data=f"cab_c"),
    )
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"to_main")
    )
    return kb


def admin_task_panel() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            text=f'Список текущих задач',
            callback_data=f"tadmin_current"
        )
    )
    kb.add(
        InlineKeyboardButton(
            text=f'Задачи в работе',
            callback_data=f"tadmin_work"
        )
    )
    kb.add(
        InlineKeyboardButton(
            text=f'Отложенные задачи',
            callback_data=f"tadmin_postponed"
        )
    )
    kb.add(
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"main_admin"),
        InlineKeyboardButton(
            text=f'В начало',
            callback_data=f"to_main")
    )
    return kb


def task_keyboard(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    masters = crud.get_all_masters()
    buttons = []
    for master in masters:
        buttons.append(InlineKeyboardButton(
            text=f'{master.get_name()}',
            callback_data=f"employee_{master.user_id}_{task_id}"
        )
        )
    kb.add(*buttons)
    master = crud.get_task(task_id)
    kb.add(
        InlineKeyboardButton(
            text='Выполнено',
            callback_data=f'complete_{master.employee}_{task_id}'
        )
    )
    kb.add(
        InlineKeyboardButton(
            text='Закрыть',
            callback_data=f'close'
        )
    )
    return kb


def employee_complete(task_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    master = crud.get_task(task_id)
    kb.add(
        InlineKeyboardButton(
            text='Выполнено',
            callback_data=f'complete_{master.employee}_{task_id}'
        ),
        InlineKeyboardButton(
            text='Отложить',
            callback_data=f'postponed_{master.employee}_{task_id}'
        )
    )
    return kb


def cancle() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(
            text='Отменить',
            callback_data=f'cancel_task'
        )
    )
    return kb


def report_panel() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(
            text=f'Отчёт по заявкам',
            callback_data=f"treport"),
        InlineKeyboardButton(
            text=f'⬅ Назад',
            callback_data=f"main_admin"),
        InlineKeyboardButton(
            text=f'В начало',
            callback_data=f"to_main")
    )
    return kb
