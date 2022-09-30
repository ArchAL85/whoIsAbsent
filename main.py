import asyncio
import aioschedule
from aiogram.utils import executor

from loader import bot
from handlers import dp

from config import GLOBAL_SET
from keyboards.keyboard import first_lesson
from database.crud import get_first_lesson_today


async def remember():
    GLOBAL_SET.clear()
    all_lessons = get_first_lesson_today()
    for lesson in all_lessons:
        if lesson[1]:
            await bot.send_message(chat_id=lesson[1],
                                   text="Доброе утро!🖖 У Вас сегодня первый урок. Не забудьте отметить отсутствующих",
                                   reply_markup=first_lesson(lesson[2]))


async def scheduler():
    aioschedule.every().day.at("08:00").do(remember)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp):
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)