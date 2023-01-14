from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.services.database import db_commands
from tgbot.services.dependences import ANSWER_LETTERS
from tgbot.services.service_functions import parse_share_link

question_type_callback = CallbackData("action", "question_type")
qe_approve_callback = CallbackData("action", "approve")
answers_approve_callback = CallbackData("action", "approve")
qe_list_callback = CallbackData("action", "qe_id")
statistics_kb_callback = CallbackData("action", "act")
file_type_callback = CallbackData("action", "f_type")
delete_qe_approve_callback = CallbackData("action", "approve")
replay_qe_approve_callback = CallbackData("action", "approve")
answer_options_callback = CallbackData("action", "answer")


question_types = ["open", "closed", "cancel"]
question_type_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Открытый", callback_data=question_type_callback.new(question_type="open")),
            InlineKeyboardButton(text="Закрытый", callback_data=question_type_callback.new(question_type="closed"))
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data=question_type_callback.new(question_type="cancel"))
        ]
    ]
)

qe_approves = ["create", "delete"]
questionnaire_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Создать", callback_data=qe_approve_callback.new(approve="create")),
            InlineKeyboardButton(text="❌ Отмена", callback_data=qe_approve_callback.new(approve="delete"))
        ]
    ]
)

answers_approves = ["send", "delete"]
answers_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Отправить", callback_data=answers_approve_callback.new(
                approve="send")),
            InlineKeyboardButton(text="❌ Отмена", callback_data=answers_approve_callback.new(
                approve="delete"))
        ]
    ]
)

# cancel_create_qe_callback = CallbackData("action", "approve")
# cancel_create_qe_kb = InlineKeyboardMarkup(
#     row_width=1,
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_create_qe_callback.new(approve="cancel_create"))
#         ]
#     ]
# )


async def qe_list_kb(questionnaires: list):
    buttons = []
    for qe in questionnaires:
        questionnaire = await db_commands.select_questionnaire(qe_id=qe.qe_id)
        buttons.append(InlineKeyboardButton(text=f"{questionnaire.title}",
                                            callback_data=qe_list_callback.new(qe_id=f"{qe.qe_id}")))

    buttons.append(InlineKeyboardButton(text="◀️ Главное меню",
                                        callback_data=qe_list_callback.new(qe_id="main_menu")))
    keyboard = InlineKeyboardMarkup(row_width=1)
    for button in buttons:
        keyboard.row(button)
    return keyboard


statistics_acts = ["step_back", "main_menu", "get_file", "freeze_qe", "resume_qe", "delete", "share_link"]


async def created_qe_statistics_kb(is_active: str, qe_id: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    if is_active == "true":
        status = "⏸ Остановить опрос"
        act = "freeze_qe"
    else:
        status = "▶️ Возобновить опрос"
        act = "resume_qe"
    share_link = await parse_share_link(qe_id=qe_id)
    buttons = [
        InlineKeyboardButton(text="📨 Посмотреть ответы", callback_data=statistics_kb_callback.new(act="get_file")),
        InlineKeyboardButton(text="📎 Ссылка", switch_inline_query=share_link),
        InlineKeyboardButton(text=f"{status}", callback_data=statistics_kb_callback.new(act=f"{act}")),
        InlineKeyboardButton(text="🚮 Удалить опрос", callback_data=statistics_kb_callback.new(act="delete")),
        InlineKeyboardButton(text="◀️ Назад", callback_data=statistics_kb_callback.new(act="step_back")),
        InlineKeyboardButton(text="⏺ Главное меню", callback_data=statistics_kb_callback.new(act="main_menu"))
    ]

    keyboard.row(buttons[0])
    keyboard.row(buttons[1])
    keyboard.row(buttons[2])
    keyboard.row(buttons[3])
    keyboard.row(buttons[4], buttons[5])
    return keyboard


f_types = ["pdf", "xlsx", "step_back", "main_menu"]
file_type_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📕 PDF", callback_data=file_type_callback.new(f_type="pdf"))

        ],
        [
            InlineKeyboardButton(text="📗 Excel", callback_data=file_type_callback.new(f_type="xlsx"))
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data=file_type_callback.new(f_type="step_back")),
            InlineKeyboardButton(text="⏺ Главное меню", callback_data=file_type_callback.new(f_type="main_menu"))
        ]
    ]
)


delete_qe_approves = ["delete", "cancel"]
delete_qe_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Удалить", callback_data=delete_qe_approve_callback.new(approve="delete")),
            InlineKeyboardButton(text="❌ Отмена", callback_data=delete_qe_approve_callback.new(approve="cancel"))
        ]
    ]
)


def passed_qe_statistics_kb(share_text: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text="✉️ Поделиться ответами", switch_inline_query=share_text),
        InlineKeyboardButton(text="◀️ Назад", callback_data=statistics_kb_callback.new(act="step_back")),
        InlineKeyboardButton(text="⏺ Главное меню", callback_data=statistics_kb_callback.new(act="main_menu"))
    ]
    keyboard.row(buttons[0])
    keyboard.row(buttons[1], buttons[2])
    return keyboard


def share_link_kb(share_link: str):
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton(text="✉️ Поделиться ссылкой",
                             switch_inline_query=share_link)
    ]
    keyboard.row(buttons[0])
    return keyboard


pass_qe_approve_callback = CallbackData("action", "approve")
pass_qe_approves = ["pass", "cancel"]
pass_qe_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Начать", callback_data=pass_qe_approve_callback.new(approve="pass")),
            InlineKeyboardButton(text="❌ Отмена", callback_data=pass_qe_approve_callback.new(approve="cancel"))
        ]
    ]
)

replay_approves = ["cancel", "replay"]
replay_qe_approve_kb = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Пройти заново",
                                 callback_data=replay_qe_approve_callback.new(approve="replay")),
            InlineKeyboardButton(text="❌ Отмена", callback_data=replay_qe_approve_callback.new(approve="cancel"))
        ]
    ]
)


def parse_answer_options_kb(options_quantity: int):
    buttons = []
    for i in range(options_quantity):
        buttons.append(InlineKeyboardButton(text=f"{ANSWER_LETTERS[i]}",
                                            callback_data=answer_options_callback.new(answer=f"{ANSWER_LETTERS[i]}")))
    buttons.append(InlineKeyboardButton(text="❌ Отмена", callback_data=answer_options_callback.new(answer="cancel")))

    keyboard = InlineKeyboardMarkup(row_width=options_quantity)

    for i in range(options_quantity):
        keyboard.insert(buttons[i])

    keyboard.row(buttons[-1])
    return keyboard
