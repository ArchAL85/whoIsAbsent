import requests
from bs4 import BeautifulSoup


class EduTatar:
    _LOGIN_URL = 'https://edu.tatar.ru/logon'  # Страница Логина
    _LOGOUT_URL = 'https://edu.tatar.ru/logoff'
    _MAIN_URL = 'https://edu.tatar.ru/user/anketa'
    _CLASSES_PAGE = 'https://edu.tatar.ru/school/academic_year/classes'  # <tbody id="dataBody">

    def __init__(self, login, password):
        self.s = requests.Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'Upgrade-Insecure-Requests': '1'})
        auth = {
            'main_login2': login,
            'main_password2': password
        }

        self.s.post(self._LOGIN_URL, data=auth, headers=dict(referer=self._LOGIN_URL))

    def connected(self):
        get_teachers_from_page = BeautifulSoup(self.get_html(self._MAIN_URL), 'lxml')
        find_error1 = get_teachers_from_page.find_all("div", {"class": "alert-danger"})
        find_error2 = get_teachers_from_page.find_all("div", {"class": "err_msg"})
        if find_error1 or find_error2:
            return 'Error', 'Неверный логин или пароль!'
        else:
            return 'Ok', '1'

    def get_html(self, url):
        response = self.s.get(url)
        return response.text

    def get_state(self):
        # print('Проверка статуса человека')
        get_teachers_from_page = BeautifulSoup(self.get_html(self._MAIN_URL), 'lxml')
        tr = get_teachers_from_page.find('table').find_all('tr')
        for s in tr:
            td = s.find_all('td', limit=4, string=True)
            td = [e.string.strip() for e in td]
            if td[0] == 'Должность:':
                return td[1]

    def get_name(self):
        # print('Загрузка данных о человеке')
        get_name_from_page = BeautifulSoup(self.get_html(self._MAIN_URL), 'lxml')
        tr = get_name_from_page.find('table').find_all('tr')
        for s in tr:
            td = s.find_all('td', limit=4, string=True)
            td = [e.string.strip() for e in td]
            if td[0] == 'Имя:':
                return tuple(td[1].split())

    def get_school(self):
        # print('Данные о школе')
        get_school_from_page = BeautifulSoup(self.get_html(self._MAIN_URL), 'lxml')
        tr = get_school_from_page.find('table').find_all('tr')
        for s in tr:
            td = s.find_all('td', limit=4, string=True)
            td = [e.string.strip() for e in td]
            if td[0] == 'Школа:':
                return td[1]

    @staticmethod
    def get_user_list(get_users_from_page):
        users = []
        for s in get_users_from_page.find_all('tr'):
            td = s.find_all('td', string=True)
            td = [e.string.strip() for e in td]
            if td[4] == 'активен':
                name = td[1].split()
                # Редактируем отчество, если это необходимо. Иногда оно может состоять из двух полей
                if len(name) > 3:
                    name[2] = f'{name[2]} {name.pop(3)}'
                users.append(name + [td[2], td[3]])
        return users

    # def get_users(self):
    #     # Получить список всех активных пользователей из edu.tatar.ru для образовательного учреждения.
    #     # Нужен вход от имени директора ОУ. Список загружается только при первом входе директора и назначении ролей.
    #     url = 'https://edu.tatar.ru/user/edu_user/?profile_id='
    #     urls = user_list
    #     users = []
    #     for url_id in urls:
    #         get_users_from_page = BeautifulSoup(self.get_html(url + str(url_id)), 'lxml')
    #         users.extend(self.get_user_list(get_users_from_page))
    #         get_pages = get_users_from_page.find('p', {"class": "pages"})
    #         if get_pages:
    #             pages = [t.string.strip() for t in get_pages.find_all('a', href=True)]
    #             for page in pages:
    #                 get_users_from_page = BeautifulSoup(self.get_html(url + str(url_id)) + '&page=' + str(page), 'lxml')
    #                 users.extend(self.get_user_list(get_users_from_page))
    #     if special_users_url:
    #         get_users_from_page = BeautifulSoup(self.get_html(special_users_url), 'lxml')
    #         users.extend(self.get_user_list(get_users_from_page))
    #     return users

    def get_cabinets(self):
        url = 'https://edu.tatar.ru/school/classroom'
        cabinets = []
        get_cabinets = BeautifulSoup(self.get_html(url), 'lxml')
        for s in get_cabinets.find_all('tr'):
            td = s.find_all('td', string=True)
            td = [e.string.strip() for e in td]
            cabinets.append([td[1], td[2], td[4]])
        return cabinets[1:]

    def get_students_classes(self):
        # подгружаем классы учеников
        url = 'https://edu.tatar.ru/school/academic_year/classes'
        classes = []
        get_classes = BeautifulSoup(self.get_html(url), 'lxml')
        for s in get_classes.find_all('tr'):
            td = s.find_all('td', string=True)
            td = [e.string.strip() for e in td]
            try:
                class_id = s.find('a', text='(Свойства класса)', href=True).get('href')
                class_id = str(class_id)[str(class_id).find('edu_class_id=') + len('edu_class_id='):]
                classes.append([class_id, td[0], td[1]])
            except Exception as e:
                print(e)
        return classes

    def get_students(self):
        classes = self.get_students_classes()
        url = 'https://edu.tatar.ru/school/journal/school_editor?edu_class_id='
        all_students = {}
        for student_class in classes:
            all_students[student_class[1] + student_class[2]] = {}
            get_classes = BeautifulSoup(self.get_html(url + student_class[0]), 'lxml').find('table', class_='table')
            for student in get_classes.find_all('tr'):
                td = student.find_all('td', string=True, title=True, class_='fio')
                td = [line.string.strip() for line in td]
                if td:
                    fio = td[0].split()
                    student_id = str(student.find('td', string=True, class_='fio').get('title')).split()[0]
                    student_id = student_id[student_id.find('login=') + len('login='):]
                    if len(fio) >= 2:
                        all_students[student_class[1] + student_class[2]][student_id] = fio
        return all_students

    def logout(self):
        self.s.post(self._LOGOUT_URL)
    #
    # def __del__(self):
    #     self.logout()


edu_tatar_user = EduTatar('1562000003', 'kbwtqbyyjgjkbc#1')
user = edu_tatar_user.connected()
print(user)
edu_tatar_user.logout()