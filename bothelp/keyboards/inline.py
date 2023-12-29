from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp import parser
from bothelp.db import session_maker, Student


skip_photo_pic_btn = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Попустить',
                callback_data='skip_photo_pic'
            )
        ]
    ]
)


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


def get_user_method_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text='По Telegram id',
        callback_data='get_user_method_1'
    ))
    builder.row(InlineKeyboardButton(
        text='По Schools.by id',
        callback_data='get_user_method_2'
    ))
    return builder.as_markup()


def message_recip_menu():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text='Авторизованные',
        callback_data='user_type_1'
    ))
    builder.add(InlineKeyboardButton(
        text='Неавторизованные',
        callback_data='user_type_2'
    ))
    builder.row(InlineKeyboardButton(
        text='C паролем в БД',
        callback_data='user_type_3'
    ))
    builder.row(InlineKeyboardButton(
        text='Без пароля в БД',
        callback_data='user_type_4'
    ))
    builder.row(InlineKeyboardButton(
        text='Администраторы',
        callback_data='user_type_5'
    ))
    builder.row(InlineKeyboardButton(
        text='По домену сайта',
        callback_data='user_type_6'
    ))
    builder.row(InlineKeyboardButton(
        text='По Telegram ids',
        callback_data='user_type_7'
    ))
    builder.row(InlineKeyboardButton(
        text='По Schools.by ids',
        callback_data='user_type_8'
    ))
    builder.row(InlineKeyboardButton(
        text='Всем',
        callback_data='user_type_9'
    ))

    return builder.as_markup()


def send_message_dialog():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='Отправить',
            callback_data='notify_dialog_confirm'
        )
    )

    builder.row(
        InlineKeyboardButton(
            text='Отмена',
            callback_data='notify_dialog_cancel'
        )
    )

    return builder.as_markup()
