from aiogram.dispatcher.filters.state import State, StatesGroup


class BotStates(StatesGroup):
    """
    Класс для состояний
    """

    main_menu = State()
    wait_for_task = State()
    task = State()
    absent_menu = State()
    admin_menu = State()
    all_task = State()
    task_cabinet = State()
    postponed = State()
