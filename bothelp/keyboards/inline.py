from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp import parser
from bothelp.db import session_maker, Student


def quarter_inline_menu():
    builder = InlineKeyboardBuilder()
    [builder.button(text=f'{x-1} и {x}', callback_data=f'quarter{x}') for x in range(2, 5)]

    builder.row(
        InlineKeyboardButton
        (
            text='За все четверти',
            callback_data='quarter5'
        )
    )
    builder.adjust(3)

    return builder.as_markup()


async def lessons_inline_menu(user_id: int, tag: str = 'lesson'):
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == user_id))
        par = parser.WebUser(result.scalars().one_or_none(), session)
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


def save_data_inline_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text='Сохранить данные',
        callback_data='confirm_data_save'
    ))
    builder.row(InlineKeyboardButton(
        text='Не сохранять данные',
        callback_data='denied_data_save'
    ))

    return builder.as_markup()
