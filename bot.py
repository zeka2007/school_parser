import logging
import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bothelp import bot_sql, parser, tables, buttons, multiprocesshelp

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=MemoryStorage())

mysql = bot_sql.MySQL()

users_if_get_marks = {}


class LoginState(StatesGroup):
    S1 = State()
    S2 = State()


class IfGetMarks(StatesGroup):
    state = State()


class SetAlarmLessons(StatesGroup):
    alarm = State()


@dp.message_handler(commands=['test'])
async def test_fun(message: types.Message):
    await message.answer(parser.WebUser(message.from_user.id).get_id())


@dp.callback_query_handler(text_contains='quarter')
async def process_callback_button_(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    quarter = int(callback_query.data[-1])
    await bot.send_message(callback_query.from_user.id,
                           'Получение информации...')
    user_obj = parser.WebUser(callback_query.from_user.id)

    lessons = user_obj.get_lessons()
    if quarter == 5:
        marks_dict = {}
        for i in range(1, 5):
            marks_q = user_obj.get_quarters_marks(i)
            marks_dict[i] = marks_q
        text = tables.quarter_marks_analytics_all(lessons,
                                                  marks_dict)
        await bot.send_message(callback_query.from_user.id,
                               text)

    if 1 < quarter < 5:
        marks = user_obj.get_quarters_marks(quarter)
        old_marks = user_obj.get_quarters_marks(quarter - 1)

        text = tables.quarter_marks_analytics(lessons, marks, old_marks)

        await bot.send_message(callback_query.from_user.id,
                               text)


@dp.callback_query_handler(text_contains='lesson')
async def process_callback_button_lessons(callback_query: types.CallbackQuery):
    # timer = time.time()
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user_obj = parser.WebUser(user_id)
    await bot.send_message(user_id, 'Сбор информации...')
    num = user_obj.get_current_quarter()
    lesson = user_obj.get_lessons()[int(callback_query.data.split('_')[1])]
    marks = multiprocesshelp.Multiprocess(user_id).get_all_marks(num, lesson)
    text = tables.lessons_marks_table(marks, lesson)
    await bot.send_message(user_id, text)
    # await bot.send_message(user_id, str(time.time() - timer))


@dp.callback_query_handler(text_contains='fix')
async def process_callback_button_lessons(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user_obj = parser.WebUser(user_id)
    await bot.send_message(user_id, 'Сбор информации...')
    num = user_obj.get_current_quarter()
    lesson = user_obj.get_lessons()[int(callback_query.data.split('_')[1])]
    marks = multiprocesshelp.Multiprocess(user_id).get_all_marks(num, lesson)
    text = tables.lessons_marks_fix_table(marks, lesson)
    await bot.send_message(user_id, text)


@dp.callback_query_handler(text_contains='if')
async def process_callback_button_if(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    user_id = callback_query.from_user.id
    user_obj = parser.WebUser(user_id)
    await bot.send_message(user_id, 'Сбор информации...')
    num = user_obj.get_current_quarter()
    lesson = user_obj.get_lessons()[int(callback_query.data.split('_')[1])]
    marks = multiprocesshelp.Multiprocess(user_id).get_all_marks(num, lesson)
    text = tables.lessons_if_get_mark_table(marks, lesson)
    users_if_get_marks[user_id] = marks
    await IfGetMarks.state.set()
    await bot.send_message(user_id, text, reply_markup=buttons.cancel_menu())


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
        if parser.WebUser(user_id).login(data['login'], data['password']):
            keyboard = buttons.main_menu()
        else:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            b1 = KeyboardButton(buttons.not_login)
            keyboard.add(b1)
    me = await bot.get_me()
    await message.answer(
        f"Привет, {user_name}! Меня зовут {me.first_name} "
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

    if message.text == buttons.main_menu_buttons[2] \
            or message.text == buttons.go_to_settings \
            or message.text == buttons.setting_menu_buttons[1]:
        model = mysql.get_view_model(message.from_user.id)
        if message.text == buttons.setting_menu_buttons[1]:
            if model == 0:
                model = 1
            else:
                model = 0

            mysql.set_view_model(message.from_user.id,
                                 model)

        text = ''
        alarm_status = mysql.get_alarm_status(message.from_user.id)
        alarm_lessons = mysql.get_alarm_lessons(message.from_user.id)
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
            text = tables.setting_menu_table(
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
            text = tables.setting_menu_table(
                message.from_user.id,
                message.from_user.first_name,
                alarm_status,
                model,
                alarm_lessons=alarm_lessons_text
            )
        await message.answer(text,
                             reply_markup=buttons.setting_menu())

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

    if message.text == buttons.fix_menu_buttons[1]:
        user_id = types.User.get_current().id
        await message.answer('Выберите предмет',
                             reply_markup=buttons.lessons_inline_buttons(user_id, tag='if'))

    if message.text == buttons.setting_menu_buttons[0] \
            or message.text == buttons.alarm_setting_menu_buttons[len(buttons.alarm_setting_menu_buttons) - 1]:
        await message.answer('Параметры уведомлений:',
                             reply_markup=buttons.alarm_menu(message.from_user.id))

    if message.text == buttons.alarm_on:
        mysql.set_alarm_status(message.from_user.id,
                               True)
        await message.answer('Уведомления включены',
                             reply_markup=buttons.alarm_menu(message.from_user.id))

    if message.text == buttons.alarm_off:
        mysql.set_alarm_status(message.from_user.id,
                               False)
        await message.answer('Уведомления выключены',
                             reply_markup=buttons.alarm_menu(message.from_user.id))

    if message.text == buttons.alarm_settings:
        await message.answer('Параметры уведомлений:',
                             reply_markup=buttons.alarm_setting_menu())

    if message.text == buttons.alarm_setting_menu_buttons[0]:
        lessons = parser.WebUser(message.from_user.id).get_lessons()
        text = tables.set_alarm_lessons(lessons)
        await message.answer(text,
                             reply_markup=buttons.cancel_menu())
        await SetAlarmLessons.alarm.set()


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
            if parser.WebUser(user_id).login(data['login'], data['password']):
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
            if parser.WebUser(user_id).login(data['login'], data['password']):
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
    is_login = parser.WebUser(user_id).login(login, message.text)
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
        student_id = parser.WebUser(user_id).get_id()
        mysql.set_id(user_id, student_id)
    else:
        await message.answer('Ошибка авторизации. Повторите попытку.')
        await message.answer('Введите свой логин')
        await LoginState.S1.set()


@dp.message_handler(state=IfGetMarks.state)
async def if_get_mark_state(message: types.Message, state: FSMContext):
    if message.text == buttons.cancel:
        await message.answer('Заверешено', reply_markup=buttons.main_menu())
        await state.finish()
        return
    user_id = message.from_id
    user_marks = []
    user_marks.extend(users_if_get_marks[user_id])
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
    await IfGetMarks.state.set()


@dp.message_handler(state=SetAlarmLessons.alarm)
async def set_alarm_lessons(message: types.Message, state: FSMContext):
    if message.text == buttons.cancel:
        await message.answer('Заверешено', reply_markup=buttons.alarm_setting_menu())
        await state.finish()
        return

    if message.text == "*":
        mysql.set_alarm_lessons(message.from_user.id,
                                [])
        await state.finish()
        return await message.answer('Уведомления настроены для всех уроков.', reply_markup=buttons.alarm_setting_menu())
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
        return await SetAlarmLessons.alarm.set()

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

    mysql.set_alarm_lessons(message.from_user.id, lessons_list)

    await message.answer(output,
                         reply_markup=buttons.alarm_setting_menu())
    await state.finish()


async def send_notify(data):
    for send in data:
        await bot.send_message(int(send['user_id']),
                               f'Установлена отметка: {send["added_marks"]} по предмету {send["lesson"]}')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
