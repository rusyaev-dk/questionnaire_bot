from aiogram import types, Dispatcher


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("main_menu", "Главное меню"),
            types.BotCommand("restart", "Перезапустить бота"),
            types.BotCommand("help", "Помощь"),
        ]
    )

    # Вариант, когда необходимо более упорядоченно всё оформить:
    # default_commands = {
    #     "start": "Перезапустить бота",
    #     "help": "Помощь"
    # }
