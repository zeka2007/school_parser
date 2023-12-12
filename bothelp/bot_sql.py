import sqlite3
import config


class MySQL:
    def __init__(self, user_id: int, base_name: str = config.database_name):
        self.connection = sqlite3.connect(base_name)
        self.cursor = self.connection.cursor()
        self.user_id = user_id

    def add_new_user(self):
        with self.connection:
            self.cursor.execute(
                f"INSERT INTO users (user_id) VALUES ({self.user_id})"
            )

    def delete_user(self):
        with self.connection:
            self.cursor.execute(
                f"DELETE FROM users WHERE user_id = {self.user_id}"
            )

    def is_user_exist(self):
        with self.connection:
            self.cursor.execute(
                f"SELECT * FROM users WHERE user_id = {self.user_id}"
            )
            result = len(self.cursor.fetchall())
            if result == 0:
                return False
            else:
                return True

    def get_login_data(self):
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
                    f"FROM users WHERE user_id = {self.user_id}"
                )
                result = self.cursor.fetchall()
                if len(result) == 0:
                    sql_dict[item] = None
                else:
                    sql_dict[item] = result[0][0]
            return sql_dict

    def set_login_data(self, data: dict):
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
                        f'{item} = "{data[item]}" WHERE user_id = {self.user_id}'
                    )

    def set_id(self, student_id: int):
        with self.connection:
            self.cursor.execute(
                'UPDATE users SET '
                f'student_id = {student_id} WHERE user_id = {self.user_id}'
            )

    def get_id(self):
        with self.connection:
            self.cursor.execute(
                f"SELECT student_id "
                f"FROM users WHERE user_id = {self.user_id}"
            )
            return self.cursor.fetchall()[0][0]

    def set_site_prefix(self, prefix: str):
        with self.connection:
            self.cursor.execute(
                'UPDATE users SET '
                f'site_prefix = "{prefix}" WHERE user_id = {self.user_id}'
            )

    def get_site_prefix(self):
        with self.connection:
            self.cursor.execute(
                f"SELECT site_prefix "
                f"FROM users WHERE user_id = {self.user_id}"
            )
            return self.cursor.fetchall()[0][0]

    def get_current_quarter(self):
        with self.connection:
            self.cursor.execute(
                f"SELECT current_quarter "
                f"FROM users WHERE user_id = {self.user_id}"
            )
            return self.cursor.fetchall()[0][0]

    def set_current_quarter(self, quarter: int):
        with self.connection:
            self.cursor.execute(
                'UPDATE users SET '
                f'current_quarter = {quarter} WHERE user_id = {self.user_id}'
            )

    def get_full_quarter(self):
        with self.connection:
            self.cursor.execute(
                f"SELECT full_quarter "
                f"FROM users WHERE user_id = {self.user_id}"
            )
            return self.cursor.fetchall()[0][0]

    def set_full_quarter(self, quarter: int):
        with self.connection:
            self.cursor.execute(
                'UPDATE users SET '
                f'full_quarter = {quarter} WHERE user_id = {self.user_id}'
            )

    def set_view_model(self, view_model: int):
        with self.connection:
            self.cursor.execute(
                'UPDATE users SET '
                f'view_model = {view_model} WHERE user_id = {self.user_id}'
            )

    def get_view_model(self):
        with self.connection:
            self.cursor.execute(
                f"SELECT view_model "
                f"FROM users WHERE user_id = {self.user_id}"
            )
            return self.cursor.fetchall()[0][0]

    def set_alarm_status(self, status: bool):
        with self.connection:
            dump = 0
            if status:
                dump = 1
            self.cursor.execute(
                'UPDATE users SET '
                f'alarm_state = {dump} WHERE user_id = {self.user_id}'
            )

    def get_alarm_status(self):
        with self.connection:
            self.cursor.execute(
                f"SELECT alarm_state "
                f"FROM users WHERE user_id = {self.user_id}"
            )
            sql_data = self.cursor.fetchall()[0][0]
            status = True
            if sql_data == 0:
                status = False
            return status

    def set_alarm_lessons(self, lessons: list):
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
                f'alarm_lessons = "{put}" WHERE user_id = {self.user_id}'
            )

    def get_alarm_lessons(self):
        with self.connection:
            self.cursor.execute(
                f"SELECT alarm_lessons "
                f"FROM users WHERE user_id = {self.user_id}"
            )
            output = str(self.cursor.fetchall()[0][0])
            if output == "*":
                return "*"
            return output.split(', ')

    @staticmethod
    def get_all_users(base_name: str = config.database_name):
        connection = sqlite3.connect(base_name)
        with connection:
            cursor = connection.cursor()
            cursor.execute(
                'SELECT * FROM users'
            )
            return cursor.fetchall()
