import os.path

import requests
from bs4 import BeautifulSoup
from bothelp import bot_sql
import datetime
from datetime import timedelta
from bothelp import date_format as df

sql = bot_sql.MySQL()


def check_login(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        if not self.is_login():
            data = sql.get_login_data(self.user_id)
            if self.login(self.user_id, data['login'], data['password']) is False:
                return False
        return func(*args, **kwargs)

    return wrapper


class WebUser:
    def __init__(self, user_id: int):
        self.agent = 'Mozilla/5.0 (X11; Linux i686; rv:80.0) Gecko/20100101 Firefox/80.0'
        self.URL = 'https://schools.by/login'

        self.user_data = sql.get_login_data(user_id)
        self.user_id = user_id

        self.student_id = sql.get_id(self.user_id)

        if self.user_data is not None:
            if self.user_data['csrf_token'] is not None and self.user_data['session_id'] is not None:
                self.cookies = {
                    'csrftoken': self.user_data['csrf_token'],
                    'sessionid': self.user_data['session_id'],
                    'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
                }

    def login(self, login: str, password: str):
        headers = {
            'user-agent': self.agent,
            'Referer': self.URL
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
            self.URL,
            data=login_data,
            headers=headers,
            allow_redirects=True,
            verify=False)
        if r.url == self.URL:
            return False

        for resp in r.history:
            sql.set_login_data(
                self.user_id,
                {
                    'login': None,
                    'password': None,
                    'csrf_token': resp.cookies['csrftoken'],
                    'session_id': resp.cookies['sessionid'],
                }
            )
        return True

    def is_login(self):
        get = requests.get(self.URL,
                           headers={'user-agent': self.agent},
                           cookies=self.cookies)
        if get.url == self.URL:
            return False
        return True

    @check_login
    def get_id(self):

        req = requests.get(self.URL,
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        divs = soup.find_all('div', {'class': 'cnt'})
        for div in divs:
            student_id = div.find('b')
            if student_id is not None:
                return student_id.text

    @check_login
    def get_student_info(self):
        info = {
            'student_id': None,
            'student_name': None,
            'class': None,
            'birthday': None
        }
        req = requests.get(self.URL,
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        info['student_name'] = soup.find('h1').text.replace('\n', '')
        divs = soup.find_all('div', {'class': 'cnt'})
        for div in divs:
            student_id = div.find('b')
            if student_id is not None:
                info['student_id'] = int(student_id.text)

        divs = soup.find_all('div', {'class': 'pp_line'})
        for div in divs:
            b = div.find('b')
            if b is not None:
                if b.text.startswith('Ученик'):
                    text = div.find('a').text
                    info['class'] = text.replace('-го', '')

            label = div.find('div', {'class': 'label'})
            if label is not None:
                if label.text.find('Дата рождения') != -1:
                    info['birthday'] = div.find('div', {'class': 'cnt'}).text.replace('\n', '')

        return info

    @check_login
    def get_quarter_id(self, quarter: int = 0):

        req = requests.get(f'https://209minsk.schools.by/pupil/{self.student_id}/dnevnik',
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        uls = soup.find_all('ul', {'id': f'db_quarters_menu_{self.student_id}'})
        for ul in uls:
            lis = ul.find_all('li')
            for li in lis:
                a = li.find('a')
                span = a.find('span').text
                if span == f'{quarter} четверть':
                    return a['quarter_id']

    @check_login
    def get_current_quarter(self, update: bool = False):
        if os.path.exists('data/current_quarter.txt') and not update:
            with open('data/current_quarter.txt', 'r') as file:
                return int(file.read())

        req = requests.get(f'https://209minsk.schools.by/pupil/{self.student_id}/dnevnik',
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        num = soup.find('a', {'class': 'current'}).text
        num = int(num.split(' ')[0])
        print('create file 1')
        with open('data/current_quarter.txt', 'w') as file:
            file.write(str(num))
        return num

    @check_login
    def get_current_quarter_full(self, update: bool = False):
        if os.path.exists('data/full_current_quarter.txt') and not update:
            with open('data/full_current_quarter.txt', 'r') as file:
                return int(file.read())

        req = requests.get(f'https://209minsk.schools.by/pupil/{self.student_id}/dnevnik',
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        num = soup.find('a', {'class': 'current'})['quarter_id']
        num = int(num)
        print('create file 2')

        with open('data/full_current_quarter.txt', 'w') as file:
            file.write(str(num))
        return num

    @check_login
    def get_quarters_marks(self, quarter: int):

        q_marks = []

        req = requests.get(f'https://209minsk.schools.by/pupil/{self.student_id}/dnevnik/last-page',
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content

        soup = BeautifulSoup(req, features="html.parser")
        table = soup.find('table', {'id': f'daybook-last-page-table-{self.student_id}'})
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

    @check_login
    def get_lessons(self, update: bool = False):
        if os.path.exists('data/lessons.txt') and not update:
            with open('data/lessons.txt', 'r') as file:
                return file.read().split('\n')[0:-1]

        lessons = []

        req = requests.get(f'https://209minsk.schools.by/pupil/{self.student_id}/dnevnik/last-page',
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content

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
                if lesson_name.startswith(' '):
                    i = 0
                    l_list = list(lesson_name)
                    for letter in l_list:
                        if letter == ' ':
                            l_list[i] = ''
                        else:
                            break
                        i += 1
                    lesson_name = ''.join(l_list)
                if lesson_name.endswith(' '):
                    l_list = list(lesson_name)
                    i = len(l_list) - 1
                    for _ in l_list:
                        if l_list[i] == ' ':
                            l_list[i] = ''
                        else:
                            break
                        i -= 1
                    lesson_name = ''.join(l_list)
                lessons.append(lesson_name)
        print('create file 3')
        with open('data/lessons.txt', 'w') as file:
            write = ''
            for lesson in lessons:
                write = write + lesson + '\n'
            file.write(write)
        return lessons

    @check_login
    def get_all_marks(self, quarter: int, lesson_name: str = None):

        interval = {}

        req = requests.get(f'https://209minsk.schools.by/pupil/{self.student_id}/dnevnik/last-page',
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content

        soup = BeautifulSoup(req, features="html.parser")
        tds = soup.find_all('td', {'class': 'qdates'})
        i = 1
        for td in tds:
            result = td.text.replace('-', ' ')
            result = result.replace('\n', '')
            result = result.split(' ')
            date_start = int(result[0])
            month_start = df.formats[result[1]]
            date_end = int(result[2])
            month_end = df.formats[result[3]]
            interval[i] = {
                'start_date': date_start,
                'start_month': month_start,
                'end_date': date_end,
                'end_month': month_end,
            }
            i = i + 1

        # get date
        current_year = datetime.datetime.now().year
        if quarter <= 2:
            start_date = datetime.datetime(current_year - 1,
                                           interval[quarter]['start_month'],
                                           interval[quarter]['start_date'])
            end_date = datetime.datetime(current_year - 1,
                                         interval[quarter]['end_month'],
                                         interval[quarter]['end_date'])
        else:
            start_date = datetime.datetime(current_year,
                                           interval[quarter]['start_month'],
                                           interval[quarter]['start_date'])
            end_date = datetime.datetime(current_year,
                                         interval[quarter]['end_month'],
                                         interval[quarter]['end_date'])

        # get marks in this quarter
        full_quarter = self.get_quarter_id(quarter)

        date = start_date

        marks = []

        while True:
            if date > end_date:
                break
            # print(date)
            date_url = date.strftime("%Y-%m-%d")
            req = requests.get(f'https://209minsk.schools.by/pupil/'
                               f'{self.student_id}/dnevnik/quarter/{full_quarter}/week/{date_url}',
                               headers={'user-agent': self.agent},
                               cookies=self.cookies).content

            soup = BeautifulSoup(req, features="html.parser")
            days = soup.find_all('div', {'class': 'db_day'})
            for day in days:
                lessons = day.find('tbody').find_all('tr')
                for lesson in lessons:
                    ln = lesson.find('td', {'class': 'lesson'})
                    ln = ln.text
                    ln = ln.replace('\n', '')[2:]
                    if ln != '':
                        if ln == lesson_name:
                            mark = lesson.find('div', {'class': 'mark_box'}).text
                            mark = mark.replace('\n', '')
                            # print(f'[{mark}]')
                            if mark != '':
                                if mark.find('/') != -1:
                                    marks.append(int(mark.split('/')[0]))
                                    # print(mark.split('/')[0])
                                    marks.append(int(mark.split('/')[1]))
                                else:
                                    marks.append(int(mark))

            date = date + timedelta(weeks=1)

        return marks

    @check_login
    def get_all_marks_from_page(self, quarter: int, page: int, lesson_name: str = None):

        interval = self.get_intervals()

        # get date
        current_year = datetime.datetime.now().year
        if quarter <= 2:
            start_date = datetime.datetime(current_year,
                                           interval[quarter]['start_month'],
                                           interval[quarter]['start_date'])
            end_date = datetime.datetime(current_year,
                                         interval[quarter]['end_month'],
                                         interval[quarter]['end_date'])
        else:
            start_date = datetime.datetime(current_year,
                                           interval[quarter]['start_month'],
                                           interval[quarter]['start_date'])
            end_date = datetime.datetime(current_year,
                                         interval[quarter]['end_month'],
                                         interval[quarter]['end_date'])

        # get marks in this quarter
        full_quarter = self.get_quarter_id(quarter)

        date = start_date

        marks = []

        i = 1

        while True:
            if date > end_date:
                break

            if i == page:
                # print(date)
                date_url = date.strftime("%Y-%m-%d")
                req = requests.get(f'https://209minsk.schools.by/pupil/'
                                   f'{self.student_id}/dnevnik/quarter/{full_quarter}/week/{date_url}',
                                   headers={'user-agent': self.agent},
                                   cookies=self.cookies).content

                soup = BeautifulSoup(req, features="html.parser")
                days = soup.find_all('div', {'class': 'db_day'})
                for day in days:
                    lessons = day.find('tbody').find_all('tr')
                    for lesson in lessons:
                        ln = lesson.find('td', {'class': 'lesson'}).text
                        ln = ln.replace('\n', '')[2:]
                        ln = ln.strip()

                        if ln != '':
                            if ln == lesson_name:
                                mark = lesson.find('div', {'class': 'mark_box'}).text
                                mark = mark.replace('\n', '')
                                # print(f'[{mark}]')
                                if mark != '':
                                    if mark.find('/') != -1:
                                        marks.append(int(mark.split('/')[0]))
                                        # print(mark.split('/')[0])
                                        marks.append(int(mark.split('/')[1]))
                                    else:
                                        marks.append(int(mark))

            date = date + timedelta(weeks=1)
            i = i + 1

        return marks

    @check_login
    def get_intervals(self):

        interval = {}

        req = requests.get(f'https://209minsk.schools.by/pupil/{self.student_id}/dnevnik/last-page',
                           headers={'user-agent': self.agent},
                           cookies=self.cookies).content

        soup = BeautifulSoup(req, features="html.parser")
        tds = soup.find_all('td', {'class': 'qdates'})
        i = 1
        for td in tds:
            result = td.text.replace('-', ' ')
            result = result.replace('\n', '')
            result = result.strip()
            result = result.split(' ')

            date_start = int(result[0])
            month_start = df.formats[result[1]]
            date_end = int(result[2])
            month_end = df.formats[result[3]]
            interval[i] = {
                'start_date': date_start,
                'start_month': month_start,
                'end_date': date_end,
                'end_month': month_end,
            }
            i = i + 1

        return interval

    @check_login
    def get_pages_count(self, quarter: int):

        interval = self.get_intervals()
        # get date
        current_year = datetime.datetime.now().year
        if quarter <= 2:
            start_date = datetime.datetime(current_year - 1,
                                           interval[quarter]['start_month'],
                                           interval[quarter]['start_date'])
            end_date = datetime.datetime(current_year - 1,
                                         interval[quarter]['end_month'],
                                         interval[quarter]['end_date'])
        else:
            start_date = datetime.datetime(current_year,
                                           interval[quarter]['start_month'],
                                           interval[quarter]['start_date'])
            end_date = datetime.datetime(current_year,
                                         interval[quarter]['end_month'],
                                         interval[quarter]['end_date'])

        date = end_date - start_date

        return int(((date.days - (date.days % 7)) / 7) + 1)
