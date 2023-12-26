import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

import config
from bot_events import register_user_commands
from bothelp.db import create_database


async def main() -> None:
    if config.debug:
        logging.basicConfig(level=logging.DEBUG)

    dp = Dispatcher(storage=RedisStorage(Redis()))
    bot = Bot(config.token)

    register_user_commands(dp)

    await create_database()

    await dp.start_polling(bot)


async def send_notify(data):
    pass
    # for send in data:
    #     await dp.send_message(int(send['user_id']),
    #                            f'Установлена отметка: {send["added_marks"]} по предмету {send["lesson"]}')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped')
