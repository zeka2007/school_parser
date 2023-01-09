from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ContentType, InlineKeyboardButton, InlineKeyboardMarkup

not_login = '🔑 Войти'
cancel = '❌ Отмена'

main_menu_buttons = [
    '🔎 Анализ отметок'
]
analytics_menu_buttons = [
    '📅 Анализ четвертных отметок',
    '⬅️ Назад'
]


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
    inline_kb.add(inline_btn1, inline_btn2,
                  inline_btn3, inline_btn4)

    return inline_kb
