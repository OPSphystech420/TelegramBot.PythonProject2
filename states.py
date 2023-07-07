from aiogram.dispatcher.filters.state import State, StatesGroup


class Search(StatesGroup):
    user_id = State()


class DelPromo(StatesGroup):
    name = State()


class CreatePromo(StatesGroup):
    name = State()
    money = State()
    amount = State()


class ActivatePromo(StatesGroup):
    name = State()


class PayP2P(StatesGroup):
    amount = State()


class Admin_give_balance(StatesGroup):
    user_id = State()
    balance = State()


class Email_sending_photo(StatesGroup):
    photo = State()
    text = State()
    action = State()
    set_down_sending = State()
    set_down_sending_confirm = State()


class Admin_sending_messages(StatesGroup):
    text = State()
    action = State()
    set_down_sending = State()
    set_down_sending_confirm = State()


class Admin_buttons(StatesGroup):
    admin_buttons_del = State()
    admin_buttons_add = State()
    admin_buttons_add_text = State()
    admin_buttons_add_photo = State()
    admin_buttons_add_confirm = State()


class CreateDice(StatesGroup):
    game = State()
    bet = State()


class CreateCoin(StatesGroup):
    bet = State()


class CreateSlots(StatesGroup):
    bet = State()


class CreateBj(StatesGroup):
    bet = State()


class Set_chance(StatesGroup):
    user_id = State()
    chance = State()


class Withdraw(StatesGroup):
    qiwi = State()
    amount = State()


class EditMinBet(StatesGroup):
    bet = State()


class EditMinWith(StatesGroup):
    bet = State()


class EditRefSum(StatesGroup):
    bet = State()
