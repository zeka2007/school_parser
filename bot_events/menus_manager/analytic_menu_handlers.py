from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp import parser, tables, multiprocesshelp
from bothelp.db import session_maker, Student
from bothelp.keyboards import inline


async def quarter_analytic_handler(message: types.Message):
    await message.answer('Выберите четверти для сравнения',
                         reply_markup=inline.quarter_inline_menu())


async def marks_analytic_handler(message: types.Message):
    user_id = message.from_user.id
    await message.answer('Выберите предмет',
                         reply_markup=await inline.lessons_inline_menu(user_id))


async def quarter_analytic_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    async with session_maker() as session:
        session: AsyncSession
        quarter = int(callback_query.data[-1])
        wait_message = await callback_query.message.answer('Получение информации...')
        result = await session.execute(select(Student).where(Student.user_id == callback_query.from_user.id))
        user_obj = parser.WebUser(result.scalars().one_or_none(), session)

        lessons = user_obj.get_lessons()
        if quarter == 5:
            marks_dict = {}
            for i in range(1, 5):
                marks_q = user_obj.get_quarters_marks(i)
                marks_dict[i] = marks_q
            text = tables.quarter_marks_analytics_all(lessons,
                                                      marks_dict)
            await wait_message.edit_text(text)

        if 1 < quarter < 5:
            marks = user_obj.get_quarters_marks(quarter)
            old_marks = user_obj.get_quarters_marks(quarter - 1)

            text = tables.quarter_marks_analytics(lessons, marks, old_marks)

            await wait_message.edit_text(text)


async def marks_analytic_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == user_id))
        user_obj = parser.WebUser(result.scalars().one_or_none(), session)
        wait_message = await callback_query.message.answer('Сбор информации...')
        num = await user_obj.get_current_quarter()
        lesson = user_obj.get_lessons()[int(callback_query.data.split('_')[1])]
        marks = multiprocesshelp.Multiprocess(user_obj).get_all_marks(num, lesson)
        text = tables.lessons_marks_table(marks, lesson)
        await wait_message.edit_text(text)
    # await core_bot.send_message(user_id, str(time.time() - timer))
