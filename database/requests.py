from typing import Any
from .models import User, Category, Subcategory, Purchase, Basket, Item
from sqlalchemy import and_, func, select, update, delete
from aiogram.types import CallbackQuery, Message
from keyboard.admin_menu import admin_keyboard

class Request:
    def __init__(self, session):
        self.session = session
        # self.logger = logger

    async def set_user(self, tg_id):
        user = await self.session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            self.session.add(User(tg_id=tg_id, email=''))
            await self.session.commit()

    '''Получения'''

    async def get_goods(self):
        goods = await self.session.scalars(select(Category))
        return goods
    
    async def get_subgoods(self, category_id=None):

        if category_id is None:
            all_subgoods = await self.session.scalars(select(Subcategory))
            return all_subgoods
        subgoods = await self.session.scalars(select(Subcategory).where(Subcategory.category == category_id))
        return subgoods

    async def get_items(self, subcategory_id: int | None = None, item_id: int | None = None):
        if not subcategory_id is None:
            items = await self.session.scalars(select(Item).where(Item.subcategory_id == subcategory_id))
            sort_items = [i for i in items]
            return sort_items
        if not item_id is None:
            return  await self.session.scalar(select(Item).where(Item.id == item_id))

        return [i for i in await self.session.scalars(select(Item))]
    async def get_basket(self, user_id: int):
        basket = await self.session.scalars(select(Basket).where(Basket.user == user_id))
        return basket

    async def get_purches(self, user_id: int):
        purches = await self.session.scalars(select(Purchase).where(Purchase.user == user_id))
        return purches
    '''Создания'''

    async def set_category(self, name):
        category = await self.session.scalar(select(User).where(Category.name == name))
        if not category:
            self.session.add(Category(name=name))
            await self.session.commit()

    async def set_subcategory(self, name, category_id):
        subcategory = await self.session.scalar(select(Subcategory).where(and_(
            Subcategory.category == category_id,
            Subcategory.name == name
            )))

        if not subcategory:
            self.session.add(Subcategory(name=name, category=category_id))
            await self.session.commit()
    
    async def set_item(self, name, description, photo, price, subcategory_id):
        items = await self.session.scalar(select(Subcategory).where(and_(
            Item.subcategory_id == subcategory_id,
            Item.name == name
        )))
        if not items:
            self.session.add(Item(name=name, description=description, photo=photo,
            price=price, subcategory_id=subcategory_id))
            await self.session.commit()

    async def add_item_basket(self, item_id, callback: CallbackQuery):
        
        basket = await self.session.scalar(select(Basket).where(and_(
            Basket.item == item_id,
            Basket.user == callback.from_user.id,
            )))
        if not basket:
            self.session.add(Basket(user=callback.from_user.id, item=item_id))
            await callback.answer('Товар добавлен в карзину', show_alert=True)
            await self.session.commit()
        else:
            await callback.answer('Такой товар уже существует у вас в корзине', show_alert=True)

    async def add_item_purchase(self, item_id: int, user_id: int):
        self.session.add(Purchase(user=user_id, item=item_id))
        await self.session.commit()


    '''Редактирования'''
    async def edit_category(self, category_id: int, new_name: str):
        category = await self.session.scalar(select(Category).where(Category.id == category_id))
        category.name = new_name
        await self.session.commit()
    
    async def edit_subcategory(self, subcategory_id: int, new_name: str | None = None, category_id: int | None = None):
        subcategory = await self.session.scalar(select(Subcategory).where(Subcategory.id == subcategory_id))
        if not category_id is None:
            subcategory.category = category_id
        elif not new_name is None:
            subcategory.name = new_name
        await self.session.commit()


    async def edit_item(self, item_id: int, keyword: str, message: Message):
        item = await self.session.scalar(select(Item).where(Item.id == item_id))
        if keyword == 'name':
            item.name = message.text
            await message.answer('Название товара успешно изменено', reply_markup=admin_keyboard)
        elif keyword == 'description':
            item.description = message.text
            await message.answer('Описание товара успешно изменено', reply_markup=admin_keyboard)
        elif keyword == 'price':
            if message.text.isdigit():
                item.price = int(message.text)
                await message.answer('Цена товара успешно изменена', reply_markup=admin_keyboard)
            else:
                return False
        else:
            if message.photo:
                item.photo = message.photo[-1].file_id
                await message.answer('Фото товара успешно изменено', reply_markup=admin_keyboard)
            else:
                return False
        await self.session.commit()
        return True
       
    '''Удаления'''
    async def delete_category(self, category_id):
        category = await self.session.scalar(select(Category).where(Category.id == category_id))
        await self.session.delete(category)
        await self.session.commit()
    
    async def delete_subcategory(self, subcategory_id):
        subcategory = await self.session.scalar(select(Subcategory).where(Subcategory.id == subcategory_id))
        await self.session.delete(subcategory)
        await self.session.commit()

    async def delete_item(self, item_id):
        item = await self.session.scalar(select(Item).where(Item.id == item_id))
        await self.session.delete(item)
        await self.session.commit()

    async def delete_item_basket(self, item_id):
        item = await self.session.scalar(select(Basket).where(Basket.item == item_id))
        await self.session.delete(item)
        await self.session.commit()

    