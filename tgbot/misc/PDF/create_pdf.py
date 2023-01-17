from decimal import Decimal
from pathlib import Path

from borb.pdf import SingleColumnLayout, FlexibleColumnWidthTable, X11Color, Alignment, Image, FixedColumnWidthTable, \
    TableCell, UnorderedList, HexColor
from borb.pdf import PageLayout
from borb.pdf import Paragraph
from borb.pdf import Document
from borb.pdf import Page
from borb.pdf import PDF
from borb.pdf.canvas.font.font import Font
from borb.pdf.canvas.font.simple_font.true_type_font import TrueTypeFont

from tgbot.services.database import db_commands
from tgbot.services.database.db_models import Questionnaire


async def create_pdf_file(questionnaire: Questionnaire):
    doc: Document = Document()
    page: Page = Page()
    doc.add_page(page)
    layout: PageLayout = SingleColumnLayout(page)

    title = questionnaire.title
    questions_quantity = questionnaire.questions_quantity
    author = await db_commands.select_user(id=questionnaire.creator_id)
    questions = await db_commands.select_questions(qe_id=questionnaire.qe_id)

    font_path: Path = Path(__file__).parent / "arial.ttf"
    custom_font: Font = TrueTypeFont.true_type_font_from_file(font_path)

    layout.add(
        FixedColumnWidthTable(
            number_of_rows=2,
            number_of_columns=2,
            column_widths=[Decimal(0.2), Decimal(0.9)]
        )
        .add(
            TableCell(
                Image(
                    image="https://ie.wampi.ru/2023/01/02/bot_logo.jpg",
                    width=Decimal(80),
                    height=Decimal(80),
                ),
                row_span=2,
            )
        )
        .add(
            Paragraph(
                text=f"Название: {title}",
                font=custom_font,
                font_size=Decimal(16),
                padding_bottom=Decimal(10),
            )
        )
        .add(
            UnorderedList()
            .add(Paragraph(text=f"Дата создания опроса: {questionnaire.created_at}", font=custom_font))
            .add(Paragraph(text=f"Автор опроса: {author.name}", font=custom_font))
            .add(Paragraph(text="Создано с помощью @questionnaire_unibot", font=custom_font))
        )
        .no_borders()
    )

    layout.add(Paragraph(""))

    passed_qes = await db_commands.select_passed_users(qe_id=questionnaire.qe_id)
    table = FlexibleColumnWidthTable(number_of_columns=questions_quantity + 1, number_of_rows=len(passed_qes) + 1)
    table.add(Paragraph("№", font=custom_font))

    for i in range(questions_quantity):
        table.add(Paragraph(text=f"{questions[i].question_text}", font=custom_font))
    table.even_odd_row_colors(X11Color("LightGray"), X11Color("White"))

    counter = 1

    for passed_qe in passed_qes:
        answers = await db_commands.select_user_answers(respondent_id=passed_qe.respondent_id,
                                                        qe_id=questionnaire.qe_id)
        try:
            for i in range(questions_quantity):
                if i % questions_quantity == 0:
                    table.add(Paragraph(text=f"{counter}", font=custom_font))
                table.add(Paragraph(text=f"{answers[i].answer_text}", font=custom_font))
            counter += 1
        except AssertionError:
            doc.add_page(page)
            layout: PageLayout = SingleColumnLayout(page)
            table = FlexibleColumnWidthTable(number_of_columns=questions_quantity + 1, number_of_rows=len(passed_qes) + 1)
            continue

    table.set_padding_on_all_cells(Decimal(20), Decimal(20), Decimal(20), Decimal(20))

    layout.add(table)

    path = rf"D:\PycharmProjects\MSU_Questionnaire_Bot\tgbot\services\PDF\pdf_files\{title}.pdf"

    with open(Path(path), "wb") as out_file_handle:
        PDF.dumps(out_file_handle, doc)

    return path
