from aiogram import types

from bothelp import bot_sql, parser, tables
from bothelp.keyboards import reply, get_button_text


async def settings_menu_handler(message: types.Message):
    database = bot_sql.MySQL(message.from_user.id)
    model = database.get_view_model()
    if message.text == get_button_text(reply.setting_menu(), 1):
        if model == 0:
            model = 1
        else:
            model = 0

        database.set_view_model(model)

    alarm_status = database.get_alarm_status()
    alarm_lessons = database.get_alarm_lessons()
    alarm_lessons_text = ''
    i = 0
    for item in alarm_lessons:
        if i == len(alarm_lessons) - 1:
            alarm_lessons_text = alarm_lessons_text + item
        else:
            alarm_lessons_text = alarm_lessons_text + item + '\n'
        i += 1

    if alarm_lessons == '*':
        alarm_lessons_text = 'Все'

    if model != 0:
        data = parser.WebUser(message.from_user.id).get_student_info()
        result_text = tables.setting_menu_table(
            message.from_user.id,
            message.from_user.first_name,
            alarm_status,
            model,
            int(data['student_id']),
            data['student_name'],
            data['class'],
            data['birthday'],
            alarm_lessons_text
        )
    else:
        result_text = tables.setting_menu_table(
            message.from_user.id,
            message.from_user.first_name,
            alarm_status,
            model,
            alarm_lessons=alarm_lessons_text
        )
    await message.answer(result_text,
                         reply_markup=reply.setting_menu())
