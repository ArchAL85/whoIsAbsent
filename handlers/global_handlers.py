from aiogram.dispatcher.filters import ChatTypeFilter
from loader import dp, bot
from database import crud, models
from aiogram import types
import pymorphy2


from config import admins, super_admins, info_group, GLOBAL_SET
import messages
from keyboards import keyboard
from special.funcforbot import create_report


morph = pymorphy2.MorphAnalyzer()


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=["start"])
async def start(message: types.Message):
    get_code = message.text.split()
    if crud.user_by_telegram_id(message.from_user.id):
        await message.answer('🤖Перезапускаюсь для Вас!', reply_markup=keyboard.start(message.from_user.id))
    else:
        if len(get_code) > 1:
            res = crud.user_code(get_code[1], message.from_user.id)
            if res:
                await message.answer(f'👋Приветствую Вас, {res}, в официальном боте ГАОУ "Лицей Иннополис".' +
                                     messages.hello)
                await message.answer('Выберите, что Вы хотите сделать?',
                                     reply_markup=keyboard.start(message.from_user.id))
            else:
                await message.answer('😐Нам не удалось найти Вас в нашей базе.')
        else:
            await message.answer('🤨Вам нужно зарегистрироваться по специальной ссылке!')


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='main')
async def get_class(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    status = cq.data.split('_')[1]
    if status == 'absent':
        await bot.send_message(cq.from_user.id, 'Выберите класс:', reply_markup=keyboard.classes())
    if status == 'admin':
        await bot.send_message(cq.from_user.id, 'Добро пожаловать в панель администратора.\n'
                                                'Выберите действие:', reply_markup=keyboard.admin_panel())
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='to_main')
async def main_menu(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    await bot.send_message(cq.from_user.id, 'Выберите, что Вы хотите сделать?',
                           reply_markup=keyboard.start(cq.from_user.id))

    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='class_')
async def set_absents(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    class_ = cq.data.split('_')[1]
    await bot.send_message(cq.from_user.id, 'Выберите отсутствующих:', reply_markup=keyboard.students(class_))
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='student_')
async def set_reason(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    info = cq.data.split('_')
    if info[4] == "0":
        await bot.send_message(cq.from_user.id, f'Выберите причину для ученика: <b>{info[3]}</b>', parse_mode='HTML',
                               reply_markup=keyboard.reasons(info[2], info[1]))
    else:
        crud.delete_absent(info[1])
        await bot.send_message(cq.from_user.id, 'Выберите отсутствующих:', reply_markup=keyboard.students(info[2]))
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='reason_')
async def save_reason(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    info = cq.data.split('_')
    crud.save_absent(info[1], info[2])
    await bot.send_message(cq.from_user.id, 'Выберите отсутствующих:', reply_markup=keyboard.students(info[3]))

    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='save_')
async def save_absent(cq: types.CallbackQuery):
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
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='lesson_')
async def get_codes(cq: types.CallbackQuery):
    if cq.from_user.id in admins:
        index = int(cq.data.split('_')[1])
        all_lessons = crud.get_lesson_today(index)
        lessons = [crud.get_classes_by_id(lesson[2]) for lesson in all_lessons]
        lessons = [[lesson[0], lesson[1]] for lesson in lessons]
        teachers = [crud.get_user(edu_id=lesson[0]).get_name() for lesson in all_lessons]
        data = [[lessons[i][0], lessons[i][1], teachers[i]] for i in range(len(teachers))]
        data.sort()
        users = [f'{data[i][1]}{data[i][2]} {data[i][2]}' for i in range(len(data))]
        text = '\n'.join(users)
        await bot.send_message(cq.from_user.id, text, reply_markup=keyboard.lessons_panel())
        await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='admin')
async def admin_panel(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    status = cq.data.split('_')[1]
    if status == 'lessons':
        await bot.send_message(cq.from_user.id, 'Выберите номер урока:', reply_markup=keyboard.lessons_panel())
    if status == 'reports':
        await bot.send_message(cq.from_user.id, 'Раздел в разработке.\n'
                                                'Выберите действие:', reply_markup=keyboard.admin_panel())
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=["get_codes"])
async def get_codes(message: types.Message):
    if message.from_user.id in super_admins:
        users = crud.get_user_list_with_role(not_role=8)
        text = '\n'.join(users)
        await message.answer(text)


