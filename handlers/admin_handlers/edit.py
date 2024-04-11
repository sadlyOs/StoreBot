from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from States.keyboard_states import EditKeyboardState
from aiogram.fsm.context import FSMContext
from database.requests import Request
from filters.admin_filter import IsAdmin
from keyboard.admin_menu import *

edit = Router()
@edit.message(Command('settings'), IsAdmin())
async def process_settings_command(message: Message):
    await message.answer('Выберите, что будем делать:', reply_markup=admin_keyboard)

@edit.callback_query(IsAdmin(), F.data == 'edit')
async def process_edit_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text('Выберите раздел для редактирования:', reply_markup=admin_choice)
    await state.set_state(EditKeyboardState.start)

@edit.callback_query(IsAdmin(), EditKeyboardState.start, F.data == 'category')
async def process_button1_command(callback: CallbackQuery, state: FSMContext, request: Request):
    await callback.answer('')
    categories = await request.get_goods()
    await callback.message.edit_text('Выберите категорию для редактирования', reply_markup=await send_category(categories))
    await state.set_state(EditKeyboardState.category)

@edit.callback_query(IsAdmin(), EditKeyboardState.category)
async def process_category_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    try:
        await state.update_data(category_id=int(callback.data.split('_')[2]))
    except:
        await state.clear()
        return 
    await callback.message.edit_text("Введите другое название для категории")
    await state.set_state(EditKeyboardState.name)

@edit.message(IsAdmin(), EditKeyboardState.name)
async def process_name_command(message: Message, state: FSMContext, request: Request):
    result = await state.get_data()
    if result['subcategory_id']:
        await request.edit_subcategory(subcategory_id=result['subcategory_id'], new_name=message.text)
        await message.answer("Название подкатегории изменено", reply_markup=admin_keyboard)
    else:
        await request.edit_category(category_id=result['category_id'], new_name=message.text)
        await message.answer("Название категории изменено", reply_markup=admin_keyboard)
    await state.clear()


@edit.callback_query(IsAdmin(), F.data == 'subcategory', EditKeyboardState.start)
async def process_buttonsub_command(callback: CallbackQuery, state: FSMContext, request: Request):
    await callback.answer('')
    subcategories = await request.get_subgoods()
    await callback.message.edit_text('Выберите подкатегорию для редактирования', reply_markup=await send_subcategory(subcategories))
    await state.set_state(EditKeyboardState.subcategory)

@edit.callback_query(IsAdmin(), EditKeyboardState.subcategory)
async def process_subcat_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    try:
        await state.update_data(subcategory_id=int(callback.data.split('_')[2]))
    except:
        await state.clear()
        return
    await callback.message.edit_text('Выберите действие для изменения', reply_markup=await move_or_name_keyboard())
    await state.set_state(EditKeyboardState.choice)

@edit.callback_query(IsAdmin(), F.data.in_(['move', 'edit_name']), EditKeyboardState.choice)
async def process_choice_command(callback: CallbackQuery, state: FSMContext, request: Request):
    if callback.data == 'move':
        categories = await request.get_goods()
        await callback.message.edit_text('Выберите категорию в которую будет помещена подкатегория', reply_markup=await send_category(categories))
        await state.set_state(EditKeyboardState.move)
    else:
        await callback.message.edit_text('Введите другое название для подкатегории')
        await state.set_state(EditKeyboardState.name)

@edit.callback_query(IsAdmin(), EditKeyboardState.move)
async def process_move_command(callback: CallbackQuery, state: FSMContext, request: Request):
    result = await state.get_data()
    await request.edit_subcategory(subcategory_id=result['subcategory_id'], category_id=int(callback.data.split('_')[2]))
    await callback.message.edit_text('Подкатегория была перемещена')
    await state.clear()



@edit.callback_query(IsAdmin(), F.data == 'item', EditKeyboardState.start)
async def process_buttonsub_command(callback: CallbackQuery, state: FSMContext, request: Request):
    items = await request.get_items()
    await callback.message.edit_text('Выберите товар для изменения', reply_markup=await send_items(items))
    await state.set_state(EditKeyboardState.item)


@edit.callback_query(IsAdmin(), EditKeyboardState.item)
async def process_buttonsub_command(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выберите действие для изменения', reply_markup=await choice_edit_items(callback.data.split('_')[1]))
    await state.clear()


@edit.callback_query(IsAdmin(), F.data.startswith('edit_item_'))
async def process_item_choice_command(callback: CallbackQuery, state: FSMContext):
    result = callback.data.split('_')
    await state.update_data(item_id=result[3])
    if result[2] == 'name':
        await state.update_data(keyword='name')
        await callback.message.edit_text('Введите новое название товара')
    elif result[2] == 'description':
        await state.update_data(keyword='description')
        await callback.message.edit_text('Введите новое описание товара')
    elif result[2] == 'price':
        await state.update_data(keyword='price')
        await callback.message.edit_text('Введите новую цену товара')
    else:
        await state.update_data(keyword='photo')
        await callback.message.edit_text('Отправьте новое фото товара')
    await state.set_state(EditKeyboardState.item_edit)




@edit.message(EditKeyboardState.item_edit)
async def process_item_edit_edit(message: Message, state: FSMContext, request: Request):
    result = await state.get_data()
    if await request.edit_item(result['item_id'], result['keyword'], message):
        await state.clear()
    else:
        await message.answer('Отправленные вами данные не совпадают с запрошенными данными, повторите попытку')
    


