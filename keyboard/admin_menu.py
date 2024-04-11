from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Создать', callback_data='create'),
        InlineKeyboardButton(text='Изменить', callback_data='edit')
    ],
    [
        InlineKeyboardButton(text='Удалить', callback_data='delete')
    ]
    ])

admin_choice = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Категорию', callback_data='category'),
        InlineKeyboardButton(text='Подкатегорию', callback_data='subcategory')
    ],
    [
        InlineKeyboardButton(text='Товар', callback_data='item')
    ]
    ])

async def send_category(categories):
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(
            InlineKeyboardButton(text=category.name, callback_data=f'admin_category_{category.id}')
        )

    return keyboard.adjust(1).as_markup()

async def send_subcategory(subcategories, name='admin'):
    keyboard = InlineKeyboardBuilder()
    for subcategory in subcategories:
        keyboard.add(
            InlineKeyboardButton(text=subcategory.name, callback_data=f'{name}_subcategory_{subcategory.id}')
        )

    return keyboard.adjust(1).as_markup()

async def send_items(items):
    keyboard = InlineKeyboardBuilder()
    for item in items:
        keyboard.add(
            InlineKeyboardButton(text=item.name, callback_data=f'items_{item.id}')
        )
    return keyboard.adjust(1).as_markup()

async def move_or_name_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='Переместить', callback_data='move'),
        InlineKeyboardButton(text='Изменить', callback_data='edit_name'))
    
    return keyboard.as_markup()

async def choice_edit_items(item_id):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(
        InlineKeyboardButton(text='Название', callback_data=f'edit_item_name_{item_id}'),
        InlineKeyboardButton(text='Описание', callback_data=f'edit_item_description_{item_id}'),
        InlineKeyboardButton(text='Цена', callback_data=f'edit_item_price_{item_id}'),
        InlineKeyboardButton(text='Фото', callback_data=f'edit_item_photo_{item_id}')
        )
    
    return keyboard.as_markup()

