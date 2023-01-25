import sqlite3
conn = sqlite3.connect('base.db')
cursor = conn.cursor()
cursor.execute(
                 "CREATE TABLE users ("
                 "user_id INT,"
                 "login VARCHAR(100),"
                 "password VARCHAR(100),"
                 "csrf_token VARCHAR(255),"
                 "session_id VARCHAR(255),"
                 "student_id VARCHAR(255))"
            )