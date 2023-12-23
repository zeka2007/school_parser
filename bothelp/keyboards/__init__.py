from aiogram.types import ReplyKeyboardMarkup


def get_button_text(menu: ReplyKeyboardMarkup, btn_index: int = 0):
    return menu.keyboard[btn_index][0].text
