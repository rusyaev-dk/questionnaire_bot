import random
import string

from aiogram.utils.markdown import quote_html

from tgbot.misc.dependences import ANSWER_LETTERS, BOT_USERNAME
from tgbot.infrastructure.database import db_commands
from tgbot.infrastructure.database.db_models import Questionnaire


def generate_random_id(length: int):
    """
    Generates random combination of symbols for questionnaire_id in database
    """

    symbols = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(symbols) for i in range(length))


async def parse_share_link(qe_id):
    return f"https://t.me/{BOT_USERNAME}/?start={qe_id}"


async def parse_questions_text(questionnaire: Questionnaire):
    """
    Parsing questions entered by user
    """

    questions = await db_commands.select_questions(qe_id=questionnaire.qe_id)
    text = (f"🔍 Ваш опрос:\n\n"
            f"🔹 Название: <b>{questionnaire.title}</b>\n")
    for i in range(questionnaire.questions_quantity):

        question_text = questions[i].question_text
        if question_text is None and questions[i].question_photo_id:
            question_text = "Изображение"
        elif question_text and questions[i].question_photo_id:
            question_text = f"Изображение с описанием: {quote_html(question_text)}"
        elif question_text is None and questions[i].question_doc_id:
            question_text = "Файл"
        elif question_text and questions[i].question_doc_id:
            question_text = f"Файл с описанием {quote_html(question_text)}"

        text += f"\n• {i + 1}-й вопрос: <b>{quote_html(question_text)}</b>\n"
        if questions[i].question_type == "closed":
            answer_options = await db_commands.select_answer_options(question_id=questions[i].question_id)
            j = 0
            for answer_option in answer_options:
                text += f"<b>{ANSWER_LETTERS[j]}:</b> {quote_html(answer_option.answer_option_text)}\n"
                j += 1
    text += "\nСоздать опрос?"
    return text


async def parse_answers_text(answers: list, answers_quantity: int):
    """
    Parsing answers entered by user
    """

    text = "📄 Ваши ответы:\n"
    for i in range(answers_quantity):
        text += f"• {i + 1}-й ответ: <b>{quote_html(answers[i].answer_text)}</b>\n"
    text += "\nОтправить ответы?"
    return text


async def parse_answer_options(answer_options: list):
    """
    Parsing answer options for a given test
    """

    text = "📄 Варианты ответов:\n"
    for i in range(len(answer_options)):
        text += f"<b>{ANSWER_LETTERS[i]}:</b> {quote_html(answer_options[i].answer_option_text)}\n"
    text += "\n⬇️ Выберите ответ:"
    return text


async def created_qe_info(questionnaire: Questionnaire):
    """
    Parsing created by user questionnaire info with statistics etc.
    """

    questions = await db_commands.select_questions(qe_id=questionnaire.qe_id)

    text = f"🔹 Название: <b>{questionnaire.title}</b>\n"
    for i in range(questionnaire.questions_quantity):

        question_text = questions[i].question_text
        if question_text is None and questions[i].question_photo_id:
            question_text = "Изображение"
        elif question_text and questions[i].question_photo_id:
            question_text = f"Изображение с описанием: {quote_html(question_text)}"
        elif question_text is None and questions[i].question_doc_id:
            question_text = "Файл"
        elif question_text and questions[i].question_doc_id:
            question_text = f"Файл с описанием {quote_html(question_text)}"

        text += f"\n• {i + 1}-й вопрос: <b>{quote_html(question_text)}</b>\n"
        if questions[i].question_type == "closed":
            answer_options = await db_commands.select_answer_options(question_id=questions[i].question_id)
            j = 0
            for answer_option in answer_options:
                text += f"<b>{ANSWER_LETTERS[j]}:</b> {quote_html(answer_option.answer_option_text)}\n"
                j += 1
    return text


async def get_average_completion_time(qe_id: str):
    passed_qes = await db_commands.select_passed_qes(qe_id=qe_id)
    completion_time = 0
    if len(passed_qes) > 0:
        for passed_qe in passed_qes:
            completion_time += passed_qe.completion_time
        if completion_time / len(passed_qes) > 60:
            time_value = "мин."
            return completion_time / (len(passed_qes) * 60), time_value
        time_value = "сек."
        return completion_time / len(passed_qes), time_value
    time_value = "сек."
    return 0, time_value


async def statistics_qe_text(questionnaire: Questionnaire):
    """
    Parsing questionnaire statistics
    """

    if questionnaire.passed_by == 0:
        pass_percent = 0
    else:
        pass_percent = questionnaire.passed_by / questionnaire.started_by * 100

    average_ct = await get_average_completion_time(qe_id=questionnaire.qe_id)
    statistics_text = (f"📊 Статистика опроса:\n"
                       f"• Начали проходить: <b>{questionnaire.started_by}</b> чел.\n"
                       f"• Прошли: <b>{questionnaire.passed_by}</b> чел.\n"
                       f"• Процент прохождения: <b>{pass_percent:.1f}%</b>\n"
                       f"• Среднее время прохождения: <b>{average_ct[0]:.1f}</b> {average_ct[1]}\n"
                       f"• Дата создания: <b>{questionnaire.created_at}</b>")
    return statistics_text


async def passed_qe_info(respondent_id: int, questionnaire: Questionnaire, markdown: bool):
    """
    Parsing passed by user questionnaire info with statistics etc.
    """

    questions = await db_commands.select_questions(qe_id=questionnaire.qe_id)
    answers = await db_commands.select_user_answers(respondent_id=respondent_id, qe_id=questionnaire.qe_id)
    passed_qe = await db_commands.select_passed_qe(respondent_id=respondent_id, qe_id=questionnaire.qe_id)
    if markdown:
        text = f"🔹 Название: **{questionnaire.title}**\n\n"
        for i in range(questionnaire.questions_quantity):
            text += (f"• {i + 1}-й вопрос: **{questions[i].question_text}**\n"
                     f"Ответ: **{answers[i].answer_text}**\n\n")
        text += f"• Дата прохождения: **{passed_qe.passed_at}**"
    else:
        text = f"🔹 Название: <b>{questionnaire.title}</b>\n\n"
        for i in range(questionnaire.questions_quantity):

            question_text = questions[i].question_text
            if question_text is None and questions[i].question_photo_id:
                question_text = "Изображение"
            elif question_text and questions[i].question_photo_id:
                question_text = f"Изображение с описанием: {quote_html(question_text)}"
            elif question_text is None and questions[i].question_doc_id:
                question_text = "Файл"
            elif question_text and questions[i].question_doc_id:
                question_text = f"Файл с описанием {quote_html(question_text)}"

            text += (f"• {i + 1}-й вопрос: <b>{quote_html(question_text)}</b>\n"
                     f"Ответ: <b>{quote_html(answers[i].answer_text)}</b>\n\n")
        text += f"• Дата прохождения: <b>{passed_qe.passed_at}</b>"
    return text
