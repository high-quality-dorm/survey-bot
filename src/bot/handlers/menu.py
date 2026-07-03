from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup
from aiogram_i18n import I18nContext, LazyFilter
from survio.main import SurveyEngine  # type: ignore[import-untyped]

from bot.keyboards import get_main_menu_kb, get_to_menu_kb
from bot.keyboards.common import get_survey_answer_kb
from bot.states import CreateSurvey, StartSurvey
from packages.survio.src.survio.schemas.schemas import Question

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
    await message.answer(
        i18n.get("survey-creation-waiting-json"), reply_markup=get_to_menu_kb()
    )


@router.message(F.text, CreateSurvey.waiting_for_json)
async def process_survey_json(
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


async def prepare_question(
    question: Question, i18n: I18nContext, state: FSMContext
) -> tuple[str, ReplyKeyboardMarkup]:
    answers = {f"{i + 1}": answer.id for i, answer in enumerate(question.answers)}
    await state.set_data(data=answers)
    text: str = f"{question.question}\n" + "\n".join(
        [f"{i + 1}. {answer.answer}" for i, answer in enumerate(question.answers)]
    )
    return (text, get_survey_answer_kb(nums=list(range(1, len(answers) + 1))))


@router.message(LazyFilter("btn-menu-start-survey"))
async def handle_menu_start_survey(
    message: Message, i18n: I18nContext, state: FSMContext
) -> None:
    await state.set_state(state=StartSurvey.waiting_for_survey_id)
    await message.answer(
        i18n.get("survey-start-waiting-id"), reply_markup=get_to_menu_kb()
    )


@router.message(F.text, StartSurvey.waiting_for_survey_id)
async def process_survey_id(
    message: Message, i18n: I18nContext, survey_engine: SurveyEngine, state: FSMContext
) -> None:
    assert message.text is not None
    try:
        question: Question = await survey_engine.start_survey(survey_uuid=message.text)

        await state.set_state(state=StartSurvey.answering_question)
        text, reply_markup = await prepare_question(
            question=question, i18n=i18n, state=state
        )
        await message.answer(text=text, reply_markup=reply_markup)
    except Exception:
        await message.answer(
            text=i18n.get("survey-start-error"), reply_markup=get_to_menu_kb()
        )


@router.message(F.text, StartSurvey.answering_question)
async def process_survey_answer(
    message: Message, i18n: I18nContext, survey_engine: SurveyEngine, state: FSMContext
) -> None:
    assert message.text is not None

    data = await state.get_data()
    answer_id = None

    print(data)
    answer_id = data.get(message.text, None)

    if not answer_id:
        await message.answer(
            text=i18n.get("survey-answer-error"), reply_markup=get_to_menu_kb()
        )
        return

    await survey_engine.submit_answer(answer_id=answer_id)

    question: Question | None = survey_engine.get_current_question()
    if question is None:
        await state.clear()
        await message.answer(text=i18n.get("survey-end"), reply_markup=get_to_menu_kb())
        return

    text, reply_markup = await prepare_question(
        question=question, i18n=i18n, state=state
    )
    await message.answer(text=text, reply_markup=reply_markup)


@router.message(LazyFilter("btn-menu-statistics"))
async def handle_menu_statistics(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("menu-statistics"), reply_markup=get_to_menu_kb())
