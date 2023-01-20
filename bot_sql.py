import sqlite3
import config


class MySQL:
    def __init__(self):
        self.connection = sqlite3.connect('base.db')
        self.cursor = self.connection.cursor()

    def add_new_user(self, user_id: int):
        with self.connection:
            # cursor.execute(
            #     "CREATE TABLE users ("
            #     "user_id INT,"
            #     "login VARCHAR(100),"
            #     "password VARCHAR(100),"
            #     "csrf_token VARCHAR(255),"
            #     "session_id VARCHAR(255))"
            # )
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
