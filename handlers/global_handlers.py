import datetime
import logging

from aiogram.dispatcher.filters import ChatTypeFilter
from aiogram.dispatcher import FSMContext
from loader import dp, bot
from database import crud, models
from aiogram import types
import pymorphy2


from config import admins, super_admins, info_group, GLOBAL_SET, task_admins
import messages
from keyboards import keyboard
from special.funcforbot import create_report
from states.bot_state import BotStates

morph = pymorphy2.MorphAnalyzer()


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=["start"])
async def start(message: types.Message, state: FSMContext):
    get_code = message.text.split()
    if crud.user_by_telegram_id(message.from_user.id):
        await message.answer('🤖Перезапускаюсь для Вас!', reply_markup=keyboard.start(message.from_user.id))
        await state.set_state(BotStates.main_menu.state)
    else:
        if len(get_code) > 1:
            res = crud.user_code(get_code[1], message.from_user.id)
            if res:
                await message.answer(f'👋Приветствую Вас, {res}, в официальном боте ГАОУ "Лицей Иннополис".' +
                                     messages.hello)
                await message.answer('Выберите, что Вы хотите сделать?',
                                     reply_markup=keyboard.start(message.from_user.id))
                await state.set_state(BotStates.main_menu.state)
            else:
                await message.answer('😐Нам не удалось найти Вас в нашей базе.')
        else:
            await message.answer('🤨Вам нужно зарегистрироваться по специальной ссылке!')


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='main', state='*')
async def get_class(cq: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(cq.id)
    status = cq.data.split('_')[1]
    if status == 'absent':
        await bot.send_message(cq.from_user.id, 'Выберите класс:', reply_markup=keyboard.classes())
        await state.set_state(BotStates.absent_menu.state)
    elif status == 'admin':
        await bot.send_message(cq.from_user.id, 'Добро пожаловать в панель администратора.\n'
                                                'Выберите действие:', reply_markup=keyboard.admin_panel())
        await state.set_state(BotStates.admin_menu.state)
    elif status == 'repair':
        await bot.send_message(cq.from_user.id, 'Выберите, кому хотите оставить заявку?',
                               reply_markup=keyboard.kb_master())
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='to_main', state='*')
async def main_menu(cq: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(cq.id)
    await bot.send_message(cq.from_user.id, 'Выберите, что Вы хотите сделать?',
                           reply_markup=keyboard.start(cq.from_user.id))
    await state.set_state(BotStates.main_menu.state)
    await state.reset_data()
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='class_', state='*')
async def set_absents(cq: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(cq.id)
    class_ = cq.data.split('_')[1]
    await bot.send_message(cq.from_user.id, 'Выберите отсутствующих:', reply_markup=keyboard.students(class_))
    await state.set_state(BotStates.absent_menu.state)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='student_', state='*')
async def set_reason(cq: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(cq.id)
    info = cq.data.split('_')
    if info[4] == "0":
        await bot.send_message(cq.from_user.id, f'Выберите причину для ученика: <b>{info[3]}</b>', parse_mode='HTML',
                               reply_markup=keyboard.reasons(info[2], info[1]))
    else:
        crud.delete_absent(info[1])
        await bot.send_message(cq.from_user.id, 'Выберите отсутствующих:', reply_markup=keyboard.students(info[2]))
    await state.set_state(BotStates.absent_menu.state)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='reason_', state='*')
async def save_reason(cq: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(cq.id)
    info = cq.data.split('_')
    crud.save_absent(info[1], info[2])
    await bot.send_message(cq.from_user.id, 'Выберите отсутствующих:', reply_markup=keyboard.students(info[3]))
    await state.set_state(BotStates.absent_menu.state)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='save_', state='*')
async def save_absent(cq: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(cq.id)
    info = cq.data.split('_')
    class_ = crud.get_classes_by_id(info[1])
    user = crud.get_user(telegram_id=cq.from_user.id)
    absent_list = crud.get_absent_users_by_class(info[1])
    class_count = crud.get_class_count(info[1])
    absent_message = ''
    if absent_list:
        absent_message = '\nОтсутствующие: '
        for one in absent_list:
            absent_message += f'{one[0]} ({one[1]}), '
        absent_message = absent_message[:-2]
    sex = 'отправил'
    name = user.get_name()
    parsed_word = morph.parse(name.split()[1])[0]
    if parsed_word.tag.gender == 'femn':
        sex += 'а'
    await bot.send_message(info_group, f'{name} {sex} информацию по классу <b>{class_[0]}{class_[1]}</b>:\n'
                                       f'Учеников в классе: <b>{class_count[0] - class_count[1]} из {class_count[0]}</b>'
                                       f'{absent_message}', parse_mode='HTML')
    await bot.send_message(cq.from_user.id, 'Выберите класс:', reply_markup=keyboard.classes())
    GLOBAL_SET.add(class_)
    all_classes = crud.get_classes_list()
    if len(GLOBAL_SET) == len(all_classes):
        file_name = create_report()
        for telegram_id in admins:
            try:
                with open(file_name, 'rb') as f:
                    await bot.send_document(telegram_id, f)
            except Exception as e:
                await bot.send_message(148161847, f'{e}')
    await state.set_state(BotStates.absent_menu.state)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='lesson_', state='*')
