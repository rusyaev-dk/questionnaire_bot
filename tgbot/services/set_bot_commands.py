from aiogram import types, Dispatcher
from aiogram.types import BotCommand

from tgbot.config import load_config


async def set_bot_commands(dp):
    default_commands = {
        "menu": "Главное меню",
        "cancel": "Отмена",
        "restart": "Перезапустить бота",
        "help": "Помощь"
    }

    admin_commands = {
        "statistics": "Статистика бота",
        "notify_users": "Уведомить пользователей",
        "menu": "Главное меню",
        "cancel": "Отмена",
        "restart": "Перезапустить бота",
        "help": "Помощь"
    }

    await dp.bot.set_my_commands(
        [BotCommand(name, value) for name, value in default_commands.items()],
        scope=types.BotCommandScopeDefault())

    await dp.bot.set_my_commands(
        [BotCommand(name, value) for name, value in admin_commands.items()],
        scope=types.BotCommandScopeChat(chat_id=load_config().tg_bot.admin_ids[0]))
