from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_states.states import AdminRequestId
from bothelp.db import session_maker, Student
from bothelp.parser import WebUser
from bothelp.tables import admin_user_info_table


async def get_user_info(message: types.Message, state: FSMContext):
    await state.set_state(AdminRequestId.state)
    await message.answer('Введите id пользователя; /cancel - для отмены')


async def get_user_info_state(message: types.Message, state: FSMContext):

    async with session_maker() as session:

        if message.text == '/cancel':
            await state.set_state()
            await message.answer('Отменено')
            return

        if not message.text.isnumeric():
            await state.set_state(AdminRequestId.state)
            return message.answer('Введите правильный Telegram id!')
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == int(message.text)))
        student: Student = result.scalars().one_or_none()

        await state.set_state()

        if student is None:
            await state.set_state()
            return await message.answer('Нет такого пользователя')

        user_obj = WebUser(student, session)

        if not await user_obj.is_login():
            await state.set_state()
            return await message.answer('Пользователь не авторизован')

        user_info = user_obj.get_student_info()
        text = admin_user_info_table(
            student.user_id,
            student.reg_date,
            student.alarm_state,
            student.is_block,
            student.admin_level,
            user_info['student_id'],
            user_info['student_name'],
            user_info['class'],
            user_info['birthday'],
            ','.join(student.alarm_lessons)
        )

        await message.answer(text)
