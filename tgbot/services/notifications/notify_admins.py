import logging

from aiogram import Dispatcher
from environs import Env

env = Env()
env.read_env()
bot_admins = env.list("ADMINS")


async def on_startup_notify(dp: Dispatcher):
    for admin in bot_admins:
        try:
            await dp.bot.send_message(admin, "Сообщение для администрации:\n"
                                             "<b>Бот запущен!</b> /start")

        except Exception as err:
            logging.exception(err)
