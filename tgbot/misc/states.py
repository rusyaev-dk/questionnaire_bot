from aiogram.dispatcher.filters.state import StatesGroup, State


# class CreateTextQe(StatesGroup):
#     Title = State()
#     Questions_qty = State()
#     GetQuestion = State()
#     Approve = State()


class CreateQe(StatesGroup):
    Title = State()
    Questions_qty = State()
    QuestionType = State()

    OpenQuestionText = State()

    ClosedQuestionText = State()
    ClosedAnswersQuantity = State()
    ClosedAnswerText = State()

    Approve = State()


class FillQe(StatesGroup):
    QuestionType = State()
    OpenAnswer = State()
    ClosedAnswer = State()
    Approve = State()


class CreatedQeStatistics(StatesGroup):
    SelectQE = State()
    SelectStatsAct = State()
    SelectFileType = State()
    ApproveDelete = State()


class PassedQeStatistics(StatesGroup):
    SelectQE = State()
    SelectStatsAct = State()
