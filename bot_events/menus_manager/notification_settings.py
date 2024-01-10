from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from aiogram_states.states import SetAlarmLessons
from bothelp import parser, tables
from bothelp.db import session_maker, Student
from bothelp.keyboards import inline


async def back_to_notifications_menu(callback: types.CallbackQuery):
    await callback.message.edit_text('Параметры уведомлений:',
                                     reply_markup=inline.notification_settings_list_menu())


async def get_settings_menu_text(menu_type: str, student: Student):
    if menu_type == 'lessons':

        text = 'Настройка уведомлений о новых отметках\n\n' \
               'Статус: %s \n\n' % ("❌ Выключены" if not student.alarm_state else "✅ Включены")
        if student.alarm_state:
            text += f'Предметы: {", ".join(student.alarm_lessons)}'
        return text

    elif menu_type == 'updates':
        text = 'Настройка уведомлений об обновлениях\n\n' \
               'Статус: %s \n\n' % ("❌ Выключены" if not student.update_alarm_state else "✅ Включены")
        return text
    elif menu_type == 'newsletters':
        text = 'Настройка рассылок\n' \
               'Рассылки отправляются администраторами бота и могут содержать ' \
               'важную информации, поэтому отключайте их с осторожностью.\n\n' \
               'Статус: %s \n\n' % ("❌ Выключены" if not student.newsletters_alarm_state else "✅ Включены")
        return text


async def set_notification_menu(callback: types.CallbackQuery):
    menu_type = callback.data.split('_')[-1]
    await callback.answer()
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student)
                                       .where(Student.user_id == callback.from_user.id))
        student: Student = result.scalars().one()
        if menu_type == 'lessons':
            text = await get_settings_menu_text(menu_type, student)
            await callback.message.edit_text(
                text,
                reply_markup=inline.notifications_menu(
                    student.alarm_state,
                    menu_type
                )
            )
        elif menu_type == 'updates':
            text = await get_settings_menu_text(menu_type, student)
            await callback.message.edit_text(
                text,
                reply_markup=inline.notifications_menu(
                    student.update_alarm_state,
                    menu_type,
                    only_state=True
                )
            )
        elif menu_type == 'newsletters':
            text = await get_settings_menu_text(menu_type, student)
            await callback.message.edit_text(
                text,
                reply_markup=inline.notifications_menu(
                    student.newsletters_alarm_state,
                    menu_type,
                    only_state=True
                )
            )


async def set_notification_status(callback: types.CallbackQuery):
    notification_type = callback.data.split('_')[-2]
    status = callback.data.split('_')[-1]
    async with session_maker() as session:
        session: AsyncSession
        if status == 'on':
            alarm_state = True
        elif status == 'off':
            alarm_state = False
        if notification_type == 'lessons':
            await session.execute(
                update(Student)
                .where(Student.user_id == callback.from_user.id)
                .values(
                    alarm_state=alarm_state
                )
            )
            await session.commit()
            result = await session.execute(select(Student)
                                           .where(Student.user_id == callback.from_user.id))
            student: Student = result.scalars().one()
            text = await get_settings_menu_text(notification_type, student)
            await callback.message.edit_text(
                text,
                reply_markup=inline.notifications_menu(
                    alarm_state,
                    notification_type
                )
            )
        elif notification_type == 'updates':
            await session.execute(
                update(Student)
                .where(Student.user_id == callback.from_user.id)
                .values(
                    update_alarm_state=alarm_state
                )
            )
            await session.commit()
            result = await session.execute(select(Student)
                                           .where(Student.user_id == callback.from_user.id))
            student: Student = result.scalars().one()
            text = await get_settings_menu_text(notification_type, student)
            await callback.message.edit_text(
                text,
                reply_markup=inline.notifications_menu(
                    alarm_state,
                    notification_type,
                    only_state=True
                )
            )
        elif notification_type == 'newsletters':
            await session.execute(
                update(Student)
                .where(Student.user_id == callback.from_user.id)
                .values(
                    newsletters_alarm_state=alarm_state
                )
            )
            await session.commit()
            result = await session.execute(select(Student)
                                           .where(Student.user_id == callback.from_user.id))
            student: Student = result.scalars().one()
            text = await get_settings_menu_text(notification_type, student)
            await callback.message.edit_text(
                text,
                reply_markup=inline.notifications_menu(
                    alarm_state,
                    notification_type,
                    only_state=True
                )
            )


async def set_alarm_lessons_handler(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == callback.from_user.id))
        lessons = await parser.WebUser(result.scalars().one_or_none(), session).get_lessons()
        text = tables.set_alarm_lessons(lessons)
        await callback.message.answer(text)
        await state.set_state(SetAlarmLessons.alarm)


async def set_alarm_lessons(message: types.Message, state: FSMContext):
    async with session_maker() as session:
        session: AsyncSession
        result = await session.execute(select(Student).where(Student.user_id == message.from_user.id))
        student: Student = result.scalars().one_or_none()

        if message.text == "*":
            await session.execute(update(Student).where(Student.user_id == message.from_user.id).values(
                alarm_lessons=["*"]
            ))
            await session.commit()
            await state.set_state()
            return await message.answer('Уведомления настроены для всех уроков.')
        text = message.text.split(' ')
        lessons = await parser.WebUser(student, session).get_lessons()

        errors = 0
        text[:] = list(set(text))
        for chose in text:
            if chose.isnumeric():
                if not int(chose) <= len(lessons):
                    errors += 1
            else:
                errors += 1
        if errors != 0:
            await message.answer('Вы допустили ошибку при заполнении. Попробуйте ещё раз.')
            return await state.set_state(SetAlarmLessons.alarm)

        lessons_list = []
        i = 1
        for lesson in lessons:
            for chose in text:
                if int(chose) == i:
                    lessons_list.append(lesson)
            i += 1

        output = 'Уведомления настроены для уроков:\n'
        for item in lessons_list:
            output = output + item + '\n'

        await session.execute(update(Student).where(Student.user_id == message.from_user.id).values(
            alarm_lessons=lessons_list
        ))
        await session.commit()
        student.alarm_lessons = lessons_list
        text = await get_settings_menu_text('lessons', student)
        await message.answer(
            text,
            reply_markup=inline.notifications_menu(
                student.alarm_state,
                'lessons'
            )
        )
        await state.set_state()
