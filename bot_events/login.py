from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup
import aiogram.utils.markdown as md
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_states.states import LoginState
from bothelp import parser
from bothelp.db import session_maker, Student
from bothelp.keyboards import reply, get_button_text, inline
from aiogram import types


async def get_cancel_markup(user_id: int, session: AsyncSession) -> ReplyKeyboardMarkup:
    result = await session.execute(select(Student).where(Student.user_id == user_id))
    student: Student = result.scalars().one_or_none()

    if student is None:
        session.add(Student(user_id=user_id))
        await session.commit()
        keyboard = reply.not_login
    else:
        if await parser.login_user(student, session):
            keyboard = reply.main_menu()
        else:
            keyboard = reply.not_login

    return keyboard


async def login_menu(message: types.Message, state: FSMContext):

    await message.answer('Введите свой логин', reply_markup=reply.cancel)
    await state.set_state(LoginState.waiting_for_login)


async def login_1(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    async with session_maker() as session:
        session: AsyncSession

        if message.text == get_button_text(reply.cancel):
            await state.set_state()
            keyboard = await get_cancel_markup(user_id, session)
            await message.answer(
                'Отменено',
                reply_markup=keyboard)

        await state.set_data({'login': message.text})
        await message.answer('Теперь введите пароль')
        await state.set_state(LoginState.waiting_for_password)


async def login_2(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    async with session_maker() as session:
        session: AsyncSession
        if message.text == get_button_text(reply.cancel):
            await state.set_state()
            keyboard = await get_cancel_markup(user_id, session)
            await message.answer(
                'Отменено',
                reply_markup=keyboard)
            return

        await message.answer('Попытка авторизации...')
        data = await state.get_data()
        login = data.get("login")

        student = Student(
            user_id=user_id,
            login=login,
            password=message.text
        )

        is_login = await parser.login_user(student, session)
        if is_login:
            await state.set_state()
            # database.set_login_data(
            #     {
            #         'login': login,
            #         'password': message.text,
            #         'csrf_token': None,
            #         'session_id': None
            #     }
            # )
            await message.answer(
                'Вы успешно авторизовались',
                reply_markup=reply.main_menu())

            await message.answer(
                f'{md.bold("Сохранить данные для входа?")}\n'
                f'При авторизации в сервисе Schools.by создается {md.italic("токен")}, который '
                'позволяет запомнить пользователя и входить в аккаунт без запроса логина и пароля.\n'
                'Благодаря этому вы можете отказаться от сохранения ваших данных для авторизации в базу бота, '
                'ведь для получения информации будет использован токен, который не связан с вашим логином и паролем, '
                'Однако в случае устаревания токена бот снова потребует ваши данные',
                reply_markup=inline.save_data_inline_menu()
            )

            await state.update_data(
                {
                    'login': login,
                    'password': message.text
                }
            )
        else:
            await message.answer('Ошибка авторизации. Повторите попытку.')
            await message.answer('Введите свой логин')
            await state.set_state(LoginState.waiting_for_login)


async def confirm_data_save(callback_query: types.CallbackQuery, state: FSMContext):
    async with session_maker() as session:
        session: AsyncSession
        data = await state.get_data()
        await session.execute(update(Student).where(Student.user_id == callback_query.from_user.id).values(
            login=data['login'],
            password=data['password']
        ))
        await session.commit()
        await callback_query.answer('Данные сохранены')
        await callback_query.message.delete()


async def denied_data_save(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    await state.set_state()
    await callback_query.message.delete()
