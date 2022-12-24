from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

q_type_callback = CallbackData("action", "q_type")

q_types = ["test", "text", "cancel"]
questionnaire_type_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Тесты", callback_data=q_type_callback.new(q_type="test"))
        ],
        [
            InlineKeyboardButton(text="Текстовый опрос", callback_data=q_type_callback.new(q_type="text"))
        ],
        [
            InlineKeyboardButton(text="Главное меню", callback_data=q_type_callback.new(q_type="cancel"))
        ]
    ]
)