async def get_lessons(cq: types.CallbackQuery):
    if cq.from_user.id in admins:
        index = int(cq.data.split('_')[1])
        all_lessons = crud.get_lesson_today(index)
        lessons = [crud.get_classes_by_id(lesson[2]) for lesson in all_lessons]
        lessons = [[lesson[0], lesson[1]] for lesson in lessons]
        teachers = [crud.get_user(edu_id=lesson[0]).get_name() for lesson in all_lessons]
        data = [[lessons[i][0], lessons[i][1], teachers[i]] for i in range(len(teachers))]
        data.sort()
        users = [f'{data[i][0]}{data[i][1]} {data[i][2]}' for i in range(len(data))]
        text = '\n'.join(users)
        try:
            await bot.send_message(cq.from_user.id, text, reply_markup=keyboard.lessons_panel())
        except Exception as e:
            await bot.send_message(cq.from_user.id, 'На это время уроков нет!', reply_markup=keyboard.lessons_panel())
        await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='admin', state='*')
async def admin_panel(cq: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(cq.id)
    status = cq.data.split('_')[1]
    if status == 'lessons':
        await bot.send_message(cq.from_user.id, 'Выберите номер урока:', reply_markup=keyboard.lessons_panel())
    if status == 'reports':
        await bot.send_message(cq.from_user.id, 'Раздел в разработке.\n'
                                                'Выберите действие:', reply_markup=keyboard.admin_panel())
    if status == 'tasks':
        await bot.send_message(cq.from_user.id, 'Выберите действие:', reply_markup=keyboard.admin_task_panel())
    await state.set_state(BotStates.admin_menu.state)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=["get_codes"], state='*')
async def get_codes(message: types.Message):
    if message.from_user.id in super_admins:
        users = crud.get_user_list_with_role(not_role=8)
        text = '\n'.join(users)
        await message.answer(text)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='master_', state='*')
async def get_block(cq: types.CallbackQuery, state: FSMContext):
    _, master, user = cq.data.split('_')
    await state.update_data(master=int(master), employee=int(user))
    await bot.send_message(cq.from_user.id, 'Выберите блок:', reply_markup=keyboard.blocks())
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='cab_', state='*')
async def get_cab(cq: types.CallbackQuery, state: FSMContext):
    block = cq.data.split('_')[1]
    await state.update_data(block=block)
    mes = await bot.send_message(cq.from_user.id, 'Введите номер кабинета или пояснение')
    await state.set_state(BotStates.task_cabinet.state)
    await state.update_data(message_id=mes.message_id)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), state=BotStates.task_cabinet)
async def master_panel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.update_data(cabinet=message.text)
    await state.set_state(BotStates.wait_for_task.state)
    mes = await bot.send_message(message.from_user.id, 'Опишите суть проблемы и потом отправьте её')
    await bot.delete_message(chat_id=message.from_user.id, message_id=data['message_id'])
    await state.update_data(message_id=mes.message_id)


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), state=BotStates.wait_for_task)
async def try_to_save_task(message: types.Message, state: FSMContext):
    correct_block = {'a': 'А', 'b': 'Б', 'c': 'В'}
    data = await state.get_data()
    last_id = crud.save_task(message.text, message.from_user.id, data['master'],
                             correct_block[data["block"]], data["cabinet"], data["employee"])
    if bool(last_id):
        await message.answer('Ваша заявка принята')
        role = crud.get_role(data['master'])
        for x_id in task_admins:
            user = crud.get_user(telegram_id=message.from_user.id)
            await bot.send_message(x_id, f'Заявка от: <b>{user.get_name()}</b>\n'
                                         f'Дата заявки: <b>{datetime.datetime.now().strftime("%d.%m.%y %H:%M")}</b>\n'
                                         f'Кому: <b>{role.title}</b>\n'
                                         f'Блок: <b>{correct_block[data["block"]]}</b>\n'
                                         f'Кабинет: <b>{data["cabinet"]}</b>\n'
                                         f'Описание: {message.text}', reply_markup=keyboard.task_keyboard(last_id))
        await bot.delete_message(chat_id=message.from_user.id, message_id=data['message_id'])
        await bot.send_message(message.from_user.id, 'Хотите оставить ещё одну заявку?',
                               reply_markup=keyboard.kb_master())
        await state.reset_data()
        await state.set_state(BotStates.task.state)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='task_list', state='*')
