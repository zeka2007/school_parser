from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_states.states import SetAdminLevel
from bothelp.db import session_maker, Student


async def set_admin_level(message: types.Message, state: FSMContext):
    await state.set_state(SetAdminLevel.get_id)
    await message.answer('Введите id пользователя; /cancel - для отмены')


async def set_admin_level_get_id(message: types.Message, state: FSMContext):
    async with session_maker() as session:
        if message.text == '/cancel':
            await state.set_state()
            await message.answer('Отменено')
            return

        if not message.text.isnumeric():
            await state.set_state(SetAdminLevel.get_id)
            return message.answer('Введите правильный Telegram id!')
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == int(message.text)))
        student: Student = result.scalars().one_or_none()

        if student is None:
            await state.set_state()
            return await message.answer('Нет такого пользователя')
        await state.set_state(SetAdminLevel.get_level)
        await state.set_data({'user_id': student.user_id})
        await message.answer('Укажите уровень или введите 0 для снятия административных прав:')


async def set_admin_level_get_login(message: types.Message, state: FSMContext):
    async with session_maker() as session:
        if message.text == '/cancel':
            await state.set_state()
            await message.answer('Отменено')
            return

        if not message.text.isnumeric():
            await state.set_state(SetAdminLevel.get_level)
            return message.answer('Введите целое положительное число!')
        session: AsyncSession
        data = await state.get_data()
        user_id: int = data.get('user_id')
        await session.execute(update(Student).where(Student.user_id == user_id).values(
            admin_level=int(message.text)
        ))
        await session.commit()

        await state.set_state()

        text_rec = f'{message.from_user.username} выдал вам права администратора {message.text} уровня.\n' \
                   f'Просмотр доступных команд - /ahelp'
        text_sender = 'Вы успешно выдали админ права'

        if int(message.text) == 0:
            text_rec = f'{message.from_user.username} отобрал у вас права администратора'
            text_sender = 'Вы успешно отобрали права администратора'
        await message.bot.send_message(user_id, text_rec)

        await message.answer(text_sender)
