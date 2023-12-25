from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp import parser, file_manager
from bothelp.db import session_maker, Student
from bothelp.keyboards import reply


async def test_cmd(message: types.Message):
    await message.reply('Hello!')


async def send_welcome(message: types.Message, state: FSMContext):
    user_name = message.from_user.username
    user_id = message.from_user.id

    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == user_id))
        obj: Student = result.scalars().one_or_none()
        if obj is None:
            new_student = Student(
                user_id=user_id
            )
            session.add(new_student)
            await session.commit()
            keyboard = reply.not_login

        else:
            if await parser.login_user(obj, session):
                keyboard = reply.main_menu()
            else:
                keyboard = reply.not_login
        await state.set_state()
        await message.answer(
            f"Привет, {user_name}! ",
            reply_markup=keyboard)


async def exit_from_system(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == user_id))
        student: Student = result.scalars().one_or_none()
        file_manager.UserData(student.student_id).remove_all_data()

        await session.execute(delete(Student).where(Student.user_id == user_id))
        await session.commit()

        keyboard = reply.not_login

        await state.set_state()

        await message.answer('Вы были отключены от системы',
                             reply_markup=keyboard)
