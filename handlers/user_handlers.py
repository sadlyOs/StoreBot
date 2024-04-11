from contextlib import suppress
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest
from lexicon.lexicon import LEXICON_RU, text_button
from aiogram import F, Bot
from aiogram.types import InputMediaPhoto, Message, CallbackQuery, PreCheckoutQuery, LabeledPrice
from aiogram import Router
from aiogram.filters import Command, CommandStart
from database.requests import Request
from keyboard.menu import *
from States.keyboard_states import UserKeyboardState as KeyboardState
from aiogram.fsm.context import FSMContext
from config_data.settings_config import Config

user = Router()

@user.callback_query(F.data == 'cancel')
@user.message(CommandStart())
async def process_start_command(message: Message | CallbackQuery, request: Request):
    await request.set_user(message.from_user.id)
    if isinstance(message, Message):
        await message.answer_photo(caption=LEXICON_RU['/start'], 
                                   photo='AgACAgIAAxkBAAIFoWYWfMrjX_wkwbstsMLkfQU7MAmgAALx3DEbio24SOG7Ovyt_1cgAQADAgADeAADNAQ',
                                   reply_markup=keyboard)
    else:
        photo = InputMediaPhoto(media='AgACAgIAAxkBAAIFoWYWfMrjX_wkwbstsMLkfQU7MAmgAALx3DEbio24SOG7Ovyt_1cgAQADAgADeAADNAQ', caption=LEXICON_RU['/start'])
        await message.message.edit_media(media=photo, reply_markup=keyboard)
        await message.answer('')

@user.message(Command('help'))
async def process_help_command(message: Message, request: Request):
    await request.set_user(message.from_user.id)
    await message.answer(LEXICON_RU['/help'])

@user.callback_query(F.data == 'goods')
async def process_menu_command(callback: CallbackQuery, request: Request, state: FSMContext):

    goods = await request.get_goods()
    await callback.answer('')

    await callback.message.answer(LEXICON_RU['Собаки'], reply_markup=await categories_keyboard(goods=goods))
    await state.set_state(KeyboardState.button1)

@user.callback_query(Goods.filter(), KeyboardState.button1)
async def process_sub_command(callback: CallbackQuery, request: Request, state: FSMContext):

    subcatecories = await request.get_subgoods(callback.data.split(':')[1])

    await callback.answer('')
    await callback.message.edit_text(LEXICON_RU['Порода'], reply_markup=await subcategories_keyboard(subgoods=subcatecories))
    await state.set_state(KeyboardState.button2)

@user.callback_query(Goods.filter(), KeyboardState.button2)
async def process_item_command(callback: CallbackQuery, callback_data: Goods, request: Request, state: FSMContext):
    print(callback_data.subcategory_id)
    items = await request.get_items(callback_data.subcategory_id)
    print(len(items))
    try:
        await callback.message.answer_photo(photo=items[0].photo,
                                            caption=await text_button(items[0].name, 
                                            items[0].description, 
                                            items[0].price,),
                                            reply_markup=await paginator(items[0].id,callback_data.subcategory_id))
    except:
        await callback.message.edit_text("Пока нет товаров в наличие")
    await callback.answer('')
    await state.clear()

@user.callback_query(Pagination.filter(F.action.in_(['prev', 'next'])))
async def process_pagination_command(callback: CallbackQuery, callback_data: Pagination, request: Request):
    print(callback_data.subcategory_id)
    items = await request.get_items(callback_data.subcategory_id)
    page_num = int(callback_data.page)
    if callback_data.action == 'prev':
        page = page_num - 1 if page_num > 0 else 0
    else:
        page = page_num + 1 if page_num <= len(items) else page_num

    with suppress(TelegramBadRequest | IndexError):
        photo = InputMediaPhoto(media=items[page].photo, caption=await text_button(items[page].name, items[page].description, items[page].price))
        await callback.message.edit_media(media=photo, reply_markup=await paginator(items[page].id, callback_data.subcategory_id, page))
        

    await callback.answer('') 



@user.callback_query(F.data.startswith('basket_'))
async def process_basketadd_command(callback: CallbackQuery, request: Request):
    result = callback.data.split('_')
    await request.add_item_basket(item_id=int(result[1]), callback=callback)
    

@user.callback_query(F.data == 'basket')
async def process_basket_command(callback: CallbackQuery, request: Request):
    basket = await request.get_basket(user_id=callback.from_user.id)
    items = [await request.get_items(item_id=i.item) for i in basket]
    try:
        await callback.message.answer_photo(photo=items[0].photo,
                                                    caption=await text_button(items[0].name, 
                                                    items[0].description, 
                                                    items[0].price,),
                                                    reply_markup=await paginator2(items[0].id))
    except:
        await callback.message.answer("Корзина пуста")
    await callback.answer('')

