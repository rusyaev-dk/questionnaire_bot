from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

email_accept_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="❌ Продолжить без почты")
        ]
    ]
)

main_menu_kb = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="📝 Создать опрос")
        ],
        [
            KeyboardButton(text="🗂 Созданные опросы"),
            KeyboardButton(text="🗃 Пройденные опросы")
        ],
        [
            KeyboardButton(text="🔖 Мой профиль")
        ]
    ]
)
