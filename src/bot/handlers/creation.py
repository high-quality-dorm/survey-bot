from click.formatting import measure_table
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_i18n import I18nContext, LazyFilter
from survio.main import SurveyEngine  # type: ignore[import-untyped]

from bot.keyboards import get_to_menu_kb
from bot.states import CreateSurvey

router = Router()


@router.message(LazyFilter("btn-menu-create"), StateFilter(None))
async def handle_menu_create(
    message: Message, i18n: I18nContext, state: FSMContext
) -> None:
    await state.set_state(state=CreateSurvey.waiting_for_json)
    await message.answer(
        i18n.get("survey-creation-waiting-json"), reply_markup=get_to_menu_kb()
    )
    await message.answer("Пример входных данных (скопируйте и отправьте):")
    await message.answer("""{
  "title": "Опрос о продукте",
  "description": "Пожалуйста, ответьте на несколько вопросов",
  "questions": [
    {
      "name": "q1",
      "question": "Как вы узнали о нашем продукте?",
      "answers": [
        { "answer": "Из рекламы в соцсетях", "next_question": "q2" },
        { "answer": "По рекомендации друзей", "next_question": "q2" },
        { "answer": "Случайно в интернете", "next_question": "q3" }
      ]
    },
    {
      "name": "q2",
      "question": "Что вам понравилось больше всего?",
      "answers": [
        { "answer": null, "next_question": null }
      ]
    },
    {
      "name": "q3",
      "question": "Хотели бы вы порекомендовать нас друзьям?",
      "answers": [
        { "answer": "Да", "next_question": null },
        { "answer": "Нет", "next_question": null }
      ]
    }
  ]
}""")


@router.message(F.text, CreateSurvey.waiting_for_json)
async def handle_survey_json(
    message: Message, i18n: I18nContext, survey_engine: SurveyEngine, state: FSMContext
) -> None:
    assert message.text is not None
    try:
        survey_id = await survey_engine.load_survey(survey=message.text)
        await state.clear()
        await message.answer(
            text=i18n.get("survey-creation-success", survey_id=survey_id),
            reply_markup=get_to_menu_kb(),
        )
    except Exception:
        await message.answer(
            text=i18n.get("survey-creation-error"), reply_markup=get_to_menu_kb()
        )
