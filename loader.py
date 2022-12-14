from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
import config
from database import models, db, crud
import logging


bot = Bot(token=config.TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

models.Base.metadata.create_all(bind=db.engine)
db = db.SessionLocal()

# todo add loguru
logging.basicConfig(filename="log.log", level=logging.INFO)
log = logging.getLogger("bot")

