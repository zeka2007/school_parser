import asyncio
import multiprocessing
from bothelp import bot_sql, parser, marks_manager

sql = bot_sql.MySQL()
# par = parser.WebUser(1134428403)
manager = marks_manager.Manager()


async def update_data():
    data = sql.get_all_users()
    for user in data:
        user_obj = parser.WebUser(user[0])
        result = user_obj.get_lessons(update=True)
        if result:
            user_obj.get_current_quarter(update=True)
            user_obj.get_current_quarter_full(update=True)
            return


async def update_alarm():
    await manager.update_alarm()


async def checker():
    try:
        while True:
            await update_data()
            await asyncio.sleep(86400)
    except (KeyboardInterrupt, SystemExit):
        pass


async def checker_alarm():
    try:
        while True:
            await update_alarm()
            await asyncio.sleep(360)
    except (KeyboardInterrupt, SystemExit):
        pass


# schedule.every().day.do(update_data)
def start():
    try:
        asyncio.run(checker())
    except (KeyboardInterrupt, SystemExit):
        pass


def start_alarm():
    try:
        asyncio.run(checker_alarm())
    except (KeyboardInterrupt, SystemExit):
        pass


multiprocessing.Process(target=start).start()
multiprocessing.Process(target=start_alarm).start()

# update_data()
