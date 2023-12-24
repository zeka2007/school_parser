from aiogram import types
from aiogram.fsm.context import FSMContext

from aiogram_states.states import SetAlarmLessons
from bothelp import parser, tables, bot_sql
from bothelp.keyboards import reply, get_button_text


async def alarm_settings_menu_handler(message: types.Message):
    await message.answer('Параметры уведомлений:',
                         reply_markup=reply.alarm_setting_menu())


async def set_alarm_lessons_handler(message: types.Message, state: FSMContext):
    lessons = parser.WebUser(message.from_user.id).get_lessons()
    text = tables.set_alarm_lessons(lessons)
    await message.answer(text,
                         reply_markup=reply.cancel)
    await state.set_state(SetAlarmLessons.alarm)


async def set_alarm_lessons(message: types.Message, state: FSMContext):
    database = bot_sql.MySQL(message.from_user.id)

    if message.text == get_button_text(reply.cancel):
        await message.answer('Завершено', reply_markup=reply.alarm_setting_menu())
        await state.set_state()
        return

    if message.text == "*":
        database.set_alarm_lessons([])
        await state.set_state()
        return await message.answer('Уведомления настроены для всех уроков.', reply_markup=reply.alarm_setting_menu())
    text = message.text.split(' ')
    lessons = parser.WebUser(message.from_user.id).get_lessons()

    errors = 0
    text[:] = list(set(text))
    for chose in text:
        if chose.isnumeric():
            if not int(chose) <= len(lessons):
                errors += 1
        else:
            errors += 1
    if errors != 0:
        await message.answer('Вы допустили ошибку при заполнении. Попробуйте ещё раз.')
        return await state.set_state(SetAlarmLessons.alarm)

    lessons_list = []
    i = 1
    for lesson in lessons:
        for chose in text:
            if int(chose) == i:
                lessons_list.append(lesson)
        i += 1

    output = 'Уведомления настроены для уроков:\n'
    for item in lessons_list:
        output = output + item + '\n'

    database.set_alarm_lessons(lessons_list)

    await message.answer(output,
                         reply_markup=reply.alarm_setting_menu())
    await state.set_state()
