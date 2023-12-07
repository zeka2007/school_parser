from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from tgmenu.button import Button


class Directory:
    def __init__(self, name: str):
        self.name = name
        self.buttons = []

    def add_button(self, btn: Button):
        btn.directory = self
        self.buttons.append(btn)

    def get_keyboard(self):
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        for btn in self.buttons:
            keyboard.add(KeyboardButton(btn.text))
        return keyboard
