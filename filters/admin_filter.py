from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

class IsAdmin(BaseFilter):

    async def __call__(self, message: Message | CallbackQuery) -> bool:
        from config_data.settings_config import Config
        return message.from_user.id == int(Config().ADMIN_ID.get_secret_value())