@user.callback_query(Pagination2.filter(F.action.in_(['basket_prev', 'basket_next'])))
async def process_pagination_command(callback: CallbackQuery, callback_data: Pagination2, request: Request):
    basket = await request.get_basket(callback.from_user.id)
    items = [await request.get_items(item_id=i.item) for i in basket]
    page_num = int(callback_data.page)
    if callback_data.action == 'basket_prev':
        page = page_num - 1 if page_num > 0 else 0
    else:
        page = page_num + 1 if page_num <= len(items) else page_num

    with suppress(TelegramBadRequest | IndexError):
        photo = InputMediaPhoto(media=items[page].photo, caption=await text_button(items[page].name, items[page].description, items[page].price))
        await callback.message.edit_media(media=photo, reply_markup=await paginator2(page=page, item_id=items[page].id))
    await callback.answer('')

@user.callback_query(F.data.startswith('buy_'))
async def process_pagination_command(callback: CallbackQuery, request: Request, bot: Bot):
    result = callback.data.split('_')
    item = await request.get_items(item_id=int(result[1]))
    photo = InputMediaPhoto(media='AgACAgIAAxkBAAIFoWYWfMrjX_wkwbstsMLkfQU7MAmgAALx3DEbio24SOG7Ovyt_1cgAQADAgADeAADNAQ',
                            caption=LEXICON_RU['/start'])

    await callback.message.edit_media(media=photo, reply_markup=keyboard)
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=f'Товар: {item.name}',
        description=item.description,
        payload=f'{item.id}',
        provider_token=Config().CLICK.get_secret_value(),
        currency='rub',
        prices=[
            LabeledPrice(
                label='Дополнительно',
                amount=item.price*100
            ),
        ],
        start_parameter='nztcoder',
        provider_data=None,
        photo_url='https://www.google.com/url?sa=i&url=https%3A%2F%2Fru.freepik.com%2Fpremium-vector%2Fcute-penguin-holding-money-animal-cartoon-concept-isolated_20884027.htm&psig=AOvVaw39dwSOdFy0iC6le1o7LLva&ust=1712838032909000&source=images&cd=vfe&opi=89978449&ved=0CBIQjRxqFwoTCPCZ7Labt4UDFQAAAAAdAAAAABAI',
        need_name=True,
        need_phone_number=True,
        need_email=True,
        need_shipping_address=False,
        protect_content=False,
        reply_to_message_id=None,
        allow_sending_without_reply=True,
        reply_markup=None,
        request_timeout=15
    )

@user.pre_checkout_query()
async def checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    

@user.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def payment(message: Message, request: Request):
    await request.delete_item_basket(int(message.successful_payment.invoice_payload))
    await request.add_item_purchase(item_id=int(message.successful_payment.invoice_payload), user_id=message.from_user.id)
    msg = f'Товар успешно куплен {message.successful_payment.total_amount // 100} {message.successful_payment.currency}.' \
          f'\r\nНаш Влаdick получил заявку и взламывает ваш номер.' \
          f'\r\nНажмите на /start'
    await message.answer(msg)

@user.callback_query(F.data == 'purches')
async def process_purches_command(call: CallbackQuery, request: Request):
    purches = await request.get_purches(call.from_user.id)
    items = [await request.get_items(item_id=i.item) for i in purches]
    try:
        await call.message.answer_photo(photo=items[0].photo,
                                                    caption=await text_button(items[0].name, 
                                                    items[0].description, 
                                                    items[0].price,),
                                                    reply_markup=await paginator3())
    except:
        await call.message.answer("Вы ещё ничего не покупили")
    await call.answer('')

@user.callback_query(Pagination3.filter(F.action.in_(['purches_prev', 'purches_next'])))
async def process_purches_move_command(call: CallbackQuery, callback_data: Pagination3, request: Request):
    purches = await request.get_purches(call.from_user.id)
    items = [await request.get_items(item_id=i.item) for i in purches]
    print(len(items))
    page_num = int(callback_data.page)
    if callback_data.action == 'purches_prev':
        page = page_num - 1 if page_num > 0 else 0
    else:
        page = page_num + 1 if page_num <= len(items) else page_num

    with suppress(TelegramBadRequest | IndexError):
        photo = InputMediaPhoto(media=items[page].photo, caption=await text_button(items[page].name, items[page].description, items[page].price))
        await call.message.edit_media(media=photo, reply_markup=await paginator3(page=page))
    await call.answer('')
