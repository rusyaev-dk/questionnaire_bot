from aiogram.dispatcher.filters.state import StatesGroup, State


class CreateQE(StatesGroup):
    Title = State()
    Questions_qty = State()
    Q1 = State()
    Q2 = State()
    Q3 = State()
    Q4 = State()
    Q5 = State()
    Q6 = State()
    Q7 = State()
    Q8 = State()
    Q9 = State()
    Q10 = State()
    Approve = State()


class FillQE(StatesGroup):
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
