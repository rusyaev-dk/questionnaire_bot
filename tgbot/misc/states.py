from aiogram.dispatcher.filters.state import StatesGroup, State


class CreateTextQe(StatesGroup):
    Title = State()
    Questions_qty = State()
    GetQuestion = State()
    Approve = State()


class FillQe(StatesGroup):
    GetAnswer = State()
    A1 = State()
    A2 = State()
    A3 = State()
    A4 = State()
    A5 = State()
    A6 = State()
    A7 = State()
    A8 = State()
    A9 = State()
    A10 = State()
    Approve = State()


class CreatedQeStatistics(StatesGroup):
    SelectQE = State()
    SelectStatsAct = State()
    SelectFileType = State()
    ApproveDelete = State()


class PassedQeStatistics(StatesGroup):
    SelectQE = State()
    SelectStatsAct = State()
