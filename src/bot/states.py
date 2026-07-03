from aiogram.fsm.state import State, StatesGroup


class CreateSurvey(StatesGroup):
    waiting_for_json = State()


class StartSurvey(StatesGroup):
    waiting_for_survey_uuid = State()
    answering_question = State()


class ShowStatistics(StatesGroup):
    waiting_for_survey_uuid = State()
