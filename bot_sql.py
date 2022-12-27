from mysql.connector import connect
import config

class MySQL():
	
	def add_new_user(self, user_id: int):
		with connect(
            host=config.BOT_SQL_HOST,
            user=config.BOT_SQL_USER,
            password=config.BOT_SQL_PASS,
            database=config.BOT_SQL_DB_NAME
       	) as connection:
			with connection.cursor() as cursor:
				# cursor.execute(
				#     "CREATE TABLE users ("
				#     "user_id INT,"
				#     "login VARCHAR(100),"
				#     "password VARCHAR(100),"
				#     "csrf_token VARCHAR(255),"
				#     "session_id VARCHAR(255))"
				# )
				cursor.execute(
					f"INSERT INTO users (user_id) VALUES ({user_id})"
					)
				connection.commit()

	def is_user_exist(self, user_id: int):
		with connect(
            host=config.BOT_SQL_HOST,
            user=config.BOT_SQL_USER,
            password=config.BOT_SQL_PASS,
            database=config.BOT_SQL_DB_NAME
       	) as connection:
			with connection.cursor() as cursor:
				cursor.execute(
					f"SELECT * FROM users WHERE user_id = {user_id}"
					)
				result = len(cursor.fetchall())
				if result == 0:
					return False
				else:
					return True

	def get_login_data(self, user_id: int):
		with connect(
            host=config.BOT_SQL_HOST,
            user=config.BOT_SQL_USER,
            password=config.BOT_SQL_PASS,
            database=config.BOT_SQL_DB_NAME
       	) as connection:
			with connection.cursor() as cursor:
				list = [
					'login',
					'password',
					'csrf_token',
					'session_id'
				]
				dict = {}
				for item in list:
					cursor.execute(
						f"SELECT {item} "
						f"FROM users WHERE user_id = {user_id}"
						)
					dict[item] = cursor.fetchall()[0][0]
				return dict

	def set_login_data(self, user_id: int, data: dict):
		with connect(
            host=config.BOT_SQL_HOST,
            user=config.BOT_SQL_USER,
            password=config.BOT_SQL_PASS,
            database=config.BOT_SQL_DB_NAME
       	) as connection:
			with connection.cursor() as cursor:
				list = [
					'login',
					'password',
					'csrf_token',
					'session_id'
				]
				for item in list:
					if data[item] is not None:
						cursor.execute(
							'UPDATE users SET '
							f'{item} = "{data[item]}" WHERE user_id = {user_id}'
							)
				connection.commit()