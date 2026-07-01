from aiogram.fsm.state import State, StatesGroup


class CreateSurvey(StatesGroup):
    waiting_for_json = State()
