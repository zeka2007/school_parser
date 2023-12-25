__all__ = ['register_user_commands']

from aiogram import Router, F

from aiogram_states.states import LoginState, SetAlarmLessons, IfGetMarks
from bot_events.base_commands import send_welcome, exit_from_system, test_cmd
from bot_events.login import login_menu, login_1, login_2, confirm_data_save, denied_data_save
from bot_events.menus_manager.main_menu_handlers import main_menu_handler, analytics_menu_handler, fix_menu_handler
from bot_events.menus_manager.main_settings_menu_handlers import settings_menu_handler
from bot_events.menus_manager.notification_small_menu import notifications_menu_handler, \
    set_notification_on, \
    set_notification_off
from bot_events.menus_manager.notification_large_menu import alarm_settings_menu_handler, \
    set_alarm_lessons_handler, \
    set_alarm_lessons
from bot_events.menus_manager.analytic_menu_handlers import quarter_analytic_handler, \
    marks_analytic_handler, \
    marks_analytic_callback, \
    quarter_analytic_callback
from bot_events.menus_manager.fix_menu_handlers import marks_fix_handler, \
    if_get_handler, \
    marks_fix_callback, \
    if_get_callback, \
    if_get_marks_state

from bothelp.keyboards import reply, get_button_text
from bothelp.parser import LoginCheckMiddleware
from aiogram.filters import Command, CommandStart


def register_user_commands(router: Router) -> None:

    router.message.middleware(LoginCheckMiddleware())

    router.message.register(test_cmd, Command(commands=['test']), flags={'chat_action': 'WebService'})
    # Base commands
    router.message.register(send_welcome, CommandStart())
    router.message.register(exit_from_system, Command(commands=['exit']))

    # Login functions
    router.message.register(login_menu, F.text == get_button_text(reply.not_login))
    router.message.register(login_1, LoginState.waiting_for_login)
    router.message.register(login_2, LoginState.waiting_for_password)

    router.callback_query.register(confirm_data_save, F.data == 'confirm_data_save')
    router.callback_query.register(denied_data_save, F.data == 'denied_data_save')

    # Menu buttons handlers
    router.message.register(main_menu_handler, F.text == reply.back_button_text)  # Back button
    router.message.register(analytics_menu_handler, F.text == get_button_text(reply.main_menu()))
    router.message.register(fix_menu_handler, F.text == get_button_text(reply.main_menu(), 1))

    # Main settings menu handlers
    router.message.register(settings_menu_handler, F.text == get_button_text(reply.main_menu(), 2))
    router.message.register(settings_menu_handler, F.text == reply.go_to_settings)
    router.message.register(settings_menu_handler, F.text == get_button_text(reply.setting_menu(), 1))

    # Notification small menu handlers
    router.message.register(notifications_menu_handler, F.text == get_button_text(reply.setting_menu()))
    router.message.register(notifications_menu_handler, F.text == get_button_text(reply.alarm_setting_menu(), -1))

    router.message.register(set_notification_on, F.text == reply.alarm_on)
    router.message.register(set_notification_off, F.text == reply.alarm_off)

    # Notification large menu handlers
    router.message.register(alarm_settings_menu_handler, F.text == reply.alarm_settings)
    router.message.register(set_alarm_lessons_handler, F.text == get_button_text(reply.alarm_setting_menu()))
    router.message.register(set_alarm_lessons, SetAlarmLessons.alarm)

    # Analytic menu handlers
    router.message.register(quarter_analytic_handler,
                            F.text == get_button_text(reply.analytics_menu()))
    router.message.register(marks_analytic_handler,
                            F.text == get_button_text(reply.analytics_menu(), 1))

    router.callback_query.register(quarter_analytic_callback, F.data.startswith('quarter'),
                                   flags={'chat_action': 'WebService'})
    router.callback_query.register(marks_analytic_callback, F.data.startswith('lesson'),
                                   flags={'chat_action': 'WebService'})

    # Fix menu handlers
    router.message.register(marks_fix_handler, F.text == get_button_text(reply.fix_menu()))
    router.message.register(if_get_handler, F.text == get_button_text(reply.fix_menu(), 1))

    router.callback_query.register(marks_fix_callback, F.data.startswith('fix'),
                                   flags={'chat_action': 'WebService'})
    router.callback_query.register(if_get_callback, F.data.startswith('if'),
                                   flags={'chat_action': 'WebService'})

    router.message.register(if_get_marks_state, IfGetMarks.state)
