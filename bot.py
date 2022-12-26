import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.handlers.echo import register_echo
from tgbot.handlers.users.process_bot_start import register_process_bot_start
from tgbot.handlers.users.process_fill_text_questionnaire import register_process_fill_text_questionnaire
from tgbot.handlers.users.process_main_menu import register_process_main_menu
from tgbot.handlers.users.process_create_text_questionnaire import register_process_questionnaire
from tgbot.middlewares.db import DbMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.services import set_bot_commands
from tgbot.services.database import db_gino
from tgbot.services.database.db_gino import db
from tgbot.services.notifications import notify_admins

logger = logging.getLogger(__name__)


def register_all_middlewares(dp):
    dp.setup_middleware(DbMiddleware())
    dp.setup_middleware(ThrottlingMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(AdminFilter)


def register_all_handlers(dp):

    register_process_bot_start(dp)
    register_process_main_menu(dp)
    register_process_questionnaire(dp)

    register_process_fill_text_questionnaire(dp)

    register_echo(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = RedisStorage2() if config.tg_bot.use_redis else MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    await db_gino.on_startup(dp)
    await db.gino.drop_all()
    await db.gino.create_all()

    bot['config'] = config

    register_all_middlewares(dp)
    register_all_filters(dp)
    register_all_handlers(dp)

    # Установка стандартных команд:
    await set_bot_commands.set_default_commands(dp)

    # Уведомление администраторов бота о запуске:
    await notify_admins.on_startup_notify(dp)

    # Запуск бота:
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
