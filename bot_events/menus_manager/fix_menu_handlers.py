from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_states.states import IfGetMarks
from bothelp import parser, tables
from bothelp.db import session_maker, Student
from bothelp.keyboards import inline, reply, get_button_text


async def marks_fix_handler(message: types.Message):
    user_id = message.from_user.id

    await message.answer('Выберите предмет',
                         reply_markup=await inline.lessons_inline_menu(user_id, tag='fix'))


async def if_get_handler(message: types.Message):
    user_id = message.from_user.id
    await message.answer('Выберите предмет',
                         reply_markup=await inline.lessons_inline_menu(user_id, tag='if'))


async def marks_fix_callback(callback_query: types.CallbackQuery):
    async with session_maker() as session:
        session: AsyncSession
        await callback_query.answer()
        user_id = callback_query.from_user.id
        result = await session.execute(select(Student).where(Student.user_id == user_id))
        user_obj = parser.WebUser(result.scalars().one_or_none(), session)
        wait_message = await callback_query.message.answer('Сбор информации...')
        num = await user_obj.get_current_quarter()
        lesson = await user_obj.get_lessons()
        lesson = lesson[int(callback_query.data.split('_')[1])]
        marks = await user_obj.get_all_marks(num, lesson)
        text = tables.lessons_marks_fix_table(marks, lesson)
        await wait_message.edit_text(text)


async def if_get_callback(callback_query: types.CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        session: AsyncSession
        user_id = callback_query.from_user.id
        await callback_query.answer()
        result = await session.execute(select(Student).where(Student.user_id == user_id))
        user_obj = parser.WebUser(result.scalars().one_or_none(), session)
        wait_message = await callback_query.message.answer('Сбор информации...')
        num = await user_obj.get_current_quarter()
        lesson = await user_obj.get_lessons()
        lesson = lesson[int(callback_query.data.split('_')[1])]
        marks = await user_obj.get_all_marks(num, lesson)
        text = tables.lessons_if_get_mark_table(marks, lesson)
        await state.set_data(marks)
        await state.set_state(IfGetMarks.state)
        await wait_message.delete()
        await callback_query.message.answer(text, reply_markup=reply.cancel)


async def if_get_marks_state(message: types.Message, state: FSMContext):
    if message.text == get_button_text(reply.cancel):
        await message.answer('Завершено', reply_markup=reply.fix_menu())
        await state.set_state()
        return
    user_marks = []
    data = await state.get_data()
    user_marks.extend(data)
    for mark in message.text.split(' '):
        if mark.isdigit():
            if 10 >= int(mark) > 0:
                user_marks.append(int(mark))
            else:
                return await message.answer('Это число не может быть отметкой')

        else:
            return await message.answer('Введите число, а не строку')

    text = tables.lessons_marks_table(user_marks)
    await message.answer(text)
    await state.set_state(IfGetMarks.state)
