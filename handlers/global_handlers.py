from aiogram.dispatcher.filters import ChatTypeFilter
from loader import dp, bot
from database import crud, models
from aiogram import types
from config import admins, super_admins, info_group, GLOBAL_SET
import messages
from keyboards import keyboard
from special.funcforbot import create_report


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=["start"])
async def start(message: types.Message):
    get_code = message.text.split()
    if crud.user_by_telegram_id(message.from_user.id):
        await message.answer('🤖Перезапускаюсь для Вас!', reply_markup=keyboard.start())
    else:
        if len(get_code) > 1:
            res = crud.user_code(get_code[1], message.from_user.id)
            if res:
                await message.answer(f'👋Приветствую Вас, {res}, в официальном боте ГАОУ "Лицей Иннополис".' +
                                     messages.hello)
                await message.answer('Выберите, что Вы хотите сделать?', reply_markup=keyboard.start())
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

    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), text_startswith='to_main')
async def main_menu(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    await bot.send_message(cq.from_user.id, 'Выберите, что Вы хотите сделать?', reply_markup=keyboard.start())

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
    await bot.send_message(info_group, f'{user.get_name()} отправил информацию по классу {class_[1]}{class_[2]}:\n'
                                       f'Учеников в классе: {class_count[0] - class_count[1]} из {class_count[0]}'
                           + absent_message)
    await bot.send_message(cq.from_user.id, 'Выберите класс:', reply_markup=keyboard.classes())
    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)
    GLOBAL_SET.add(class_)
    all_classes = crud.get_classes_list()
    crud.get_first_lesson_today()
    if len(GLOBAL_SET) == len(all_classes):
        file_name = create_report()
        for telegram_id in admins:
            try:
                with open(file_name, 'rb') as f:
                    await bot.send_document(telegram_id, f)
            except Exception as e:
                await bot.send_message()


@dp.message_handler(ChatTypeFilter(chat_type=types.ChatType.PRIVATE), commands=["get_codes"])
async def get_codes(message: types.Message):
    if message.from_user.id in super_admins:
        users = crud.get_user_list_with_role(not_role=8)
        text = '\n'.join(users)
        await message.answer(text)


