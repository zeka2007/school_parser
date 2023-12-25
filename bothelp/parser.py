import datetime
import logging
from datetime import timedelta
from typing import Callable, Dict, Any, Awaitable

import requests
from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import Message
from bs4 import BeautifulSoup
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp import date_format as df
from bothelp import file_manager as fm
from bothelp.db import Student, session_maker

agent = 'Mozilla/5.0 (X11; Linux i686; rv:80.0) Gecko/20100101 Firefox/80.0'
URL = 'https://schools.by/login'


class LoginCheckMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        if get_flag(data, 'chat_action') != 'WebService':
            return await handler(event, data)

        async with session_maker() as session:
            session: AsyncSession
            result = await session.execute(select(Student).where(Student.user_id == event.from_user.id))
            student: Student = result.scalars().one_or_none()

            if WebUser(student, session).is_login():
                return await handler(event, data)
            else:
                return await event.answer('Не удается получить доступ к сервису Schools.by, '
                                          'используя ваши данные для входа.')


# def check_login(func):
#     def wrapper(*args, **kwargs):
#         self = args[0]
#         if not self.is_login():
#             data = self.sql.get_login_data()
#             if login_user(self.user_id, data['login'], data['password']) is False:
#                 return False
#         return func(*args, **kwargs)
#
#     return wrapper


async def login_user(user: Student, session: AsyncSession):
    headers = {
        'user-agent': agent,
        'Referer': URL
    }

    client = requests.session()

    # Retrieve the CSRF token first
    req = client.get('https://schools.by/login')
    soup = BeautifulSoup(req.content, features="html.parser")
    csrftoken = soup.find('input', dict(name='csrfmiddlewaretoken'))['value']

    login_data = {
        'csrfmiddlewaretoken': csrftoken,
        'username': user.login,
        'password': user.password,
        '|123': '|123'
    }
    r = client.post(
        URL,
        data=login_data,
        headers=headers,
        allow_redirects=True,
        verify=False)
    redirect_url = r.url
    if redirect_url == URL:
        return False

    site_prefix = redirect_url.split('.')[0].replace('https://', '')
    student_id = int(redirect_url.split('/')[-1])

    csrf_token = ''
    session_id = ''

    for resp in r.history:
        csrf_token = resp.cookies['csrftoken']
        session_id = resp.cookies['sessionid']

    await session.execute(update(Student).where(Student.user_id == user.user_id).values(
        site_prefix=site_prefix,
        student_id=student_id,
        csrf_token=csrf_token,
        session_id=session_id
    ))
    await session.commit()
    return True


class WebUser:
    def __init__(self, student: Student, session: AsyncSession):

        self.cookies = {}
        self.student = student
        self.session = session

        self.user_data = {
            'login': self.student.login,
            'password': self.student.password,
            'csrf_token': self.student.csrf_token,
            'session_id': self.student.session_id
        }
        self.personal_url = f'https://{self.student.site_prefix}.schools.by'

        if self.user_data is not None:
            if self.user_data['csrf_token'] is not None and self.user_data['session_id'] is not None:
                self.cookies = {
                    'csrftoken': self.user_data['csrf_token'],
                    'sessionid': self.user_data['session_id'],
                    'slc_cookie': '{slcMakeBetter}{headerPopupsIsClosed}'
                }

    def is_login(self):
        get = requests.get(URL,
                           headers={'user-agent': agent},
                           cookies=self.cookies)
        if get.url == URL:
            if login_user(self.student, self.session) is False:
                return False
        return True

    def get_student_info(self):
        info = {
            'student_id': None,
            'student_name': None,
            'class': None,
            'birthday': None
        }
        req = requests.get(f'{self.personal_url}/pupil/{self.student.student_id}',
                           headers={'user-agent': agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        info['student_name'] = soup.find('h1').text.replace('\n', '')
        info['student_id'] = self.student.student_id

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

    def get_quarter_id(self, quarter: int = 0):

        req = requests.get(f'{self.personal_url}/pupil/{self.student.student_id}/dnevnik',
                           headers={'user-agent': agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        uls = soup.find_all('ul', {'id': f'db_quarters_menu_{self.student.student_id}'})
        for ul in uls:
            lis = ul.find_all('li')
            for li in lis:
                a = li.find('a')
                span = a.find('span').text
                if span == f'{quarter} четверть':
                    return a['quarter_id']

    async def get_current_quarter(self, upd: bool = False):
        data = self.student.current_quarter
        if data and not upd:
            return data

        req = requests.get(f'{self.personal_url}/pupil/{self.student.student_id}/dnevnik',
                           headers={'user-agent': agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        num = soup.find('a', {'class': 'current'}).text
        num = int(num.split(' ')[0])
        logging.info(f'update current quarter for {self.student.student_id}')
        self.student.current_quarter = num
        await self.session.commit()
        return num

    async def get_current_quarter_full(self, upd: bool = False):
        data = self.student.full_quarter
        if data and not upd:
            return data

        req = requests.get(f'{self.personal_url}/pupil/{self.student.student_id}/dnevnik',
                           headers={'user-agent': agent},
                           cookies=self.cookies).content
        soup = BeautifulSoup(req, features="html.parser")
        num = soup.find('a', {'class': 'current'})['quarter_id']
        num = int(num)
        logging.info(f'update full quarter for {self.student.student_id}')

        self.student.full_quarter = num
        await self.session.commit()
        return num

    def get_quarters_marks(self, quarter: int):

        q_marks = []

        req = requests.get(f'{self.personal_url}/pupil/{self.student.student_id}/dnevnik/last-page',
                           headers={'user-agent': agent},
                           cookies=self.cookies).content

        soup = BeautifulSoup(req, features="html.parser")
        table = soup.find('table', {'id': f'daybook-last-page-table-{self.student.student_id}'})
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

    def get_lessons(self, upd: bool = False):
        file_manager = fm.UserData(self.student.student_id)
        data = file_manager.get_lessons()
        if data is not None and not upd:
            return data

        lessons = []

        req = requests.get(f'{self.personal_url}/pupil/{self.student.student_id}/dnevnik/last-page',
                           headers={'user-agent': agent},
                           cookies=self.cookies).content

        soup = BeautifulSoup(req, features="html.parser")
        table = soup.find('table', {'class': 'itable ltable'})
        # print(self.student_id)
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
        logging.info(f'create lessons file for {self.student.student_id}')
        file_manager.set_lessons(lessons)

        return lessons

    def get_all_marks(self, quarter: int, lesson_name: str = None):
        interval = {}

        req = requests.get(f'{self.personal_url}/pupil/{self.student.student_id}/dnevnik/last-page',
                           headers={'user-agent': agent},
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
            req = requests.get(f'{self.personal_url}/pupil/'
                               f'{self.student.student_id}/dnevnik/quarter/{full_quarter}/week/{date_url}',
                               headers={'user-agent': agent},
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
                req = requests.get(f'{self.personal_url}/pupil/'
                                   f'{self.student.student_id}/dnevnik/quarter/{full_quarter}/week/{date_url}',
                                   headers={'user-agent': agent},
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

    def get_intervals(self):

        interval = {}

        req = requests.get(f'{self.personal_url}/pupil/{self.student.student_id}/dnevnik/last-page',
                           headers={'user-agent': agent},
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
