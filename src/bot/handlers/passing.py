from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram_i18n import I18nContext, LazyFilter
from survio.main import SurveyEngine  # type: ignore[import-untyped]
from survio.schemas.schemas import Question  # type: ignore[import-untyped]

from bot.keyboards import get_to_menu_kb
from bot.keyboards.common import get_survey_answer_kb
from bot.states import StartSurvey

router = Router()


@router.message(LazyFilter("btn-menu-start-survey"), StateFilter(None))
async def handle_menu_start_survey(
    message: Message, i18n: I18nContext, state: FSMContext
) -> None:
    await state.set_state(state=StartSurvey.waiting_for_survey_uuid)
    await message.answer(
        i18n.get("survey-start-waiting-uuid"), reply_markup=get_to_menu_kb()
    )


async def prepare_question(
    question: Question, state: FSMContext
) -> tuple[str, ReplyKeyboardMarkup | ReplyKeyboardRemove]:

    first_answer = question.answers[0]
    if not first_answer.answer:
        await state.set_data(data={"free": first_answer.id})
        print(first_answer.id)
        return (f"{question.question}\nСвободный ответ", ReplyKeyboardRemove())

    answers = {f"{i + 1}": answer.id for i, answer in enumerate(question.answers)}
    await state.set_data(data=answers)
    text: str = f"{question.question}\n" + "\n".join(
        [f"{i + 1}. {answer.answer}" for i, answer in enumerate(question.answers)]
    )
    return (text, get_survey_answer_kb(nums=list(range(1, len(answers) + 1))))


@router.message(F.text, StartSurvey.waiting_for_survey_uuid)
async def handle_start_survey_id(
    message: Message, i18n: I18nContext, survey_engine: SurveyEngine, state: FSMContext
) -> None:
    assert message.text is not None
    survey_uuid = message.text
    try:
        question: Question = await survey_engine.start_survey(survey_uuid=survey_uuid)
        await survey_engine.delete_user_passes(survey_uuid=survey_uuid)

        survey = await survey_engine.get_survey(survey_uuid)
        await message.answer(
            i18n.get(
                "survey-representation",
                title=survey.title,
                description=survey.description,
            )
        )

        await state.set_state(state=StartSurvey.answering_question)
        text, reply_markup = await prepare_question(question=question, state=state)
        await message.answer(text=text, reply_markup=reply_markup)

    except Exception:
        await message.answer(
            text=i18n.get("survey-start-error"), reply_markup=get_to_menu_kb()
        )


@router.message(F.text, StartSurvey.answering_question)
async def handle_survey_answer(
    message: Message, i18n: I18nContext, survey_engine: SurveyEngine, state: FSMContext
) -> None:
    assert message.text is not None

    data = await state.get_data()

    free_answer_id = data.get("free", None)
    if free_answer_id:
        print(free_answer_id)
        question: Question | None = await survey_engine.submit_answer(
            answer_id=free_answer_id, answer=message.text
        )
    else:
        answer_id = data.get(message.text, None)
        if not answer_id:
            await message.answer(
                text=i18n.get("survey-answer-error"), reply_markup=get_to_menu_kb()
            )
            return
        question = await survey_engine.submit_answer(answer_id=answer_id)

    if question is None:
        await state.clear()
        await message.answer(text=i18n.get("survey-end"), reply_markup=get_to_menu_kb())
        return

    text, reply_markup = await prepare_question(question=question, state=state)
    await message.answer(text=text, reply_markup=reply_markup)
