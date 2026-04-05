from aiogram import Router

from .admin import router as admin_router
from .assembly import router as assembly_router
from .auxiliary import router as auxiliary_router
from .back import router as back_router
from .common import router as common_router
from .creative import router as creative_router
from .installation import router as installation_router
from .kb import router as kb_router
from .logistics import router as logistics_router
from .main_menu import router as main_menu_router
from .preparatory import router as preparatory_router
from .rvi import router as rvi_router
from .sales import router as sales_router
from .welding import router as welding_router

main_callback_router = Router()
main_callback_router.include_router(main_menu_router)
main_callback_router.include_router(back_router)
main_callback_router.include_router(welding_router)
main_callback_router.include_router(auxiliary_router)
main_callback_router.include_router(preparatory_router)
main_callback_router.include_router(assembly_router)
main_callback_router.include_router(rvi_router)
main_callback_router.include_router(common_router)
main_callback_router.include_router(admin_router)
main_callback_router.include_router(creative_router)
main_callback_router.include_router(sales_router)
main_callback_router.include_router(kb_router)
main_callback_router.include_router(logistics_router)
main_callback_router.include_router(installation_router)

__all__ = ["main_callback_router"]
