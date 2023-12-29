from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func
from sqlalchemy.sql import text as txt

import config
from bothelp.db import session_maker, Student, Message
from bothelp.keyboards import inline


class SendMessageState(StatesGroup):
    get_additional_info = State()
    get_text = State()
    get_picture = State()


async def send_notify_command(message: types.Message):
    await message.answer('Выберите получателей:', reply_markup=inline.message_recip_menu())


async def send_notify_method(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    method = int(callback.data.split('_')[-1])
    await state.set_data({'method': method})
    if method in [5, 6, 7, 8]:
        if method == 5:
            await callback.message.answer('Введите уровни, которые получат сообщения,'
                                          'разделяя их пробелом\n'
                                          'Пример: 1 2 3\n\n'
                                          'Введите -1, чтобы отправить разработчикам\n'
                                          'Введите *, чтобы отправить всем администраторам')
        if method == 6:
            await callback.message.answer('Введите домены учреждений 3-его уровня, '
                                          'разделяя их пробелом\n'
                                          'Пример: 209minsk gymn7')
        if method in [7, 8]:
            await callback.message.answer('Введите ids, разделяя их пробелом')
        await state.set_state(SendMessageState.get_additional_info)
    else:
        await callback.message.answer('Введите текст сообщения:')
        await state.set_state(SendMessageState.get_text)


async def get_notify_additional_info(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.set_data({
        'method': int(data.get('method')),
        'add_info': message.text.split()
    })
    await message.answer('Введите текст сообщения:')
    await state.set_state(SendMessageState.get_text)


async def get_notify_text(message: types.Message, state: FSMContext):
    data = await state.get_data()

    bot_message = await message.answer('Отправьте изображение, '
                                       'которое будет находиться над текстом.\n'
                                       'Чтобы пропустить этот шаг, нажмите на кнопку ниже',
                                       reply_markup=inline.skip_photo_pic_btn)
    await state.set_data({
        'method': int(data.get('method')),
        'add_info': data.get('add_info'),
        'text': message.text,
        'skip_message_id': bot_message.message_id
    })
    await state.set_state(SendMessageState.get_picture)


async def get_count(data:dict) -> int:
    async with session_maker() as session:
        method = int(data.get('method'))
        result: int = 0

        if method == 1:
            result = await session.scalar(
                select(func.count())
                .select_from(Student)
                .where(Student.session_id is not None)
                .where(Student.csrf_token is not None)
            )
        elif method == 2:
            result = await session.scalar(
                select(func.count())
                .select_from(Student)
                .where(Student.session_id is None)
                .where(Student.csrf_token is None)
            )
        elif method == 3:
            result = await session.scalar(
                select(func.count())
                .select_from(Student)
                .where(Student.login is not None)
                .where(Student.password is not None)
            )
        elif method == 4:
            result = await session.scalar(
                select(func.count())
                .select_from(Student)
                .where(Student.login is None)
                .where(Student.password is None)
            )
        elif method == 5:
            count = 0
            for i in data.get('add_info'):
                print(i)
                query = f"SELECT count(*) FROM public.{Student.__tablename__} WHERE "
                for d in config.developers:
                    query += f"user_id <> {int(d)}"
                    query += " AND "
                query += f"admin_level = {i}"
                result = await session.scalar(txt(query))
                count += result
            result = count

        elif method == 6:
            for prefix in data.get('add_info'):
                result += await session.scalar(
                    select(func.count())
                    .select_from(Student)
                    .where(Student.site_prefix == prefix)
                )

        elif method == 7:
            for id_ent in data.get('add_info'):
                result += await session.scalar(
                    select(func.count())
                    .select_from(Student)
                    .where(Student.user_id == int(id_ent))
                )
        elif method == 8:
            for id_ent in data.get('add_info'):
                result += await session.scalar(
                    select(func.count())
                    .select_from(Student)
                    .where(Student.student_id == int(id_ent))
                )
        elif method == 9:
            result = await session.scalar(
                select(func.count())
                .select_from(Student)
            )
        return result


async def skip_photo_pic(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()

    result = await get_count(data)

    await state.set_state()
    text = f'{data.get("text")}\n\n' \
           f'Сообщение будет отправлено **{result}** пользователям.'
    await callback.message.edit_text(
        text,
        reply_markup=inline.send_message_dialog()
    )


async def get_notify_picture(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.bot.edit_message_text(
        'Отправьте изображение, '
        'которое будет находиться над текстом.',
        message.chat.id,
        int(data.get('skip_message_id'))
    )
    result = await get_count(data)
    text = f'{data.get("text")}\n\n' \
           f'Сообщение будет отправлено **{result}** пользователям.'
    await message.answer_photo(message.photo[0].file_id,
                               text,
                               reply_markup=inline.send_message_dialog())

    await state.set_data({
        'method': int(data.get('method')),
        'add_info': data.get('add_info'),
        'text': data.get('text'),
        'image_id': message.photo[0].file_id
    })

    await state.set_state()


async def send_notify_action(callback: types.CallbackQuery, state: FSMContext):
    answer = callback.data.split('_')[-1]
    data = await state.get_data()
    if answer == 'confirm':
        await callback.answer()
        await callback.message.edit_reply_markup()
        async with session_maker() as session:
            result = []
            method = int(data.get('method'))
            if method == 1:
                exe = await session.execute(
                    select(Student.user_id)
                    .where(Student.session_id is not None)
                    .where(Student.csrf_token is not None)
                )
                result = exe.scalars().fetchall()
            elif method == 2:
                exe = await session.execute(
                    select(Student.user_id)
                    .where(Student.session_id is None)
                    .where(Student.csrf_token is None)
                )
                result = exe.scalars().fetchall()
            elif method == 3:
                exe = await session.execute(
                    select(Student.user_id)
                    .where(Student.login is not None)
                    .where(Student.password is not None)
                )
                result = exe.scalars().fetchall()
            elif method == 4:
                exe = await session.execute(
                    select(Student.user_id)
                    .where(Student.login is None)
                    .where(Student.password is None)
                )
                result = exe.scalars().fetchall()

            elif method == 5:
                for i in data.get('add_info'):
                    print(i)
                    query = f"SELECT user_id FROM public.{Student.__tablename__} WHERE "
                    for d in config.developers:
                        query += f"user_id <> {int(d)}"
                        query += " AND "
                    query += f"admin_level = {i}"
                    exe = await session.execute(txt(query))
                    result += exe.scalars().fetchall()

            elif method == 6:
                for prefix in data.get('add_info'):
                    exe = await session.execute(
                        select(Student.user_id)
                        .where(Student.site_prefix == prefix)
                    )
                    result += exe.scalars().fetchall()

            elif method == 7:
                for id_ent in data.get('add_info'):
                    exe = await session.execute(
                        select(Student.user_id)
                        .where(Student.user_id == int(id_ent))
                    )
                    result += exe.scalars().fetchall()

            elif method == 8:
                for id_ent in data.get('add_info'):
                    exe = await session.execute(
                        select(Student.user_id)
                        .where(Student.student_id == int(id_ent))
                    )
                    result += exe.scalars().fetchall()

            elif method == 9:
                exe = await session.execute(
                    select(Student.user_id)
                )
                result = exe.scalars().fetchall()

            print(result)
            messages_ids = []

            if 'image_id' not in data:
                for user_id in result:
                    msg = await callback.bot.send_message(user_id, data.get('text'))
                    messages_ids.append(msg.message_id)

            else:

                for user_id in result:
                    msg = await callback.bot.send_photo(chat_id=user_id,
                                                        photo=data.get('image_id'),
                                                        caption=data.get('text'))
                    messages_ids.append(msg.message_id)
            msg_and_rec = []
            for i in range(len(result)):
                msg_and_rec.append([result[i], messages_ids[i]])
            session.add(
                Message(
                    text=data.get('text'),
                    from_user_id=callback.from_user.id,
                    image_id=data.get('image_id'),
                    message_and_recipient_ids=msg_and_rec
                )
            )
            await session.commit()
        await callback.message.answer('Сообщения отправлены!')
    elif answer == 'cancel':
        await callback.message.delete()
        await callback.answer('Отменено')
    await state.clear()
