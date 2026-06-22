from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject) -> None:
    message.answer(f"Привет! Аргументы: {command.args}")
