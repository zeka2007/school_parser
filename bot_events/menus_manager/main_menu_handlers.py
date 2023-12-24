from aiogram import types

from bothelp.keyboards import reply


async def main_menu_handler(message: types.Message):
    await message.answer('Выберите категорию:',
                         reply_markup=reply.main_menu())


async def analytics_menu_handler(message: types.Message):
    await message.answer('Выберите категорию:',
                         reply_markup=reply.analytics_menu())


async def fix_menu_handler(message: types.Message):
    await message.answer('Выберите категорию:',
                         reply_markup=reply.fix_menu())
