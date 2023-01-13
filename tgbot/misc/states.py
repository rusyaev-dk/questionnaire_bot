from aiogram.dispatcher.filters.state import StatesGroup, State


class CreateQe(StatesGroup):
    Title = State()
    QuestionsQuantity = State()
    QuestionType = State()

    QuestionText = State()

    ClosedAnswersQuantity = State()
    ClosedAnswerText = State()

    Approve = State()


class PassQe(StatesGroup):
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
