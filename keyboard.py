from aiogram import types
import config

main_menu_btn = [
    '🔎 Выбрать игру',
    '🙍🏻‍♂️ Кабинет',
    '📆 Информация',
]

admin_sending_btn = [
    '✅ Начать', # 0
    '❌ Отменить' # 2
]

to_close = types.InlineKeyboardMarkup(row_width=3)
to_close.add(
    types.InlineKeyboardButton(text='❌', callback_data='to_close')
)


def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True, row_width=2)
    markup.add(main_menu_btn[0])
    markup.add(main_menu_btn[1], main_menu_btn[2])

    return markup

def games_menu():
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton(text='🎲 Аркада', callback_data='roll'),
        types.InlineKeyboardButton(text='🎰 Слоты', callback_data='slots'),
        )
    markup.add(
        types.InlineKeyboardButton(text='🀄️ Блекджек', callback_data='blackjack'),
        types.InlineKeyboardButton(text='🔘 Орел-Решка', callback_data='coin'),
        )
    markup.add(
        types.InlineKeyboardButton(text='🏆 Рейтинг', callback_data='rating'),
        )
    return markup

def inform_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='📜 Канал', url=config.config('channel_link')),
        types.InlineKeyboardButton(text='💬 Все проекты', url=config.config('group_link')),
        types.InlineKeyboardButton(text='🧑🏻‍💻 Администратор', url=config.config("admin_link")),
        types.InlineKeyboardButton(text='🧑🏻‍🔧 Разработчик', url=config.config("coder_link")))

    return markup

def profile():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='💳 Вывести', callback_data='withdraw'),
        types.InlineKeyboardButton(text='💳 Пополнить', callback_data='payments'),
        types.InlineKeyboardButton(text='🎁 Промокод', callback_data='promocode'),
    )
    markup.add(
        types.InlineKeyboardButton(text='🧑🏻‍💻 Партнерская программа', callback_data='refferal_web'),
    )

    return markup

def rating():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='🏆 Аркада', callback_data='rating_dice'),
        types.InlineKeyboardButton(text='🏆 BlackJack ', callback_data='rating_blackjack'),
        types.InlineKeyboardButton(text='🏆 Орел-Решка ', callback_data='rating_rubl'),
        types.InlineKeyboardButton(text='🏆 Автоматы ', callback_data='rating_slots'),
    )
    markup.add(
        types.InlineKeyboardButton(text='🔙 Назад', callback_data='to_games'),
    )

    return markup

def channel():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text='Подписаться', url='https://t.me/End_Soft'),
    )

    return markup

def exit_to_info():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text ='🔙 Назад', callback_data='to_games')
    )
    return markup

def to_cabinet():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text='🔙 Назад', callback_data='to_profile'),
    )

    return markup

def payments():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='💳 QIWI', callback_data='qiwi'),
        types.InlineKeyboardButton(text='💳 P2P', callback_data='p2p'),
    )
    markup.add(
        types.InlineKeyboardButton(text='🔙 Назад', callback_data='to_profile'),
    )

    return markup

def payment_menu(url):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='🧿 Перейти к оплате 🧿', url=url),
    )
    markup.add(
        types.InlineKeyboardButton(text='♻️ Проверить', callback_data='check_payment'),
        types.InlineKeyboardButton(text='💢 Отмена', callback_data='cancel_payment'),
    )

    return markup

def pay_p2p(url, bill_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Перейти к оплате', url=url),
    )
    markup.add(
        types.InlineKeyboardButton(text='♻️ Проверить', callback_data=f'p2p_check:{bill_id}'),
    )

    return markup

def admin_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='ℹ️ Cтатистика', callback_data='admin_info'),)
    markup.add(
        types.InlineKeyboardButton(text='⚙️ Выводы', callback_data='withdrawal_requests'),
        types.InlineKeyboardButton(text='⚙️ Рассылка', callback_data='email_sending'),
        types.InlineKeyboardButton(text='⚙️ Промокоды', callback_data='admin_promo'),
        types.InlineKeyboardButton(text='⚙️ Поиск юзера', callback_data='admin_searsh'),
        )

    return markup

def promo_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Активные промо', callback_data='active_promo'),)
    markup.add(
        types.InlineKeyboardButton(text='Создать промо', callback_data='create_promo'),
        types.InlineKeyboardButton(text='Удалить промо', callback_data='delete_promo'),
        )

    return markup

def admin_user_markup(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Изменить баланс', callback_data=f'give_bal:{user_id}'),)
    markup.add(
        types.InlineKeyboardButton(text='Бан', callback_data=f'ban_{user_id}'),
        types.InlineKeyboardButton(text='Разбан', callback_data=f'unban_{user_id}'),
        types.InlineKeyboardButton(text='Врубить подкрутку', callback_data=f'spin_up:{user_id}'),
        types.InlineKeyboardButton(text='Вырубить подкрутку', callback_data=f'spin_down:{user_id}'),
        )

    return markup


def email_sending():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text='✔️ Рассылка(только текст)', callback_data='email_sending_text'),
        types.InlineKeyboardButton(text='✔️ Рассылка(текст + фото)', callback_data='email_sending_photo'),
    )

    return markup

def admin_sending():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        admin_sending_btn[0],
        admin_sending_btn[1],
    )

    return markup

