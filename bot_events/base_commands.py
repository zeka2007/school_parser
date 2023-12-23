from aiogram import types
from aiogram.fsm.context import FSMContext

from bothelp import bot_sql, parser, file_manager
from bothelp.keyboards import reply


async def send_welcome(message: types.Message, state: FSMContext):
    user_name = message.from_user.username
    user_id = message.from_user.id
    database = bot_sql.MySQL(user_id)

    if not database.is_user_exist():
        database.add_new_user()
        keyboard = reply.not_login

    else:
        data = database.get_login_data()
        if parser.login_user(user_id, data['login'], data['password']):
            keyboard = reply.main_menu()
        else:
            keyboard = reply.not_login
    await state.set_state()
    await message.answer(
        f"Привет, {user_name}! ",
        reply_markup=keyboard)


async def exit_from_system(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    sql = bot_sql.MySQL(user_id)
    file_manager.UserData(sql.get_id()).remove_all_data()
    sql.delete_user()
    keyboard = reply.not_login

    await state.set_state()

    await message.answer('Вы были отключены от системы',
                         reply_markup=keyboard)
