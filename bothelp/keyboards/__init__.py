from aiogram.types import ReplyKeyboardMarkup


def get_button_text(menu: ReplyKeyboardMarkup,
                    btn_index: int = 0,
                    btn_index_2: int = 0):
    print(menu.keyboard)
    return menu.keyboard[btn_index][btn_index_2].text
