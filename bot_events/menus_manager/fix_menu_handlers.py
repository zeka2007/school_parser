from aiogram import types
from aiogram.fsm.context import FSMContext

from aiogram_states.states import IfGetMarks
from bothelp import parser, tables, multiprocesshelp
from bothelp.keyboards import inline, reply, get_button_text


async def marks_fix_handler(message: types.message):
    user_id = message.from_user.id

    await message.answer('Выберите предмет',
                         reply_markup=inline.lessons_inline_menu(user_id, tag='fix'))


async def if_get_handler(message: types.message):
    user_id = message.from_user.id
    await message.answer('Выберите предмет',
                         reply_markup=inline.lessons_inline_menu(user_id, tag='if'))


async def marks_fix_callback(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    user_obj = parser.WebUser(user_id)
    await callback_query.message.answer('Сбор информации...')
    num = user_obj.get_current_quarter()
    lesson = user_obj.get_lessons()[int(callback_query.data.split('_')[1])]
    marks = multiprocesshelp.Multiprocess(user_id).get_all_marks(num, lesson)
    text = tables.lessons_marks_fix_table(marks, lesson)
    await callback_query.message.answer(text)


async def if_get_callback(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    user_obj = parser.WebUser(user_id)
    await callback_query.message.answer('Сбор информации...')
    num = user_obj.get_current_quarter()
    lesson = user_obj.get_lessons()[int(callback_query.data.split('_')[1])]
    marks = multiprocesshelp.Multiprocess(user_id).get_all_marks(num, lesson)
    text = tables.lessons_if_get_mark_table(marks, lesson)
    await state.set_data(marks)
    await state.set_state(IfGetMarks.state)
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
                return await message.answer('Введите число не больше 10')

        else:
            return await message.answer('Введите число, а не строку')

    text = tables.lessons_marks_table(user_marks)
    await message.answer(text)
    await state.set_state(IfGetMarks.state)
