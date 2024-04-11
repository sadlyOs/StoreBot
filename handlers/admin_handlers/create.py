from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from States.keyboard_states import CreateKeyboardState, CreateItems
from aiogram.fsm.context import FSMContext
from database.requests import Request
from filters.admin_filter import IsAdmin
from lexicon.lexicon import text_button
from keyboard.admin_menu import *

create = Router()

@create.message(Command('settings'), IsAdmin())
async def process_settings_command(message: Message):
    await message.answer('Выберите, что будем делать:', reply_markup=admin_keyboard)

@create.callback_query(IsAdmin(), F.data == 'create')
async def process_create_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await callback.message.edit_text('Выберите раздел для создания:', reply_markup=admin_choice)
    await state.set_state(CreateKeyboardState.name)

@create.callback_query(IsAdmin(), CreateKeyboardState.name)
async def process_name_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.update_data(type=callback.data)
    await callback.message.answer("Введите название для объекта")
    await state.set_state(CreateKeyboardState.button2)

@create.message(IsAdmin(), CreateKeyboardState.button2)
async def process_button2_command(message: Message, state: FSMContext, request: Request, logger):
    await state.update_data(name=message.text)
    result = await state.get_data()
    if result['type'] == 'category':
        await request.set_category(message.text)
        await message.answer('Категория создана')
        await state.clear()
    else:
        categories = [i for i in await request.get_goods()]
        logger.info(categories)
        await message.answer('Выберите категорию', reply_markup=await send_category(categories=categories))
        await state.set_state(CreateKeyboardState.button3)


@create.callback_query(IsAdmin(), CreateKeyboardState.button3)
async def process_button3_command(callback: CallbackQuery, state: FSMContext, request: Request):
    await callback.answer('')
    result = await state.get_data()
    category_id = callback.data.split('_')[2]
    await state.clear()
    if result['type'] == 'subcategory':
        await request.set_subcategory(name=result['name'], category_id=category_id)
        await callback.message.answer('Подкатегория создана')
    else:
        await callback.message.edit_text('Выберите подкатегорию', reply_markup=await send_subcategory(
            subcategories=await request.get_subgoods(category_id), name=result['name']))
        await state.set_state(CreateItems.subcategory)
    

@create.callback_query(IsAdmin(), CreateItems.subcategory)
async def process_sub_command(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.update_data(subcategory_id=callback.data.split('_')[2], name=callback.data.split('_')[0])
    await state.update_data()    
    await callback.message.edit_text('Отправь описание товара')
    await state.set_state(CreateItems.description)

@create.message(IsAdmin(), CreateItems.description)
async def process_description_command(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer('Отправь фото товара')
    await state.set_state(CreateItems.photo)

@create.message(F.photo, IsAdmin(), CreateItems.photo)
async def process_photo_command(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(photo=file_id)
    await message.answer('Введите цену товара')
    await state.set_state(CreateItems.price)

@create.message(IsAdmin(), CreateItems.price)
async def process_finish_command(message: Message, state: FSMContext, request: Request):
    result = await state.get_data()
    await request.set_item(name=result['name'],
                           description=result['description'],
                           photo=result['photo'],
                           price=message.text,
                           subcategory_id=result['subcategory_id'])
    await message.answer('Создан товар:\n\n')
    await message.answer_photo(
        photo=result['photo'],
        caption=await text_button(result['name'], result['description'], message.text),
    )

    await state.clear()