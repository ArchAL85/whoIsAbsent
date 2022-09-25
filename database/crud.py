import datetime
from sqlalchemy import or_, and_

from database.db import SessionLocal
from database.models import *

from edu_tatar.auth import EduTatar


def load_data_from_edu_tatar():
    """Выполняется только для загрузки или обновления данных"""
    school = EduTatar()
