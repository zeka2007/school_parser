from aiogram import types
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp.db import session_maker, Student
from bothelp.keyboards import reply


async def notifications_menu_handler(message: types.Message):
    await message.answer('Параметры уведомлений:',
                         reply_markup=await reply.alarm_menu(message.from_user.id))


async def set_notification_on(message: types.Message):
    async with session_maker() as session:
        session: AsyncSession
        await session.execute(update(Student).where(Student.user_id == message.from_user.id).values(
            alarm_state=True
        ))
        await session.commit()
        await message.answer('Уведомления включены',
                             reply_markup=await reply.alarm_menu(message.from_user.id))


async def set_notification_off(message: types.Message):
    async with session_maker() as session:
        session: AsyncSession
        await session.execute(update(Student).where(Student.user_id == message.from_user.id).values(
            alarm_state=False
        ))
        await session.commit()
        await message.answer('Уведомления выключены',
                             reply_markup=await reply.alarm_menu(message.from_user.id))
