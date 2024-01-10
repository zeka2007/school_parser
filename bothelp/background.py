import asyncio
import logging
import multiprocessing

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp import parser
from bothelp.db import session_maker, Student


# par = parser.WebUser(1134428403)
# manager = marks_manager.Manager()


async def update_data():
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student))
        for user in result.scalars().fetchall():
            user_obj = parser.WebUser(user, session)
            try:
                await user_obj.get_lessons(upd=True)
                await user_obj.get_current_quarter(upd=True)
                await user_obj.get_current_quarter_full(upd=True)
            except Exception as e:
                logging.warning(f'{e} for user {user.user_id}')


# async def update_alarm():
#     await manager.update_alarm()


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
            # await update_alarm()
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


def startup_all_process():
    multiprocessing.Process(target=start).start()
# multiprocessing.Process(target=start_alarm).start()

# update_data()
