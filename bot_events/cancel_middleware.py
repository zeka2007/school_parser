from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


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
