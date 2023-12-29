from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bothelp.db import session_maker, Student
from config import developers


class CheckAdminLevelMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        if get_flag(data, 'req_level') is None:
            return await handler(event, data)

        if event.from_user.id in developers:
            return await handler(event, data)

        if get_flag(data, 'req_level') < 0:
            return

        async with session_maker() as session:
            session: AsyncSession
            result = await session.execute(select(Student).where(Student.user_id == event.from_user.id))
            student: Student = result.scalars().one_or_none()

            if student is not None:
                if student.admin_level >= get_flag(data, 'req_level'):
                    return await handler(event, data)


class CancelStateMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        if get_flag(data, 'can_be_canceled') is None:
            return await handler(event, data)

        state: FSMContext = data.get('state')

        if get_flag(data, 'can_be_canceled'):
            if event.text == '/cancel':
                await state.set_state()
                await event.answer('Отменено')
                return
            else:
                return await handler(event, data)
