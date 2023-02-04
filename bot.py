import logging
import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import bot_sql
import buttons
import parser
import tables

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=MemoryStorage())

mysql = bot_sql.MySQL()
parser = parser.Parser()


class LoginState(StatesGroup):
    S1 = State()
    S2 = State()


@dp.callback_query_handler(text_contains='quarter')
async def process_callback_button_(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    quarter = int(callback_query.data[-1])
    await bot.send_message(callback_query.from_user.id,
                           'Получение информации...')
    marks = parser.get_quarters_marks(callback_query.from_user.id,
                                      quarter)
    old_marks = None
    if quarter > 1:
        old_marks = parser.get_quarters_marks(callback_query.from_user.id,
                                              quarter - 1)
    lessons = parser.get_lessons(callback_query.from_user.id)
    text = tables.quarter_marks_analytics(lessons, marks, old_marks)

    await bot.send_message(callback_query.from_user.id,
                           text)


@dp.callback_query_handler(text_contains='lesson')
async def process_callback_button_lessons(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    await bot.send_message(user_id, 'Сбор информации...')
    num = parser.get_current_quarter(user_id)
    lesson = parser.get_lessons(user_id)[int(callback_query.data.split('_')[1])]
    marks = parser.get_all_marks(user_id, num, lesson)
    text = tables.lessons_marks_table(marks, lesson)
    await bot.send_message(user_id, text)


@dp.callback_query_handler(text_contains='fix')
async def process_callback_button_lessons(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    await bot.send_message(user_id, 'Сбор информации...')
    num = parser.get_current_quarter(user_id)
    lesson = parser.get_lessons(user_id)[int(callback_query.data.split('_')[1])]
    marks = parser.get_all_marks(user_id, num, lesson)
    text = tables.lessons_marks_fix_table(marks, lesson)
    await bot.send_message(user_id, text)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    user_name = types.User.get_current().username
    user_id = types.User.get_current().id

    if not mysql.is_user_exist(user_id):
        mysql.add_new_user(user_id)
        b1 = KeyboardButton(buttons.not_login)
        keyboard.add(b1)
    else:
        data = mysql.get_login_data(user_id)
        if parser.login(user_id, data['login'], data['password']):
            keyboard = buttons.main_menu()
        else:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            b1 = KeyboardButton(buttons.not_login)
            keyboard.add(b1)
    await message.answer(
        f"Привет, {user_name}! Меня зовут Daikath "
        "и я помогу тебе с работой в электронном дневнике.",
        reply_markup=keyboard)


@dp.message_handler(commands=['exit'])
async def exit_from_system(message: types.Message):
    user_id = types.User.get_current().id

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(buttons.not_login)
    keyboard.add(b1)
    mysql.delete_user(user_id)

    await message.answer('Вы были отключены от системы',
                         reply_markup=keyboard)


@dp.message_handler(content_types=ContentType.TEXT, state=None)
async def buttons_handler(message: types.Message):
    if message.text == buttons.not_login:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        b1 = KeyboardButton(buttons.cancel)
        keyboard.add(b1)
        await message.answer('Введите свой логин', reply_markup=keyboard)
        await LoginState.S1.set()

    a_menu = buttons.analytics_menu_buttons

    if message.text == buttons.main_menu_buttons[0]:
        await message.answer('Выберите категорию:',
                             reply_markup=buttons.analytics_menu())

    if message.text == buttons.main_menu_buttons[1]:
        await message.answer('Выберите категорию:',
                             reply_markup=buttons.fix_menu())

    if message.text == a_menu[0]:
        await message.answer('Выберите четверть',
                             reply_markup=buttons.quarter_inline_buttons())

    if message.text == a_menu[1]:
        user_id = types.User.get_current().id
        # parser.get_all_marks(user_id, 3)
        await message.answer('Выберите предмет',
                             reply_markup=buttons.lessons_inline_buttons(user_id))

    if message.text == buttons.fix_menu_buttons[0]:
        user_id = types.User.get_current().id

        await message.answer('Выберите предмет',
                             reply_markup=buttons.lessons_inline_buttons(user_id, tag='fix'))

    if message.text == a_menu[len(a_menu) - 1]:
        await message.answer('Выберите категорию',
                             reply_markup=buttons.main_menu())


@dp.message_handler(state=LoginState.S1)
async def login_1(message: types.Message, state: FSMContext):
    if message.text == buttons.cancel:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        user_id = types.User.get_current().id
        await state.finish()
        if not mysql.is_user_exist(user_id):
            mysql.add_new_user(user_id)
            b1 = KeyboardButton(buttons.not_login)
            keyboard.add(b1)
        else:
            data = mysql.get_login_data(user_id)
            if parser.login(user_id, data['login'], data['password']):
                keyboard = buttons.main_menu()
            else:
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
                b1 = KeyboardButton(buttons.not_login)
                keyboard.add(b1)
        await message.answer(
            'Отменено',
            reply_markup=keyboard)
        return

    user_id = types.User.get_current().id
    if not mysql.is_user_exist(user_id):
        mysql.add_new_user(user_id)
    await state.update_data(login=message.text)
    await message.answer('Теперь введите пароль')
    await LoginState.S2.set()


@dp.message_handler(state=LoginState.S2)
async def login_2(message: types.Message, state: FSMContext):
    user_id = types.User.get_current().id
    if message.text == buttons.cancel:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        user_id = types.User.get_current().id
        await state.finish()
        if not mysql.is_user_exist(user_id):
            mysql.add_new_user(user_id)
            b1 = KeyboardButton(buttons.not_login)
            keyboard.add(b1)
        else:
            data = mysql.get_login_data(user_id)
            if parser.login(user_id, data['login'], data['password']):
                keyboard = buttons.main_menu()
            else:
                keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
                b1 = KeyboardButton(buttons.not_login)
                keyboard.add(b1)
        await message.answer(
            'Отменено',
            reply_markup=keyboard)
        return
    user_id = types.User.get_current().id
    await message.answer('Попытка авторизации...')
    data = await state.get_data()
    login = data.get("login")
    is_login = parser.login(user_id, login, message.text)
    if is_login:
        user_id = types.User.get_current().id
        await state.finish()
        mysql.set_login_data(
            user_id,
            {
                'login': login,
                'password': message.text,
                'csrf_token': None,
                'session_id': None
            }
        )
        await message.answer(
            'Вы успешно авторизовались',
            reply_markup=buttons.main_menu())
        student_id = parser.get_id(user_id)
        mysql.set_id(user_id, student_id)
    else:
        await message.answer('Ошибка авторизации. Повторите попытку.')
        await message.answer('Введите свой логин')
        await LoginState.S1.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
