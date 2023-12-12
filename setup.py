import sqlite3
import os

os.mkdir('data')
print('Create data folder')

with open('config.py', 'w+') as f:
    f.write("token = '' \n \
            database_name = 'base.db'")

conn = sqlite3.connect('base.db')
cursor = conn.cursor()
cursor.execute(
                'CREATE TABLE IF NOT EXISTS users ( \
                user_id INT, \
                login VARCHAR(100), \
                password VARCHAR(100), \
                csrf_token VARCHAR(255), \
                session_id VARCHAR(255), \
                student_id VARCHAR (255), \
                site_prefix VARCHAR (255), \
                current_quarter INT, \
                full_quarter INT, \
                alarm_state INT DEFAULT(0), \
                view_model INT NOT NULL DEFAULT(0), \
                alarm_lessons VARCHAR(255) DEFAULT "*" NOT NULL \
                )')
print('Create DB')
print('All done!')
