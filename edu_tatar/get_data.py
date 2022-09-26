from auth import EduTatar
from config import ADMIN


edu_tatar_user = EduTatar(ADMIN)
print(edu_tatar_user.get_students_classes())
print(edu_tatar_user.get_users())
print(edu_tatar_user.get_students())

edu_tatar_user.logout()