from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from States.keyboard_states import DeleteKeyboardState
from aiogram.fsm.context import FSMContext
from database.requests import Request
from filters.admin_filter import IsAdmin
from keyboard.admin_menu import *

delete = Router()
@delete.message(Command('settings'), IsAdmin())
async def process_settings_command(message: Message):
    await message.answer('Выберите, что будем делать:', reply_markup=admin_keyboard)

@delete.callback_query(IsAdmin(), F.data == 'delete')
async def process_edit_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text('Выберите раздел для удаления:', reply_markup=admin_choice)
    await state.set_state(DeleteKeyboardState.delete)

@delete.callback_query(IsAdmin(), DeleteKeyboardState.delete, F.data == 'category')
async def process_choiceCat_command(callback: CallbackQuery, request: Request, state: FSMContext):
    categories = await request.get_goods()
    await callback.message.edit_text('Выберите категорию для удаления', reply_markup=await send_category(categories=categories))
    await state.clear()

@delete.callback_query(IsAdmin(), F.data.startswith('admin_category_'))
async def process_deleteCat_command(callback: CallbackQuery, request: Request):
    result = callback.data.split('_')
    await request.delete_category(int(result[2]))
    await callback.message.edit_text('Категория успешно удалена', reply_markup=admin_keyboard)



@delete.callback_query(IsAdmin(), DeleteKeyboardState.delete, F.data == 'subcategory')
async def process_choiceCat_command(callback: CallbackQuery, request: Request, state: FSMContext):
    subcategories = await request.get_subgoods()
    await callback.message.edit_text('Выберите подкатегорию для удаления', reply_markup=await send_subcategory(subcategories))
    await state.clear()

@delete.callback_query(IsAdmin(), F.data.startswith('admin_subcategory_'))
async def process_deleteCat_command(callback: CallbackQuery, request: Request):
    result = callback.data.split('_')
    await request.delete_subcategory(int(result[2]))
    await callback.message.edit_text('Подкатегория успешно удалена', reply_markup=admin_keyboard)



@delete.callback_query(IsAdmin(), DeleteKeyboardState.delete, F.data == 'item')
async def process_choiceCat_command(callback: CallbackQuery, request: Request, state: FSMContext):
    items = await request.get_items()
    await callback.message.edit_text('Выберите товар для удаления', reply_markup=await send_items(items))
    await state.clear()

@delete.callback_query(IsAdmin(), F.data.startswith('items_'))
async def process_deleteCat_command(callback: CallbackQuery, request: Request):
    result = callback.data.split('_')
    await request.delete_item(int(result[1]))
    await callback.message.edit_text('Товар успешно удален', reply_markup=admin_keyboard)
