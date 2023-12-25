import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp import parser, multiprocesshelp
from bot import send_notify
import json

from bothelp.db import session_maker, Student

USER_ID: int = 0
ALARM_STATE: int = 6
DEMO: bool = True


def check_data(json_data_new, json_data_old):
    check_result = []

    for user in json_data_old:
        if json_data_new[user] != json_data_old[user]:
            for i in range(len(json_data_old[user])):
                marks_new = json_data_new[user][i]["marks"]
                marks_old = json_data_old[user][i]["marks"]
                if marks_new != marks_old:
                    list_difference = []
                    if len(marks_new) > len(marks_old):
                        for el in marks_new[len(marks_old):]:
                            list_difference.append(el)
                        error_list = []
                        for error in marks_new[len(marks_old):]:
                            error_list.append(error)
                            print('el', error)
                        marks_new_opt = marks_new[:len(list_difference) * -1]
                        print('marks', marks_new[len(marks_old):])
                        if error_list == marks_new[len(marks_old):]:
                            marks_new = marks_new_opt
                        else:
                            list_difference = []
                            added_marks_count = len(marks_new) - len(marks_old)
                            count = 0
                            for element in range(len(marks_old)):
                                # print(marks_new[element], marks_old[element])
                                if count == added_marks_count: break
                                if marks_new[element] != marks_old[element]:
                                    list_difference.append(marks_new[element])
                                    count += 1

                    if len(marks_new) == len(marks_old):
                        for element in range(len(marks_old)):
                            # print(marks_new[element], marks_old[element])
                            if marks_new[element] != marks_old[element]:
                                list_difference.append(marks_new[element])
                    print(list_difference)
                # check_result.append(
                #     {
                #         "user_id": user,
                #         "lesson": lessons["lesson"],
                #         "added_marks": json_data_new_marks[num]
                #     }
                # )

    return check_result


async def get_data_for_json(user_id: int):
    if DEMO:
        return [{
            'lesson': "DEMO lesson",
            'marks': [4, 7, 4, 7, 8, 8, 7]
        },
            {
                'lesson': "DEMO lesson2",
                'marks': [6, 7, 8, 6]
            }
        ]
    user_json = []
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == user_id))
        web_user = parser.WebUser(result.scalars().one_or_none(), session)
        lessons = web_user.get_lessons()
        for lesson in lessons:

            marks = multiprocesshelp.Multiprocess(web_user).get_all_marks(
                await web_user.get_current_quarter(),
                lesson
            )
            user_json.append(
                {
                    'lesson': lesson,
                    'marks': marks
                }
            )
            print({
                'lesson': lesson,
                'marks': marks
            })
        return user_json


class Manager:
    def __init__(self):
        self.file_path = 'data/marks.json'

    async def update_alarm(self):
        async with session_maker() as session:
            session: AsyncSession
            result = await session.execute(select(Student))
            data = result.scalars().fetchall()
            json_data_old = {}
            if os.stat(self.file_path).st_size != 0:
                f = open(self.file_path, 'r')
                json_data_old = json.load(f)
                f.close()
            for user in data:
                user: Student
                if user.alarm_state:
                    # print(self.get_data_for_json(user[USER_ID]))
                    if os.stat(self.file_path).st_size != 0:
                        f = open(self.file_path, 'r')
                        json_data = json.load(f)
                        f.close()
                        f = open(self.file_path, 'w')
                        json_data[str(user.user_id)] = get_data_for_json(user.user_id)
                        json.dump(json_data, f, sort_keys=True, indent=4, ensure_ascii=False)
                        f.close()

                    if os.stat(self.file_path).st_size == 0:
                        file = open(self.file_path, 'w')
                        in_json = await get_data_for_json(user.user_id)
                        in_json_end = {
                            user.user_id: in_json
                        }
                        json.dump(in_json_end, file, sort_keys=True, indent=4, ensure_ascii=False)
                        print('write data')
                        file.close()

            if os.stat(self.file_path).st_size != 0:
                f = open(self.file_path, 'r')
                json_data_new = json.load(f)
                f.close()

                result = check_data(json_data_new, json_data_old)
                if result is not None:
                    await send_notify(result)
