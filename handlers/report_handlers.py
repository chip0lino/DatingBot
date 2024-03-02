from aiogram import Router, F, Bot, types
from config import MODERATORS as admins
from aiogram.types import Message
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import database.database as bd
#from ..state.register_state import *
#from ..admin import Admin

router = Router()

from aiogram.filters import Filter
class Admin(Filter):
    global admins
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in admins
# Cоздаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFillForm(StatesGroup):
    wait_report = State()   #Состояние ожидания получения репорта от юзера
    wait_admin_report = State() #Состояние ожидания получения фидбека от админа


@router.message(F.text == 'Пожаловаться', StateFilter(default_state))
async def report(message: Message, state: FSMContext):
    await message.answer("Вы открыли репорт на анкету.\n\n.Пожалуйста, укажите причину жалобы.")
    await state.set_state(FSMFillForm.wait_report)

@router.message(StateFilter(FSMFillForm.wait_report))
async def report(message: Message, state: FSMContext, bot: Bot):
    await message.answer('Ваша жалоба успешно отправлена! Спасибо.')
    user_id = message.from_user.id
    ank_id = await bd.get_last_ank_id(user_id)
    report = message.text

    report_text = f"""
Пользователь {user_id} отправил жалобу на 
пользователя <code>{ank_id}</code>\n\n
Текст жалобы: {report} \n\n
Отправьте команду /report чтобы ответить на жалобу
    """
    for admin in admins:
        await bot.send_message(chat_id=admin, text=report_text)
    await state.clear()


@router.message(Admin(),F.text=='/report', StateFilter(default_state))
async def report_feedback(message: Message, state: FSMContext):
    await message.answer('Введите в первой строчке id юзера на которого отправили жалобу, а в следующих персональное сообщение')
    await state.set_state(FSMFillForm.wait_admin_report)

@router.message(Admin(), StateFilter(FSMFillForm.wait_admin_report))
async def report_feedback_send(message: Message, state: FSMContext, bot: Bot):
    text = message.text.split('\n')
    report_user_id = text[0]
    report_text = '\n'.join(text[1:])

    await bot.send_message(chat_id=report_user_id, text= f'На вашу анкету поступила жалоба. Сообщение от модератора:\n{report_text}')
    await message.answer(f'Отлично! Жалоба была отправлена пользователю - {report_user_id}')
    await state.clear()