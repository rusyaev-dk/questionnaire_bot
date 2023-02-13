from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from tgbot.services.database import db_commands
from tgbot.misc.dependences import ANSWER_LETTERS
from tgbot.services.service_functions import parse_share_link


question_type_callback = CallbackData("action", "question_type")
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


qe_approve_callback = CallbackData("action", "approve")
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


answers_approve_callback = CallbackData("action", "approve")
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


qe_list_callback = CallbackData("action", "qe_id")


async def qe_list_kb(questionnaires: list):
    buttons = []
    for qe in questionnaires:
        questionnaire = await db_commands.select_questionnaire(qe_id=qe.qe_id)
        buttons.append(InlineKeyboardButton(text=f"{questionnaire.title}",
                                            callback_data=qe_list_callback.new(qe_id=f"{qe.qe_id}")))
    keyboard = InlineKeyboardMarkup()
    i = 0
    while i < (len(buttons) - 1):
        keyboard.row(buttons[i], buttons[i + 1])
        i += 2
    if len(buttons) % 2 != 0:
        keyboard.row(buttons[-1])
    keyboard.row(InlineKeyboardButton(text="◀️ Главное меню", callback_data=qe_list_callback.new(qe_id="main_menu")))
    return keyboard


statistics_acts = ["step_back", "main_menu", "get_file", "freeze_qe", "resume_qe", "delete", "share_link"]


statistics_kb_callback = CallbackData("action", "act")


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
        InlineKeyboardButton(text="📨 Ответы", callback_data=statistics_kb_callback.new(act="get_file")),
        InlineKeyboardButton(text="📎 Ссылка", switch_inline_query=share_link),
        InlineKeyboardButton(text=f"{status}", callback_data=statistics_kb_callback.new(act=f"{act}")),
        InlineKeyboardButton(text="🚮 Удалить опрос", callback_data=statistics_kb_callback.new(act="delete")),
        InlineKeyboardButton(text="◀️ Назад", callback_data=statistics_kb_callback.new(act="step_back")),
        InlineKeyboardButton(text="⏺ Главное меню", callback_data=statistics_kb_callback.new(act="main_menu"))
    ]

    keyboard.row(buttons[0], buttons[1])
    keyboard.row(buttons[2])
    keyboard.row(buttons[3])
    keyboard.row(buttons[4], buttons[5])
    return keyboard


file_type_callback = CallbackData("action", "f_type")
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


delete_qe_approve_callback = CallbackData("action", "approve")
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


replay_qe_approve_callback = CallbackData("action", "approve")
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


answer_options_callback = CallbackData("action", "answer")


def parse_answer_options_kb(options_quantity: int):
    buttons = []
    for i in range(options_quantity):
        buttons.append(InlineKeyboardButton(text=f"{ANSWER_LETTERS[i]}",
                                            callback_data=answer_options_callback.new(answer=f"{ANSWER_LETTERS[i]}{i}")))
    buttons.append(InlineKeyboardButton(text="❌ Отмена", callback_data=answer_options_callback.new(answer="cancel")))

    keyboard = InlineKeyboardMarkup(row_width=options_quantity)

    for i in range(options_quantity):
        keyboard.insert(buttons[i])

    keyboard.row(buttons[-1])
    return keyboard


user_profile_menu_callback = CallbackData("action", "option")
user_profile_options = ["main_menu", "change_email"]
user_profile_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📬 Сменить электронную почту",
                                 callback_data=user_profile_menu_callback.new(option="change_email"))
        ],
        [
            InlineKeyboardButton(text="◀ Главное меню",
                                 callback_data=user_profile_menu_callback.new(option="main_menu"))
        ]
    ]
)
