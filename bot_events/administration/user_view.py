from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_states.states import AdminRequestId
from bothelp.db import session_maker, Student
from bothelp.keyboards import inline
from bothelp.parser import WebUser
from bothelp.tables import admin_user_info_table


async def get_user_info(message: types.Message, state: FSMContext):
    await state.set_state(AdminRequestId.state)
    await message.answer('Выберите способ поиска:',
                         reply_markup=inline.get_user_method_menu())


async def get_user_info_method(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data_id = int(callback.data.split('_')[-1])

    if data_id == 1:
        await callback.message.edit_text('Введите Telegram id пользователя:\n/cancel - для отмены')
    if data_id == 2:
        await callback.message.edit_text('Введите School.by id пользователя:\n/cancel - для отмены')

    await state.set_data({'method': data_id})

    await state.set_state(AdminRequestId.state)


async def get_user_info_state(message: types.Message, state: FSMContext):

    async with session_maker() as session:
        data = await state.get_data()
        method: int = data.get('method')

        if not message.text.isnumeric():
            await state.set_state(AdminRequestId.state)
            return message.answer('Введите правильный id!')
        session: AsyncSession
        if method == 1:
            result = await session.execute(select(Student).where(Student.user_id == int(message.text)))

        if method == 2:
            result = await session.execute(select(Student).where(Student.student_id == int(message.text)))

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
