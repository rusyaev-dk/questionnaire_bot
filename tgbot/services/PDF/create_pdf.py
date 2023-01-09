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


async def create_pdf_file(qe_text_answers_tab: list, quest_id: str):
    doc: Document = Document()
    page: Page = Page()
    doc.add_page(page)
    layout: PageLayout = SingleColumnLayout(page)

    questionnaire = await db_commands.select_questionnaire(quest_id=quest_id)
    title = questionnaire.title
    author = await db_commands.select_user(id=questionnaire.creator_id)
    quantity = int(questionnaire.questions_quantity)
    questions = questionnaire.questions

    font_path: Path = Path(__file__).parent / "calibri.ttf"
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
                    "https://ie.wampi.ru/2023/01/02/bot_logo.jpg",
                    width=Decimal(80),
                    height=Decimal(80),
                ),
                row_span=2,
            )
        )
        .add(
            Paragraph(
                f"Название: {title}",
                font=custom_font,
                font_size=Decimal(16),
                padding_bottom=Decimal(10),
            )
        )
        .add(
            UnorderedList()
            .add(Paragraph(f"Дата создания опроса: {questionnaire.created_at}", font=custom_font))
            .add(Paragraph(f"Автор опроса: {author.name}", font=custom_font))
            .add(Paragraph("Создано с помощью @questionnaire_unibot", font=custom_font))
        )
        .no_borders()
    )

    layout.add(Paragraph(""))

    table = FlexibleColumnWidthTable(number_of_columns=quantity + 1, number_of_rows=quantity)
    table.add(Paragraph("№", font=custom_font))

    for i in range(quantity):
        table.add(Paragraph(f"{questions[i]}", font=custom_font))

    table.even_odd_row_colors(X11Color("LightGray"), X11Color("White"))
    counter = 1
    for field in qe_text_answers_tab:
        qe_text_answers = await db_commands.select_qe_answers(quest_id=quest_id, respondent_id=field.respondent_id)
        answers = qe_text_answers.answers
        for i in range(quantity):
            if i % quantity == 0:
                table.add(Paragraph(f"{counter}", font=custom_font))
            table.add(Paragraph(f"{answers[i]}", font=custom_font))
        counter += 1

    table.set_padding_on_all_cells(Decimal(5), Decimal(5), Decimal(5), Decimal(5))

    layout.add(table)

    path = f"D:\PycharmProjects\MSU_Questionnaire_Bot\\tgbot\services\PDF\pdf_files\{title}.pdf"

    with open(Path(f"{path}"), "wb") as out_file_handle:
        PDF.dumps(out_file_handle, doc)

    return path
