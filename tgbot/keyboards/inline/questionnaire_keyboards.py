from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

q_type_callback = CallbackData("action", "q_type")
q_approve_callback = CallbackData("action", "questions_approve")
text_answers_approve_callback = CallbackData("action", "answers_approve")

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

q_approves = ["true", "false"]
questionnaire_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Создать", callback_data=q_approve_callback.new(questions_approve="true")),
            InlineKeyboardButton(text="Отмена", callback_data=q_approve_callback.new(questions_approve="false"))
        ]
    ]
)

text_a_approves = ["true", "false"]
text_answers_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отправить", callback_data=text_answers_approve_callback.new(
                answers_approve="true")),
            InlineKeyboardButton(text="Отменить", callback_data=text_answers_approve_callback.new(
                answers_approve="false"))
        ]
    ]
)
