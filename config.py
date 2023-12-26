import os

token = os.getenv("bot_token")
postgres_username = os.getenv("db_user")
postgres_password = os.getenv("db_password")
postgres_db_name = os.getenv("db_name")
postgres_port = 5432
postgres_host = 'localhost'
developers = [int(os.getenv("developer_id"))]

debug = True
