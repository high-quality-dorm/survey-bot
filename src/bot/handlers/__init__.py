from aiogram import Router

from .menu import router as menu_router
from .start import router as start_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(menu_router)

__all__ = ["main_router"]
