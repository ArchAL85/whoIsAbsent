import asyncio
import aioschedule
from aiogram.utils import executor

from loader import bot
from handlers import dp


async def choose_your_dinner():
    await bot.send_message(chat_id=148161847, text="Хей🖖 не забудь выбрать свой ужин сегодня")


async def scheduler():
    aioschedule.every().day.at("11:13").do(choose_your_dinner)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dp):
    asyncio.create_task(scheduler())

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)