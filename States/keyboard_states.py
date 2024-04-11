from aiogram.fsm.state import StatesGroup, State

class UserKeyboardState(StatesGroup):
    button1 = State()
    button2 = State()
    button3 = State()

class CreateKeyboardState(StatesGroup):
    name = State()
    button2 = State()
    button3 = State()

class CreateItems(StatesGroup):
    subcategory = State()
    description = State()
    photo = State()
    price = State()

class EditKeyboardState(StatesGroup):
    start = State()
    category = State()
    subcategory = State()
    item = State()
    item_choice = State()
    item_edit = State()
    name = State()
    choice = State()
    move = State()

class DeleteKeyboardState(StatesGroup):
    delete = State()

   