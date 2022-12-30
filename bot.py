import logging
import config
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import requests
from bs4 import BeautifulSoup
import bot_sql
import buttons
import parser

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


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):

	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

	user_name = types.User.get_current().username
	user_id = types.User.get_current().id

	if(not mysql.is_user_exist(user_id)):
		mysql.add_new_user(user_id)
		b1 = KeyboardButton(buttons.not_login)
		keyboard.add(b1)
	else:
		data = mysql.get_login_data(user_id)
		if parser.login(user_id, data['login'], data['password']):
		    keyboard=buttons.main_menu()
		else:
			keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
			b1 = KeyboardButton(buttons.not_login)
			keyboard.add(b1)
	await message.answer(
			f"Привет, {user_name}! Меня зовут Daikath "
			"и я помогу тебе с работой в электронном дневнике.",
			reply_markup=keyboard)


@dp.message_handler(commands=['exit'])
async def exit(message: types.Message):
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
	if message.text == 'Мое имя':
		user_id = types.User.get_current().id
		await message.answer(parser.get_name(user_id))

@dp.message_handler(state=LoginState.S1)
async def login_1(message: types.Message, state: FSMContext):
	if message.text == buttons.cancel:
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
		user_id = types.User.get_current().id
		await state.finish()
		if(not mysql.is_user_exist(user_id)):
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
		if(not mysql.is_user_exist(user_id)):
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
		keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
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
		if(not mysql.is_user_exist(user_id)):
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
		    	'Вы успешно авторизовались',
		    	reply_markup=keyboard)
	else:
		await message.answer('Ошибка авторизации. Повторите попытку.')
		await message.answer('Введите свой логин')
		await LoginState.S1.set()

	
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
