from tgbot.services.database import db_commands
from tgbot.services.database.db_models import Questionnaire


async def parse_questions_text(questionnaire):
    questions_list = questionnaire.questions
    text = "Отлично, Ваш опрос создан!\n" + "\n".join(
        f"<b>Вопрос {i + 1}:</b>\n{questions_list[i]}\n" for i in range(0, len(questions_list))
    )
    return text
