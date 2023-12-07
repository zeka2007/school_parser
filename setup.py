import sqlite3
import os

os.mkdir('data')
print('Create folder data')
open('data/current_quarter.txt', 'w+')
print('Create file current_quarter.txt')
open('data/full_current_quarter.txt', 'w+')
print('Create file full_current_quarter.txt')
open('data/lessons.txt', 'w+')
print('Create file lessons.txt')
open('data/marks.json', 'w+')
print('Create file marks.json')
open('data/marks_old.json', 'w+')
print('Create file marks_old.json')

with open('config.py', 'w+') as f:
    f.write("token = ''")

conn = sqlite3.connect('base.db')
cursor = conn.cursor()
cursor.execute(
                 'CREATE TABLE users ( \
                 user_id INT, \
                 login VARCHAR(100), \
                 password VARCHAR(100), \
                 csrf_token VARCHAR(255), \
                 session_id VARCHAR(255), \
                 student_id VARCHAR (255), \
                 alarm_state INT DEFAULT(0), \
                 view_model INT NOT NULL DEFAULT(0), \
                 alarm_lessons VARCHAR(255) DEFAULT "*" NOT NULL \
                 )')
print('Create DB')
print('All done!')

