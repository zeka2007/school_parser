import requests
from bs4 import BeautifulSoup
import bot_sql

sql = bot_sql.MySQL()


class Parser():
    def __init__(self):
        self.agent = 'Mozilla/5.0 (X11; Linux i686; rv:80.0) Gecko/20100101 Firefox/80.0'
        self.URL = 'https://schools.by/login'

    def login(self, user_id: int, login: str, password: str):
        URL = 'https://schools.by/login'
        headers = {
            'user-agent': self.agent,
            'Referer': URL
        }

        client = requests.session()

        # Retrieve the CSRF token first
        req = client.get('https://schools.by/login')
        soup = BeautifulSoup(req.content, features="html.parser")
        csrftoken = soup.find('input', dict(name='csrfmiddlewaretoken'))['value']

        login_data = {
            'csrfmiddlewaretoken': csrftoken,
            'username': login,
            'password': password,
            '|123': '|123'
        }
        r = client.post(
            URL,
            data=login_data,
            headers=headers,
            allow_redirects=True,
            verify=False)
        if r.url == URL:
            return False

        for resp in r.history:
            sql.set_login_data(
                user_id,
                {
                    'login': None,
                    'password': None,
                    'csrf_token': resp.cookies['csrftoken'],
                    'session_id': resp.cookies['sessionid'],
                }
            )
        return True

    def is_login(self, user_id):
        data = sql.get_login_data(user_id)
        if data is None:
            return False
        if data['csrf_token'] is None or data['session_id'] is None:
            return False
        cookies = {
            'csrftoken': data['csrf_token'],
            'sessionid': data['session_id'],
            'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
        }
        get = requests.get(self.URL,
                           headers={'user-agent': self.agent},
                           cookies=cookies)
        if get.url == self.URL:
            return False
        return True

    def get_id(self, user_id):
        if not self.is_login(user_id):
            data = sql.get_login_data(user_id)
            if self.login(user_id, data['login'], data['password']) is False:
                return False

        data = sql.get_login_data(user_id)
        cookies = {
            'csrftoken': data['csrf_token'],
            'sessionid': data['session_id'],
            'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
        }

        req = requests.get(self.URL,
                           headers={'user-agent': self.agent},
                           cookies=cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        divs = soup.find_all('div', {'class': 'cnt'})
        for div in divs:
            student_id = div.find('b')
            if student_id is not None:
                return student_id.text

    def get_quarter_id(self, user_id: int, quarter: int = 0):
        if not self.is_login(user_id):
            data = sql.get_login_data(user_id)
            if self.login(user_id, data['login'], data['password']) is False:
                return False

        data = sql.get_login_data(user_id)
        cookies = {
            'csrftoken': data['csrf_token'],
            'sessionid': data['session_id'],
            'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
        }

        student_id = sql.get_id(user_id)

        req = requests.get(f'https://209minsk.schools.by/pupil/{student_id}/dnevnik',
                           headers={'user-agent': self.agent},
                           cookies=cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        uls = soup.find_all('ul', {'id': f'db_quarters_menu_{student_id}'})
        for ul in uls:
            lis = ul.find_all('li')
            for li in lis:
                a = li.find('a')
                span = a.find('span').text
                if span == f'{quarter} четверть':
                    return a['quarter_id']

    def get_quarters_marks(self, user_id: int, quarter: int):
        if not self.is_login(user_id):
            data = sql.get_login_data(user_id)
            if self.login(user_id, data['login'], data['password']) is False:
                return False

        data = sql.get_login_data(user_id)
        cookies = {
            'csrftoken': data['csrf_token'],
            'sessionid': data['session_id'],
            'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
        }

        student_id = sql.get_id(user_id)
        q_marks = []

        req = requests.get(f'https://209minsk.schools.by/pupil/{student_id}/dnevnik/last-page',
                           headers={'user-agent': self.agent},
                           cookies=cookies).content

        soup = BeautifulSoup(req, features="html.parser")
        table = soup.find('table', {'id': f'daybook-last-page-table-{student_id}'})
        body = table.find('tbody')
        trs = body.find_all('tr', {'class': 'marks'})
        for tr in trs:
            tds = tr.find_all('td', {'class': 'qmark'})
            mark = tds[quarter - 1].text
            if mark == '':
                q_marks.append('Нет')
            else:
                q_marks.append(mark)

        return q_marks

    def get_lessons(self, user_id: int):
        if not self.is_login(user_id):
            data = sql.get_login_data(user_id)
            if self.login(user_id, data['login'], data['password']) is False:
                return False

        data = sql.get_login_data(user_id)
        cookies = {
            'csrftoken': data['csrf_token'],
            'sessionid': data['session_id'],
            'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
        }

        student_id = sql.get_id(user_id)
        lessons = []

        req = requests.get(f'https://209minsk.schools.by/pupil/{student_id}/dnevnik/last-page',
                           headers={'user-agent': self.agent},
                           cookies=cookies).content

        soup = BeautifulSoup(req, features="html.parser")
        table = soup.find('table', {'class': 'itable ltable'})
        body = table.find('tbody')
        trs = body.find_all('tr')
        for tr in trs:
            td = tr.find('td')
            a = td.find('a')
            if a is not None:
                lesson_name = a.text
                lesson_name = lesson_name.replace('\n', '')
                lessons.append(lesson_name)

        return lessons
