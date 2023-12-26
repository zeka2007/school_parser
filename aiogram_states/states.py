from aiogram.fsm.state import StatesGroup, State


class LoginState(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()


class IfGetMarks(StatesGroup):
    state = State()


class SetAlarmLessons(StatesGroup):
    alarm = State()


class AdminRequestId(StatesGroup):
    state = State()


class SetAdminLevel(StatesGroup):
    get_id = State()
    get_level = State()
