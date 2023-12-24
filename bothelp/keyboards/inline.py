from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bothelp import parser


def quarter_inline_menu():
    builder = InlineKeyboardBuilder()
    [builder.button(text=str(x), callback_data=f'quarter{x}') for x in range(1, 5)]

    builder.row(
        InlineKeyboardButton
        (
            text='За все четверти',
            callback_data='quarter5'
        )
    )
    builder.adjust(4)

    return builder.as_markup()


def lessons_inline_menu(user_id: int, tag: str = 'lesson'):
    par = parser.WebUser(user_id)
    lessons = par.get_lessons()
    counter = 0
    builder = InlineKeyboardBuilder()

    for lesson in lessons:
        inline_btn = InlineKeyboardButton(
            text=lesson,
            callback_data=f'{tag}_{counter}'
        )
        builder.add(inline_btn)
        counter = counter + 1
    builder.adjust(2)

    return builder.as_markup()
