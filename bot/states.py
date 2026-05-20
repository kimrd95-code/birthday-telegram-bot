from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    birth_date = State()
    team = State()


class ProfileEdit(StatesGroup):
    field = State()
    value = State()
