from aiogram import types

from bothelp import bot_sql
from bothelp.keyboards import reply


async def notifications_menu_handler(message: types.Message):
    await message.answer('Параметры уведомлений:',
                         reply_markup=reply.alarm_menu(message.from_user.id))


async def set_notification_on(message: types.Message):
    database = bot_sql.MySQL(message.from_user.id)
    database.set_alarm_status(True)
    await message.answer('Уведомления включены',
                         reply_markup=reply.alarm_menu(message.from_user.id))


async def set_notification_off(message: types.Message):
    database = bot_sql.MySQL(message.from_user.id)
    database.set_alarm_status(False)
    await message.answer('Уведомления выключены',
                         reply_markup=reply.alarm_menu(message.from_user.id))
