import sqlite3
import config

class MySQL():
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
			list = [
				'login',
				'password',
				'csrf_token',
				'session_id'
			]
			dict = {}
			for item in list:
				self.cursor.execute(
					f"SELECT {item} "
					f"FROM users WHERE user_id = {user_id}"
					)
				result = self.cursor.fetchall()
				if len(result) == 0:
					dict[item] = None
				else:
					dict[item] = result[0][0]
			return dict

	def set_login_data(self, user_id: int, data: dict):
		with self.connection:
			list = [
				'login',
				'password',
				'csrf_token',
				'session_id'
			]
			for item in list:
				if data[item] is not None:
					self.cursor.execute(
						'UPDATE users SET '
						f'{item} = "{data[item]}" WHERE user_id = {user_id}'
						)
				