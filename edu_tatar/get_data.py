from auth import EduTatar
from config import ADMIN


edu_tatar_user = EduTatar(ADMIN)
user = edu_tatar_user.connected()
print(edu_tatar_user.get_schedule())
edu_tatar_user.logout()