from aiogram.fsm.state import StatesGroup, State


class Register_anketa(StatesGroup):
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
    redaction = State()
    name_red = State()
    gender_red = State()
    age_red = State()
    photo_red = State()
    anketa_description_red = State()
    zodiak_sign_red = State()
    kurs_red = State()
    faculty_red = State()
    grade_red = State()


class Register_profile(StatesGroup):
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

