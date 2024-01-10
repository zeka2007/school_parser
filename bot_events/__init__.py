__all__ = ['register_user_commands', 'register_admin_commands']

from aiogram import Router, F

from aiogram_states.states import LoginState, SetAlarmLessons, IfGetMarks, AdminRequestId, SetAdminLevel
from bot_events.administration.base_commands import admin_help, admin_commands
from bot_events.administration.middleware import CheckAdminLevelMiddleware
from bot_events.administration.notifications import send_notify_method, get_notify_additional_info, get_notify_text, \
    SendMessageState, get_notify_picture, skip_photo_pic, send_notify_action
from bot_events.administration.user_view import get_user_info_state, get_user_info_method
from bot_events.administration.hight_level_commands import set_admin_level_get_id, set_admin_level_get_login
from bot_events.base_commands import send_welcome, exit_from_system, test_cmd
from bot_events.cancel_middleware import CancelStateMiddleware
from bot_events.login import login_menu, login_1, login_2, confirm_data_save, denied_data_save
from bot_events.menus_manager.main_menu_handlers import main_menu_handler, analytics_menu_handler, fix_menu_handler
from bot_events.menus_manager.main_settings_menu_handlers import settings_menu_handler, notifications_menu_handler, \
    update_all_data
from bot_events.menus_manager.notification_settings import set_notification_status, set_notification_menu, \
    back_to_notifications_menu, set_alarm_lessons_handler, set_alarm_lessons

from bot_events.menus_manager.analytic_menu_handlers import quarter_analytic_handler, \
    marks_analytic_handler, \
    marks_analytic_callback, \
    quarter_analytic_callback
from bot_events.menus_manager.fix_menu_handlers import marks_fix_handler, \
    if_get_handler, \
    marks_fix_callback, \
    if_get_callback, \
    if_get_marks_state

from bothelp.keyboards import reply, get_button_text, inline
from bothelp.parser import LoginCheckMiddleware
from aiogram.filters import Command, CommandStart


def register_user_commands(router: Router) -> None:
    router.message.middleware.register(LoginCheckMiddleware())
    router.callback_query.middleware.register(LoginCheckMiddleware())
    router.message.middleware.register(CancelStateMiddleware())

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
    router.message.register(settings_menu_handler, F.text == get_button_text(reply.setting_menu(), 0, 1))
    router.message.register(
        update_all_data,
        F.text == get_button_text(reply.setting_menu(), 1),
        flags={'chat_action': 'WebService'}
    )

    # Notification settings
    router.message.register(notifications_menu_handler, F.text == get_button_text(reply.setting_menu()))

    router.callback_query.register(back_to_notifications_menu, F.data == 'back_to_notif_settings')
    router.callback_query.register(set_alarm_lessons_handler, F.data == 'set_lessons_to_alarm')

    router.callback_query.register(set_notification_menu, F.data.startswith('notif_settings_type_'))
    router.callback_query.register(set_notification_status, F.data.startswith('set_notification_'))

    router.message.register(set_alarm_lessons,
                            SetAlarmLessons.alarm,
                            flags={'can_be_canceled': True})
    # Notification large menu handlers
    # router.message.register(set_alarm_lessons_handler, F.text == get_button_text(reply.alarm_setting_menu()))

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


def register_admin_commands(router: Router) -> None:
    # Middlewares register
    router.message.middleware.register(CheckAdminLevelMiddleware())
    router.callback_query.middleware.register(CheckAdminLevelMiddleware())

    # Text commands
    for command in admin_commands:
        router.message.register(
            command['func'],
            Command(command['command'].command),
            flags={'req_level': command['level']}
        )

    # Get user info
    router.message.register(get_user_info_state, AdminRequestId.state,
                            flags={'can_be_canceled': True})
    router.callback_query.register(get_user_info_method,
                                   F.data.startswith('get_user_method'),
                                   flags={'req_level': 1})

    # Set admin level
    router.message.register(set_admin_level_get_id, SetAdminLevel.get_id,
                            flags={'can_be_canceled': True})
    router.message.register(set_admin_level_get_login, SetAdminLevel.get_level,
                            flags={'can_be_canceled': True})

    # Send notifications
    router.callback_query.register(send_notify_method,
                                   F.data.startswith('user_type'),
                                   flags={'req_level': 3})
    router.message.register(get_notify_additional_info, SendMessageState.get_additional_info,
                            flags={
                                'req_level': 3,
                                'can_be_canceled': True
                            })

    router.message.register(get_notify_text, SendMessageState.get_text,
                            flags={
                                'req_level': 3,
                                'can_be_canceled': True
                            })
    router.callback_query.register(skip_photo_pic,
                                   F.data == inline.skip_photo_pic_btn.inline_keyboard[0][0].callback_data,
                                   SendMessageState.get_picture)
    router.message.register(get_notify_picture,
                            F.photo,
                            SendMessageState.get_picture,
                            flags={
                                'req_level': 3,
                                'can_be_canceled': True
                            })

    router.callback_query.register(send_notify_action,
                                   F.data.startswith('notify_dialog_'),
                                   flags={'req_level': 3})
