from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from bothelp import bot_sql

back_button_text = '⬅️ Назад'

go_to_settings = '⬅ В меню настроек'
alarm_on = '🛎️ Вкл. Уведомления'
alarm_off = '🛎️ Выкл. Уведомления'
alarm_settings = '👤 Настройка уведомлений'


not_login = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='🔑 Войти')]],
    resize_keyboard=True)
cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='❌ Отмена')]],
    resize_keyboard=True)


def main_menu():
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text='🔎 Анализ отметок'))
    builder.row(KeyboardButton(text='🧐 Советы по исправлению'))
    builder.row(KeyboardButton(text='👤 Настройки'))

    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard


def analytics_menu():
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text='📅 Анализ четвертных отметок'))
    builder.row(KeyboardButton(text='🧮 Средний балл'))
    builder.row(KeyboardButton(text=back_button_text))

    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard


def fix_menu():
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text='⁉️ Способы исправления отметки'))
    builder.row(KeyboardButton(text='☝️ Что будет если получить...'))
    builder.row(KeyboardButton(text=back_button_text))

    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard


def setting_menu():
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text='🛎️ Уведомления',))
    builder.row(KeyboardButton(text='⚙️ Изменить вид'))
    builder.row(KeyboardButton(text=back_button_text))

    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard


def alarm_setting_menu():
    builder = ReplyKeyboardBuilder()

    builder.row(KeyboardButton(text='☑️ Выбранные уроки'))
    builder.row(KeyboardButton(text='📅 Период проверки'))
    builder.row(KeyboardButton(text='⬅️ В меню уведомлений'))

    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True
    return keyboard


def alarm_menu(user_id: int):
    sql = bot_sql.MySQL(user_id)
    alarm_menu_buttons = [
        alarm_on,
        alarm_settings,
        go_to_settings
    ]
    if sql.get_alarm_status():
        alarm_menu_buttons = [
            alarm_off,
            alarm_settings,
            go_to_settings
        ]
    builder = ReplyKeyboardBuilder()
    for menu_item in alarm_menu_buttons:
        builder.row(KeyboardButton(text=menu_item))
    keyboard = builder.as_markup()
    keyboard.resize_keyboard = True

    return keyboard
