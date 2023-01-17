import openpyxl
from openpyxl.styles import Alignment

from tgbot.misc.dependences import BOT_USERNAME
from tgbot.services.database import db_commands
from tgbot.services.database.db_models import Questionnaire


async def create_xlsx_file(questionnaire: Questionnaire):
    book = openpyxl.Workbook()
    book.remove(book.active)
    sheet_1 = book.create_sheet("Ответы")
    sheet_2 = book.create_sheet("Статистика")
    qe_title = questionnaire.title

    questions_fields = await db_commands.select_questions(qe_id=questionnaire.qe_id)
    questions = []
    for field in questions_fields:
        questions.append(field.question_text)
    sheet_1.append(questions)

    passed_qes = await db_commands.select_passed_users(qe_id=questionnaire.qe_id)
    for passed_qe in passed_qes:
        answers_fields = await db_commands.select_user_answers(respondent_id=passed_qe.respondent_id,
                                                               qe_id=questionnaire.qe_id)
        answers = []
        for field in answers_fields:
            answers.append(field.answer_text)
        sheet_1.append(answers)

    letters = ["A", "B", "C", "D", "E", "F", "G", "H"]
    i = 0
    for letter in letters:
        if i > questionnaire.questions_quantity - 1:
            break
        col = sheet_1.column_dimensions[f'{letter}']
        col.width = len(questions[i]) + 10
        col.alignment = Alignment(horizontal="center")
        i += 1

    path = rf'D:\PycharmProjects\{BOT_USERNAME}\tgbot\misc\Excel\xlsx_files\{qe_title}.xlsx'
    book.save(path)

    return path