async def all_task_panel(cq: types.CallbackQuery, state: FSMContext):
    tasks = crud.get_tasks_by_telegram_id(cq.from_user.id)
    if tasks:
        await state.set_state(BotStates.all_task.state)
        messages_id = []
        for task in tasks:
            x = await bot.send_message(cq.from_user.id, task.description, reply_markup=keyboard.task_list(task.task_id))
            messages_id.append(x.message_id)
        await state.update_data(messages_id=messages_id)
        await bot.send_message(cq.from_user.id, 'Вы можете удалить ранее созданную задачу',
                               reply_markup=keyboard.task_go_back())
    else:
        await bot.send_message(cq.from_user.id, 'У вас нет задач!', reply_markup=keyboard.go_back())
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='delete_task',
                           state=BotStates.all_task)
async def delete_task(cq: types.CallbackQuery, state: FSMContext):
    task = int(cq.data.split('_')[2])
    crud.delete_task(task)
    data = await state.get_data()
    data['messages_id'].remove(cq.message.message_id)
    await state.update_data(messages_id=data['messages_id'])
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='task_to_main',
                           state=BotStates.all_task)
async def delete_task(cq: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    for x in data['messages_id']:
        await bot.delete_message(chat_id=cq.from_user.id, message_id=x)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)
    await state.reset_data()
    await state.set_state(BotStates.task.state)
    await bot.send_message(cq.from_user.id, 'Хотите оставить ещё одну заявку?',
                           reply_markup=keyboard.kb_master())


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='tadmin_', state='*')
async def admin_task(cq: types.CallbackQuery, state: FSMContext):
    task = cq.data.split('_')[1]
    await state.update_data(message_id=[])
    if task == 'current':
        tasks = crud.get_all_task()
        for one in tasks:
            data = await state.get_data()
            user = crud.get_user(user_id=one.client_id)
            role = crud.get_role(one.role)
            text = f'Заявка от: <b>{user.get_name()}</b>\n' \
                   f'Дата заявки: <b>{one.start_date.strftime("%d.%m.%y %H:%M")}</b>\n' \
                   f'Кому: <b>{role.title}</b>\n' \
                   f'Блок: <b>{one.block}</b>\n' \
                   f'Кабинет: <b>{one.cabinet}</b>\n' \
                   f'Описание: {one.description}'
            x = await bot.send_message(cq.from_user.id, text,
                                       reply_markup=keyboard.task_keyboard(one.task_id))
            data['message_id'].append(x.message_id)
            await state.update_data(message_id=data['message_id'])
        await bot.send_message(cq.from_user.id, 'Выберите действие выше или нажмите на отмену',
                               reply_markup=keyboard.cancle())
    elif task == 'report':
        pass
    elif task == 'month':
        pass
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='cancel_', state='*')
async def cancel_task(cq: types.CallbackQuery, state: FSMContext):
    task = cq.data.split('_')[1]
    if task == 'task':
        data = await state.get_data()
        for message_id in data['message_id']:
            try:
                await bot.delete_message(chat_id=cq.from_user.id, message_id=message_id)
            except Exception as e:
                logging.info(e)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)
    await bot.send_message(cq.from_user.id, 'Выберите действие:', reply_markup=keyboard.admin_task_panel())


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='employee_', state='*')
async def set_employee_for_task(cq: types.CallbackQuery):
    _, user_id, task_id = cq.data.split('_')
    crud.update_task(int(task_id), int(user_id))
    user = crud.get_user(user_id=user_id)
    await bot.send_message(user.telegram_id, cq.message.text, reply_markup=keyboard.employee_complete(int(task_id)))
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='complete', state='*')
async def complete_for_task(cq: types.CallbackQuery):
    _, user_id, task_id = cq.data.split('_')
    crud.update_task(int(task_id), int(user_id), True)
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)
