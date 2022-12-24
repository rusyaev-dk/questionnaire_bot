from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="Создать опрос"),
            KeyboardButton(text="Пустая кнопка")
        ],
        [
            KeyboardButton(text="Пустая кнопка 2")
        ]
    ]
)
