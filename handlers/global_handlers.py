from database import crud
from aiogram import types
from loader import dp, bot
from database import crud, models
from aiogram import types
from config import admins, super_admins
import messages
from keyboards import keyboard


@dp.message_handler(commands=["start"])
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


@dp.callback_query_handler(text_startswith='main')
async def main_menu(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    status = cq.data.split('_')[1]
    if status == 'absent':
        await bot.send_message(cq.from_user.id, 'Выберите класс:', reply_markup=keyboard.classes())

    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(text_startswith='to_main')
async def main_menu(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    await bot.send_message(cq.from_user.id, 'Выберите, что Вы хотите сделать?', reply_markup=keyboard.start())

    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(text_startswith='class_')
async def main_menu(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    class_ = cq.data.split('_')[1]
    await bot.send_message(cq.from_user.id, 'Выберите отсутствующих:', reply_markup=keyboard.students(class_))

    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.callback_query_handler(text_startswith='student_')
async def main_menu(cq: types.CallbackQuery):
    await bot.answer_callback_query(cq.id)
    info = cq.data.split('_')
    await bot.send_message(cq.from_user.id, f'Выберите причину для ученика: <b>{info[3]}</b>', parse_mode='HTML',
                           reply_markup=keyboard.reasons(info[2], info[1]))

    await bot.delete_message(chat_id=cq.from_user.id, message_id=cq.message.message_id)


@dp.message_handler(commands=["get_codes"])
async def get_codes(message: types.Message):
    if message.from_user.id in super_admins:
        users = crud.get_user_list_with_role(not_role=8)
        text = '\n'.join(users)
        await message.answer(text)


