import random, string

from tgbot.services.database import db_commands
from tgbot.services.database.db_models import Questionnaire
from tgbot.services.dependences import ANSWER_LETTERS


def get_rand_id(length: int):
    """
    Generates random combination of symbols for questionnaire_id in database
    """

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(symbols) for i in range(length))


async def parse_questions_text(questionnaire: Questionnaire):
    """
    Parsing questions entered by user
    """

    questions_list = questionnaire.questions
    text = (f"🔍 Ваш опрос:\n\n "
            f"🔹 Название: <b>{questionnaire.title}</b>\n\n")
    for i in range(len(questions_list)):
        text += f"{i + 1}-й вопрос : <b>{questions_list[i][1]}</b>\n"
    text += "\n\nСоздать опрос?"
    return text


async def parse_answers_text(answers: list):
    """
    Parsing answers entered by user
    """

    text = "📄 Ваши ответы:\n\n"
    for i in range(len(answers)):
        text += f"{i + 1}-й ответ: <b>{answers[i]}</b>\n"
    text += "\n\nОтправить ответы?"
    return text


async def parse_answer_options(answer_options: list):
    """
    Parsing answer options for a given test
    """

    text = "📄 Варианты ответов:\n"
    for i in range(len(answer_options)):
        text += f"<b>{ANSWER_LETTERS[i]}:</b> {answer_options[i]}\n"
    text += "\n✏️ Выберите ответ:"
    return text


async def created_qe_info(questionnaire: Questionnaire):
    """
    Parsing created by user questionnaire info with statistics etc.
    """

    questions_list = questionnaire.questions
    answer_options = questionnaire.answer_options
    closed_counter = 0

    text = f"🔹 Название: <b>{questionnaire.title}</b>\n\n"
    for i in range(len(questions_list)):
        text += f"• {i + 1}-й вопрос: <b>{questions_list[i][1]}</b>\n"
        if questions_list[i][0] == "closed":
            for j in range(len(answer_options[i])):
                text += f"<b>{ANSWER_LETTERS[j]}:</b> {answer_options[i][closed_counter]}\n"
            closed_counter += 1
            text += "\n"

    if questionnaire.passed_by == 0:
        pass_percent = 0
    else:
        pass_percent = questionnaire.started_by / questionnaire.passed_by * 100

    stat_text = (f"📊 Статистика:\n"
                 f"• Начали проходить: <b>{questionnaire.started_by}</b> чел.\n"
                 f"• Прошли: <b>{questionnaire.passed_by}</b> чел.\n"
                 f"• Процент прохождения: <b>{pass_percent}%</b>\n"
                 f"• Дата создания: <b>{questionnaire.created_at}</b>")
    # text += stat_text
    return text, stat_text


async def passed_qe_info(respondent_id: int, quest_id: str, markdown: bool):
    """
    Parsing passed by user questionnaire info with statistics etc.
    """

    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    questions_list = questionnaire.questions
    qe_answers = await db_commands.select_qe_answers(respondent_id=respondent_id, quest_id=quest_id)
    answers_list = qe_answers.answers
    answer_options = questionnaire.answer_options
    closed_counter = 0

    if markdown:
        text = f"🔹 Название: **{qe_answers.title}**\n\n"
        for i in range(len(questions_list)):
            text += f"{i + 1}-й вопрос: **{questions_list[i][1]}**\n"
            if questions_list[i][0] == "closed":
                for j in range(len(answer_options[i])):
                    text += f"**{ANSWER_LETTERS[j]}:** {answer_options[i][closed_counter]}\n"
                closed_counter += 1
            text += f"Ответ: **{answers_list[i]}**\n"
        text += f"\nДата прохождения: **{qe_answers.created_at}**"
    else:
        text = f"🔹 Название: <b>{qe_answers.title}</b>\n\n"

        for i in range(len(questions_list)):
            text += f"{i + 1}-й вопрос: <b>{questions_list[i][1]}</b>\n"

            if questions_list[i][0] == "closed":
                for j in range(len(answer_options[i])):
                    text += f"<b>{ANSWER_LETTERS[j]}:</b> {answer_options[closed_counter][j]}\n"
                closed_counter += 1

            text += f"Ответ: <b>{answers_list[i]}</b>\n\n"
        text += f"Дата прохождения: <b>{qe_answers.created_at}</b>"
    return text
