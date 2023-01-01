from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.services.database import db_commands

q_type_callback = CallbackData("action", "q_type")
q_approve_callback = CallbackData("action", "questions_approve")
text_answers_approve_callback = CallbackData("action", "answers_approve")
qe_list_callback = CallbackData("action", "quest_id")
statistics_kb_callback = CallbackData("action", "act")

q_types = ["test", "text", "main_menu"]
questionnaire_type_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Текстовый опрос", callback_data=q_type_callback.new(q_type="text")),
            InlineKeyboardButton(text="Тесты", callback_data=q_type_callback.new(q_type="test"))
        ],
        [
            InlineKeyboardButton(text="◀️ Главное меню", callback_data=q_type_callback.new(q_type="main_menu"))
        ]
    ]
)

q_approves = ["true", "false"]
questionnaire_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Создать", callback_data=q_approve_callback.new(questions_approve="true")),
            InlineKeyboardButton(text="❌ Отмена", callback_data=q_approve_callback.new(questions_approve="false"))
        ]
    ]
)

text_a_approves = ["true", "false"]
text_answers_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Отправить", callback_data=text_answers_approve_callback.new(
                answers_approve="true")),
            InlineKeyboardButton(text="❌ Отменить", callback_data=text_answers_approve_callback.new(
                answers_approve="false"))
        ]
    ]
)


async def generate_qe_list(questionnaires: list):
    buttons = []
    for quest_id in questionnaires:
        questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
        buttons.append(InlineKeyboardButton(text=f"{questionnaire.title}",
                                            callback_data=qe_list_callback.new(quest_id=f"{quest_id}")))

    buttons.append(InlineKeyboardButton(text="◀️ Главное меню",
                                        callback_data=qe_list_callback.new(quest_id="main_menu")))
    keyboard = InlineKeyboardMarkup(row_width=1)
    for button in buttons:
        keyboard.row(button)
    return keyboard


def share_link(link: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="✉️ Поделиться ссылкой",
                             switch_inline_query=f"{link}")
    ]
    keyboard.row(buttons[0])
    return keyboard


statistics_acts = ["step_back", "main_menu", "get_file", "freeze", "resume", "answers", "share"]


def created_qe_statistics_kb(is_active: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if is_active == "true":
        text = "⏸ Остановить опрос"
        act = "freeze"
    else:
        text = "▶️ Возобновить опрос"
        act = "resume"
    buttons = [
        InlineKeyboardButton(text="Получить файл", callback_data=statistics_kb_callback.new(act="get_file")),
        InlineKeyboardButton(text=f"{text}", callback_data=statistics_kb_callback.new(act=f"{act}")),
        InlineKeyboardButton(text="📨 Посмотреть ответы", callback_data=statistics_kb_callback.new(act="answers")),
        InlineKeyboardButton(text="◀️ Назад", callback_data=statistics_kb_callback.new(act="step_back")),
        InlineKeyboardButton(text="⏺ Главное меню", callback_data=statistics_kb_callback.new(act="main_menu"))
    ]

    keyboard.row(buttons[0])
    keyboard.row(buttons[1])
    keyboard.row(buttons[2])
    keyboard.row(buttons[3], buttons[4])
    return keyboard


def passed_qe_statistics_kb(share_text: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="✉️ Поделиться ответами", switch_inline_query=f"{share_text}"),
        InlineKeyboardButton(text="◀️ Назад", callback_data=statistics_kb_callback.new(act="step_back")),
        InlineKeyboardButton(text="⏺ Главное меню", callback_data=statistics_kb_callback.new(act="main_menu"))
    ]
    keyboard.row(buttons[0])
    keyboard.row(buttons[1], buttons[2])
    return keyboard
