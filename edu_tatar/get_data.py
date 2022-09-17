from auth import EduTatar


edu_tatar_user = EduTatar('', '')
user = edu_tatar_user.connected()
print(user)
edu_tatar_user.logout()