import sqlite3
import config


class MySQL:
    def __init__(self):
        self.connection = sqlite3.connect('base.db')
        self.cursor = self.connection.cursor()

    def add_new_user(self, user_id: int):
        with self.connection:
            self.cursor.execute(
                f"INSERT INTO users (user_id) VALUES ({user_id})"
            )

    def delete_user(self, user_id: int):
        with self.connection:
            self.cursor.execute(
                f"DELETE FROM users WHERE user_id = {user_id}"
            )

    def is_user_exist(self, user_id: int):
        with self.connection:
            self.cursor.execute(
                f"SELECT * FROM users WHERE user_id = {user_id}"
            )
            result = len(self.cursor.fetchall())
            if result == 0:
                return False
            else:
                return True

    def get_login_data(self, user_id: int):
        with self.connection:
            items = [
                'login',
                'password',
                'csrf_token',
                'session_id'
            ]
            sql_dict = {}
            for item in items:
                self.cursor.execute(
                    f"SELECT {item} "
                    f"FROM users WHERE user_id = {user_id}"
                )
                result = self.cursor.fetchall()
                if len(result) == 0:
                    sql_dict[item] = None
                else:
                    sql_dict[item] = result[0][0]
            return sql_dict

    def set_login_data(self, user_id: int, data: dict):
        with self.connection:
            items = [
                'login',
                'password',
                'csrf_token',
                'session_id'
            ]
            for item in items:
                if data[item] is not None:
                    self.cursor.execute(
                        'UPDATE users SET '
                        f'{item} = "{data[item]}" WHERE user_id = {user_id}'
                    )

    def set_id(self, user_id: int, student_id: int):
        with self.connection:
            self.cursor.execute(
                'UPDATE users SET '
                f'student_id = {student_id} WHERE user_id = {user_id}'
            )

    def get_id(self, user_id: int):
        with self.connection:
            self.cursor.execute(
                f"SELECT student_id "
                f"FROM users WHERE user_id = {user_id}"
            )
            return self.cursor.fetchall()[0][0]

    def set_view_model(self, user_id: int, view_model: int):
        with self.connection:
            self.cursor.execute(
                'UPDATE users SET '
                f'view_model = {view_model} WHERE user_id = {user_id}'
            )

    def get_view_model(self, user_id: int):
        with self.connection:
            self.cursor.execute(
                f"SELECT view_model "
                f"FROM users WHERE user_id = {user_id}"
            )
            return self.cursor.fetchall()[0][0]

    def set_alarm_status(self, user_id: int, status: bool):
        with self.connection:
            dump = 0
            if status:
                dump = 1
            self.cursor.execute(
                'UPDATE users SET '
                f'alarm_state = {dump} WHERE user_id = {user_id}'
            )

    def get_alarm_status(self, user_id: int):
        with self.connection:
            self.cursor.execute(
                f"SELECT alarm_state "
                f"FROM users WHERE user_id = {user_id}"
            )
            sql_data = self.cursor.fetchall()[0][0]
            status = True
            if sql_data == 0:
                status = False
            return status

    def set_alarm_lessons(self, user_id: int, lessons: list):
        with self.connection:
            put = ''
            if not lessons:
                put = "*"
            else:
                i = 0
                for item in lessons:
                    if i == len(lessons) - 1:
                        put = put + item
                    else:
                        put = put + item + ', '
                    i += 1

            self.cursor.execute(
                'UPDATE users SET '
                f'alarm_lessons = "{put}" WHERE user_id = {user_id}'
            )

    def get_alarm_lessons(self, user_id: int):
        with self.connection:
            self.cursor.execute(
                f"SELECT alarm_lessons "
                f"FROM users WHERE user_id = {user_id}"
            )
            output = str(self.cursor.fetchall()[0][0])
            if output == "*":
                return "*"
            return output.split(', ')

    def get_all_users(self):
        with self.connection:
            self.cursor.execute(
                'SELECT * FROM users'
            )
            return self.cursor.fetchall()
