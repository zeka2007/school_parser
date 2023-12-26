from aiogram import types
from aiogram.types import BotCommand

from bot_events.administration.hight_level_commands import set_admin_level
from bot_events.administration.user_view import get_user_info


async def admin_help(message: types.Message):
    text = 'Список команд:\n\n'
    for command in admin_commands:
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
    }
]
