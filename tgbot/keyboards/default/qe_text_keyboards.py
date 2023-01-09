from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_kb = ReplyKeyboardMarkup(
    row_width=2,
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="📝 Создать опрос")
        ],
        [
            KeyboardButton(text="🗂 Созданные опросы"),
            KeyboardButton(text="📌 Пройденные опросы")
        ]
    ]
)


cancel_fill_qe = ReplyKeyboardMarkup(
    row_width=1,
    resize_keyboard=True,
    keyboard=[
        [
            KeyboardButton(text="❌ Отмена")
        ]
    ]
)


# question_type_kb = ReplyKeyboardMarkup(
#     row_width=2,
#     resize_keyboard=True,
#     keyboard=[
#         [
#             KeyboardButton(text="Открытый"),
#             KeyboardButton(text="")
#         ]
#     ]
# )
