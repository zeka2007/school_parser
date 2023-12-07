import aiogram.dispatcher

import tgmenu.directory, tgmenu.button_types
from aiogram.types import ContentType, message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


class Menu:
    def __init__(self, dp: aiogram.dispatcher):
        self.dispatcher = dp
        self.directories = []
        self.button_pressed_fun = None
        self.directory_select_fun = None
        self.default_buttons = None

        @self.dispatcher.message_handler(content_types=ContentType.TEXT, state=None)
        async def menu_handler(msg: message):

            for directory in self.directories:
                for btn in directory.buttons:
                    if btn.text == msg.text:
                        if btn.btn_type == tgmenu.button_types.btn_default:
                            if self.button_pressed_fun:
                                await self.button_pressed_fun(msg.from_user, btn)
                        if btn.btn_type == tgmenu.button_types.btn_directory:
                            if self.directory_select_fun:
                                await self.directory_select_fun(msg.from_user, btn.target_directory)

    def button_pressed(self, fun):
        self.button_pressed_fun = fun

    def directory_select(self, fun):
        self.directory_select_fun = fun

    def add_directory(self, directory: tgmenu.directory.Directory):
        self.directories.append(directory)
        if not self.default_buttons:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for btn in self.directories[0].buttons:
                keyboard.add(KeyboardButton(btn.text))
            self.default_buttons = keyboard

