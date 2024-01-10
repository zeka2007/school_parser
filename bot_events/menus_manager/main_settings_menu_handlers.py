from aiogram import types
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp import parser, tables
from bothelp.db import session_maker, Student
from bothelp.keyboards import reply, get_button_text, inline


async def settings_menu_handler(message: types.Message):
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == message.from_user.id))
        student: Student = result.scalars().one_or_none()
        model: bool = student.full_view_model
        if message.text == get_button_text(reply.setting_menu(), 0, 1):
            model = not model

            await session.execute(update(Student).where(Student.user_id == message.from_user.id).values(
                full_view_model=model
            ))
            await session.commit()

        alarm_lessons = student.alarm_lessons
        alarm_lessons_text = ''
        i = 0
        for item in alarm_lessons:
            if i == len(alarm_lessons) - 1:
                alarm_lessons_text = alarm_lessons_text + item
            else:
                alarm_lessons_text = alarm_lessons_text + item + '\n'
            i += 1

        if model:
            data = await parser.WebUser(student, session).get_student_info()
            result_text = tables.setting_menu_table(
                student,
                message.from_user.first_name,
                data['student_name'],
                data['class'],
                data['birthday']
            )

        else:
            result_text = tables.setting_menu_table(
                student,
                message.from_user.first_name
            )

        await message.answer(result_text,
                             reply_markup=reply.setting_menu())


async def update_all_data(message: types.Message):
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(
            Student.user_id == message.from_user.id
        ))
        student: Student = result.scalars().one_or_none()
        web_user = parser.WebUser(student, session)
        await web_user.get_current_quarter(True)
        await web_user.get_current_quarter_full(True)
        await web_user.get_lessons(True)
        await message.answer(
            'Информация об уроках и четвертях обновлена'
        )


async def notifications_menu_handler(message: types.Message):
    await message.answer('Параметры уведомлений:',
                         reply_markup=inline.notification_settings_list_menu())
