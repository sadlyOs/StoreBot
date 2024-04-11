from aiogram import Router


def setup_message_routers():
    from . import user_handlers, other_handlers, admin_handlers
    router = Router()
    router.include_router(admin_handlers.create)
    router.include_router(admin_handlers.edit)
    router.include_router(admin_handlers.delete)
    router.include_router(user_handlers.user)
    router.include_router(other_handlers.other)
    
    return router