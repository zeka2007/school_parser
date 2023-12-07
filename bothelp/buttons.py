from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from bothelp import bot_sql

from bothelp import parser

not_login = '🔑 Войти'
cancel = '❌ Отмена'
go_to_settings = '⬅ В меню настроек'
alarm_on = '🛎️ Вкл. Уведомления'
alarm_off = '🛎️ Выкл. Уведомления'
alarm_settings = '👤 Настройка уведомлений'

main_menu_buttons = [
    '🔎 Анализ отметок',
    '🧐 Советы по исправлению',
    '👤 Настройки',
]
analytics_menu_buttons = [
    '📅 Анализ четвертных отметок',
    '🧮 Средний балл',
    '⬅️ Назад'
]

fix_menu_buttons = [
    '⁉️ Способы исправления отметки',
    '☝️ Что будет если получить...',
    '⬅️ Назад'
]

setting_menu_buttons = [
        '🛎️ Уведомления',
        '⚙️ Изменить вид',
        '⬅️ Назад'
    ]

alarm_setting_menu_buttons = [
        '☑️ Выбранные уроки',
        '📅 Период проверки',
        '⬅️ В меню уведомлений'
    ]


def cancel_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button = KeyboardButton(cancel)
    keyboard.add(button)
    return keyboard


def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for menu_item in main_menu_buttons:
        b = KeyboardButton(menu_item)
        keyboard.add(b)
    return keyboard


def analytics_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for menu_item in analytics_menu_buttons:
        b = KeyboardButton(menu_item)
        keyboard.add(b)
    return keyboard


def fix_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for menu_item in fix_menu_buttons:
        b = KeyboardButton(menu_item)
        keyboard.add(b)
    return keyboard


def setting_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for menu_item in setting_menu_buttons:
        b = KeyboardButton(menu_item)
        keyboard.add(b)
    return keyboard


def alarm_setting_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for menu_item in alarm_setting_menu_buttons:
        b = KeyboardButton(menu_item)
        keyboard.add(b)
    return keyboard


def alarm_menu(user_id: int):
    sql = bot_sql.MySQL()
    alarm_menu_buttons = [
        alarm_on,
        alarm_settings,
        go_to_settings
    ]
    if sql.get_alarm_status(user_id):
        alarm_menu_buttons = [
            alarm_off,
            alarm_settings,
            go_to_settings
        ]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for menu_item in alarm_menu_buttons:
        b = KeyboardButton(menu_item)
        keyboard.add(b)
    return keyboard


def quarter_inline_buttons():
    inline_kb = InlineKeyboardMarkup(row_width=4)
    inline_btn1 = InlineKeyboardButton('1',
                                       callback_data='quarter1')
    inline_btn2 = InlineKeyboardButton('2',
                                       callback_data='quarter2')
    inline_btn3 = InlineKeyboardButton('3',
                                       callback_data='quarter3')
    inline_btn4 = InlineKeyboardButton('4',
                                       callback_data='quarter4')
    inline_btn5 = InlineKeyboardButton('За все четверти',
                                       callback_data='quarter5')
    inline_kb.add(inline_btn1, inline_btn2,
                  inline_btn3, inline_btn4, inline_btn5)

    return inline_kb


def lessons_inline_buttons(user_id: int, tag: str = 'lesson'):
    inline_kb = InlineKeyboardMarkup(row_width=2)
    par = parser.WebUser(user_id)
    lessons = par.get_lessons()
    counter = 0
    for lesson in lessons:
        inline_btn = InlineKeyboardButton(lesson,
                                          callback_data=f'{tag}_{counter}')
        inline_kb.insert(inline_btn)
        counter = counter + 1

    return inline_kb
