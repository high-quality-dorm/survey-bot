from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_i18n import I18nContext, LazyFilter
from survio.main import SurveyEngine  # type: ignore[import-untyped]

from bot.keyboards import get_main_menu_kb, get_to_menu_kb
from bot.states import ShowStatistics

router = Router()


@router.message(LazyFilter("btn-menu-statistics"), StateFilter(None))
async def handle_menu_statistics(
    message: Message, i18n: I18nContext, state: FSMContext
) -> None:

    await state.set_state(state=ShowStatistics.waiting_for_survey_uuid)
    await message.answer(
        i18n.get("survey-statistics-waiting-uuid"), reply_markup=get_to_menu_kb()
    )


@router.message(F.text, ShowStatistics.waiting_for_survey_uuid)
async def handle_statistics_survey_uuid(
    message: Message, i18n: I18nContext, survey_engine: SurveyEngine, state: FSMContext
) -> None:
    assert message.text is not None
    survey_uuid = message.text

    try:
        stats = await survey_engine.get_statistics(survey_uuid=survey_uuid)
        
        text = ""
        for question, answers in stats.items():
            text += f"{question}\n"
            for answer, count in answers.items():
                text += f"- {answer}: {count}\n"

        await state.clear()
        await message.answer(
            text=f"Статистика:\n{text}",
            reply_markup=get_to_menu_kb(),
        )
    except Exception:
        await message.answer(
            text=i18n.get("survey-statistics-error"), reply_markup=get_to_menu_kb()
        )
