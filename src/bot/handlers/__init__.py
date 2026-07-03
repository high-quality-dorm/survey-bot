from aiogram import Router

from .creation import router as creation_router
from .menu import router as menu_router
from .passing import router as passing_router
from .start import router as start_router
from .stats import router as stats_router

main_router = Router()

main_router.include_router(start_router)
main_router.include_router(menu_router)
main_router.include_routers(creation_router, passing_router, stats_router)

__all__ = ["main_router"]
