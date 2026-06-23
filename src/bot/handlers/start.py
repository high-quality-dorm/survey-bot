from aiogram import Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def handle_cmd_start(message: Message, command: CommandObject) -> None:
    await message.answer(f"Привет! Аргументы: {command.args}")
