from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_i18n import I18nContext, LazyFilter
from survio.main import SurveyEngine  # type: ignore[import-untyped]

from bot.keyboards import get_main_menu_kb, get_to_menu_kb
from bot.states import CreateSurvey

router = Router()


@router.message(LazyFilter("btn-to-menu"))
@router.message(F.text.lower() == "меню")
@router.message(Command("menu"))
async def handle_menu(message: Message, i18n: I18nContext) -> None:
    assert message.from_user is not None
    await message.answer(i18n.get("menu"), reply_markup=get_main_menu_kb())


@router.message(LazyFilter("btn-menu-create"))
async def handle_menu_create(
    message: Message, i18n: I18nContext, state: FSMContext
) -> None:
    await state.set_state(state=CreateSurvey.waiting_for_json)
    await message.answer(i18n.get("survey-creation-waiting-json"), reply_markup=get_to_menu_kb())


@router.message(F.text, CreateSurvey.waiting_for_json)
async def process_survey_json(
    message: Message, i18n: I18nContext, survey_engine: SurveyEngine, state: FSMContext
) -> None:
    assert message.text is not None
    try:
        survey_id = await survey_engine.load_survey(survey=message.text)
        await state.clear()
        await message.answer(text=i18n.get("survey-creation-success", survey_id=survey_id), reply_markup=get_to_menu_kb())
    except Exception:
        await message.answer(text=i18n.get("survey-creation-error"), reply_markup=get_to_menu_kb())


@router.message(LazyFilter("btn-menu-start-survey"))
async def handle_menu_start_survey(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("menu-start-survey"), reply_markup=get_to_menu_kb())


@router.message(LazyFilter("btn-menu-statistics"))
async def handle_menu_statistics(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("menu-statistics"), reply_markup=get_to_menu_kb())
