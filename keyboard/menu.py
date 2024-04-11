from aiogram.filters import callback_data
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from database.requests import Request

class Goods(CallbackData, prefix="Goods"):
    category_id: int
    subcategory_id: int
    item_id: int

class Pagination(CallbackData, prefix="move"):
    action: str 
    subcategory_id: int
    page: int


class Pagination2(CallbackData, prefix="move"):
    action: str
    page: int

class Pagination3(CallbackData, prefix="move"):
    action: str
    page: int

keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Товары", callback_data="goods"),
        InlineKeyboardButton(text="Корзина", callback_data="basket")
    ],
    [
        InlineKeyboardButton(text="Оплаченные", callback_data="purches")
    ]])

async def categories_keyboard(goods):
    keyboard = InlineKeyboardBuilder()
    for good in goods:
        keyboard.add(InlineKeyboardButton(
            text=good.name,
            callback_data=Goods(category_id=good.id, subcategory_id=0,item_id=0).pack()
        ))

    return keyboard.adjust(2).as_markup()


async def subcategories_keyboard(subgoods):
    keyboard = InlineKeyboardBuilder()
    for good in subgoods:
        keyboard.add(InlineKeyboardButton(
            text=good.name,
            callback_data=Goods(category_id=good.category, subcategory_id=good.id,item_id=0).pack()
        ))
    return keyboard.adjust(2).as_markup()
   

async def paginator(item_id: int, subcategory_id: int = 0, page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🔙", callback_data=Pagination(action="prev", page=page, subcategory_id=subcategory_id).pack()),
        InlineKeyboardButton(text="🔜", callback_data=Pagination(action="next", page=page, subcategory_id=subcategory_id).pack()),
        InlineKeyboardButton(text="Назад", callback_data="cancel"),
        InlineKeyboardButton(text='Добавить в корзину', callback_data=f"basket_{item_id}")
    )
    return builder.adjust(3).as_markup()
    
async def paginator2(item_id: int, page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🔙", callback_data=Pagination2(action="basket_prev", page=page).pack()),
        InlineKeyboardButton(text="🔜", callback_data=Pagination2(action="basket_next", page=page).pack()),
        InlineKeyboardButton(text="Назад", callback_data="cancel"),
        InlineKeyboardButton(text="Купить", callback_data=f"buy_{item_id}")
    )
    return builder.adjust(3).as_markup()

async def paginator3(page: int = 0):
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="🔙", callback_data=Pagination3(action="purches_prev", page=page).pack()),
        InlineKeyboardButton(text="🔜", callback_data=Pagination3(action="purches_next", page=page).pack()),
        InlineKeyboardButton(text="Назад", callback_data="cancel"),
    )
    return builder.adjust(3).as_markup()