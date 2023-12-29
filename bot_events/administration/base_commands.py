from aiogram import types
from aiogram.types import BotCommand
from sqlalchemy import select

import config
from bot_events.administration.hight_level_commands import set_admin_level
from bot_events.administration.notifications import send_notify_command
from bot_events.administration.user_view import get_user_info
from bothelp.db import session_maker, Student


async def admin_help(message: types.Message):
    async with session_maker() as session:
        result = await session.execute(select(Student).where(Student.user_id == message.from_user.id))
        student: Student = result.scalars().one()
        text = 'Список команд:\n\n'
        for command in admin_commands:
            if student.admin_level >= command['level'] or message.from_user.id in config.developers:
                text += f'/{command["command"].command} - {command["command"].description}\n'
        await message.answer(text)


admin_commands = [
    {
        'command': BotCommand(command='ahelp', description='Информация о командах администратора'),
        'func': admin_help,
        'level': 1
    },
    {
        'command': BotCommand(command='user_info', description='Получение информация о пользователи'),
        'func': get_user_info,
        'level': 1
    },
    {
        'command': BotCommand(command='set_alevel', description='Установить уровень администрации пользователю'),
        'func': set_admin_level,
        'level': -1
    },
    {
        'command': BotCommand(command='send_message', description='Отправить сообщение определенным пользователям'),
        'func': send_notify_command,
        'level': 3
    }
]
