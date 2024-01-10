from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp.db import session_maker, Student

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

    builder.add(KeyboardButton(text='🛎️ Уведомления'))
    builder.add(KeyboardButton(text='⚙️ вид'))
    builder.row(KeyboardButton(text='🔄 Обновить данные'))
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
