from aiogram.fsm.context import FSMContext

from aiogram_states.states import LoginState
from bothelp import bot_sql, parser
from bothelp.keyboards import reply, get_button_text
from aiogram import types


async def login_menu(message: types.Message, state: FSMContext):

    await message.answer('Введите свой логин', reply_markup=reply.cancel)
    await state.set_state(LoginState.waiting_for_login)


async def login_1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    database = bot_sql.MySQL(user_id)

    if message.text == get_button_text(reply.cancel):
        await state.set_state()
        if not database.is_user_exist():
            database.add_new_user()
            keyboard = reply.not_login
        else:
            data = database.get_login_data()
            if parser.login_user(user_id, data['login'], data['password']):
                keyboard = reply.main_menu
            else:
                keyboard = reply.not_login
        await message.answer(
            'Отменено',
            reply_markup=keyboard)
        return

    if not database.is_user_exist():
        database.add_new_user()
    await state.update_data(login=message.text)
    await message.answer('Теперь введите пароль')
    await state.set_state(LoginState.waiting_for_password)


async def login_2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    database = bot_sql.MySQL(user_id)
    if message.text == get_button_text(reply.cancel):
        await state.set_state()
        if not database.is_user_exist():
            database.add_new_user()
            keyboard = reply.not_login
        else:
            data = database.get_login_data()
            if parser.login_user(user_id, data['login'], data['password']):
                keyboard = reply.main_menu
            else:
                keyboard = reply.not_login

        await message.answer(
            'Отменено',
            reply_markup=keyboard)
        return
    await message.answer('Попытка авторизации...')
    data = await state.get_data()
    login = data.get("login")
    is_login = parser.login_user(user_id, login, message.text)
    if is_login:
        await state.set_state()
        database.set_login_data(
            {
                'login': login,
                'password': message.text,
                'csrf_token': None,
                'session_id': None
            }
        )
        await message.answer(
            'Вы успешно авторизовались',
            reply_markup=reply.main_menu())
    else:
        await message.answer('Ошибка авторизации. Повторите попытку.')
        await message.answer('Введите свой логин')
        await state.set_state(LoginState.waiting_for_login)
