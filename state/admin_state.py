from aiogram.fsm.state import StatesGroup, State

class Redaction_inline_mode(StatesGroup):
    name = State()
    gender = State()
    age = State()
    photo = State()
    anketa_description = State()
    zodiak_sign = State()
    kurs = State()
    faculty = State()
    grade = State()
    final = State()


class Touch(StatesGroup):
    touch_view = State()


class Redaction_inline_view(StatesGroup):
    name = State()
    gender = State()
    age = State()
    photo = State()
    anketa_description = State()
    zodiak_sign = State()
    kurs = State()
    faculty = State()
    grade = State()
    final = State()