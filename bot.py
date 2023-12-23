import asyncio
import logging
import config
from aiogram import Dispatcher, Bot
from bot_events import register_user_commands


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    dp = Dispatcher()
    bot = Bot(config.token)

    register_user_commands(dp)

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
