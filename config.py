import os

token = os.getenv("bot_token")
postgres_username = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db_name = os.getenv("POSTGRES_DB")
postgres_port = os.getenv("POSTGRES_PORT")
postgres_host = os.getenv("POSTGRES_HOST")

redis_host = os.getenv("REDIS_HOST")

developers = [int(os.getenv("developer_id"))]

debug = True
