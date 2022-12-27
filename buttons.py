from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType

not_login = '🔑 Войти'
cancel = '❌ Отмена'

def main_menu():
	keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
	b1 = KeyboardButton('Мое имя')
	keyboard.add(b1)
	return keyboard