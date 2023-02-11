from aiogram.dispatcher.filters.state import StatesGroup, State


class UserEmail(StatesGroup):
    GetEmail = State()
    UpdateEmail = State()


class CreateQe(StatesGroup):
    Title = State()
    QuestionsQuantity = State()

    QuestionType = State()
    QuestionText = State()

    AnswerOptionsQuantity = State()
    AnswerOptionText = State()

    CreateApprove = State()


class PassQe(StatesGroup):
    PassBeginApprove = State()
    PassReplayApprove = State()

    QuestionType = State()
    OpenAnswer = State()
    ClosedAnswer = State()

    PassEndApprove = State()


class CreatedQeStatistics(StatesGroup):
    SelectQE = State()

    SelectStatsAct = State()
    SelectFileType = State()

    DeleteApprove = State()


class PassedQeStatistics(StatesGroup):
    SelectQE = State()
    SelectStatsAct = State()


class NotifyUsers(StatesGroup):
    NotifyMedia = State()
    NotifyApprove = State()
