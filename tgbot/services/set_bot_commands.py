from aiogram import types, Dispatcher


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Запустить бота"),
            types.BotCommand("help", "Помощь"),
        ]
    )
    # Вариант, когда необходимо более упорядоченно всё оформить:
    # default_commands = {
    #     "start": "Перезапустить бота",
    #     "help": "Помощь"
    # }
    #
    # group_commands = {
    #     "biba": "Проверить бибу",
    #     "gay": "Узнать, насколько % пользователь гей",
    #     "quote": "Рандомная цитата"
    # }
    #
    # await dp.bot.set_my_commands(
    #     [BotCommand(name, value) for name, value in default_commands.items()],
    #     scope=types.BotCommandScopeDefault()
    # )
    #
    # await dp.bot.set_my_commands(
    #     [BotCommand(name, value) for name, value in group_commands.items()],
    #     scope=types.BotCommandScopeAllGroupChats()
    # )
