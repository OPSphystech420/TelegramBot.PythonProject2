from aiogram import types
from utils.user import User
from utils.mydb import *
import functions as func
import sqlite3
import random
import datetime
import config


my_games_txt = """
🃏 Мои игры: {}

💖 Выигрыш: {} RUB
💔 Проигрыш: {} RUB
📊 Профит: {} RUB

Данные приведены за все время
"""

raiting_txt = """
📊 ТОП 5 игроков в Орел и Решка:

🥇  1 место: <b>{}</b> | {} RUB

🥈 2 место: <b>{}</b> | {} RUB

🥉 3 место: <b>{}</b> | {} RUB

🏅 4 место: <b>{}</b> | {} RUB

🏅 5 место: <b>{}</b> | {} RUB

🏆 Ваше место в рейтинге: {} из {} ({} RUB)

Рейтинг обновляется каждые 5 минут.
"""


coin_game_info_txt = """
🔘 Орел-Решка#{}
💰 Ставка: {} RUB

🔘 Выигрышная сторона:  {}

🧑🏻‍💻 Создал: @{}
"""


coin_game_result_txt = """
🔘 Орел-Решка #{}
💰Банк: {} RUB

👤 @{} and @{}

👆Ваш результат: {}
👇Результат соперника: {}

{}
"""


game_result_txt = """
{} #{}
💰Банк: {} RUB

ℹ️Результаты:
❕ {} | {}
❕ {} | {}

Итог: {}
"""

class Game():

    def __init__(self, code):
        conn, cursor = connect()

        cursor.execute(f'SELECT * FROM coin WHERE id_game = "{code}"')
        info = cursor.fetchall()

        if len(info) == 0:
            self.status = False
        else:
            self.status = True

            self.id_game = info[0][0]
            self.user_id = info[0][1]
            self.bet = float(info[0][2])
            self.coin = info[0][3]

    def del_game(self):
        conn, cursor = connect()

        cursor.execute(f'DELETE FROM coin WHERE id_game = "{self.id_game}"')
        conn.commit()


def coin_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Создать игру', callback_data='create:coin'),
        types.InlineKeyboardButton(text='Обновить', callback_data='reload:coin'),
    )

    markup = get_games_menu(markup)

    markup.add(
        types.InlineKeyboardButton(text='📝Мои игры', callback_data='my_games:coin')
    )

    return markup


def get_games_menu(markup):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM coin')
    games = cursor.fetchall()

    for i in games:
        markup.add(types.InlineKeyboardButton(text=f'🔘 #Games_{i[0]} | {i[2]} RUB', callback_data=f'coin_game:{i[0]}'))

    return markup

def create_game(id_games, user_id, bet, win_coin):
    conn, cursor = connect()

    cursor.execute(f'INSERT INTO coin VALUES("{id_games}", "{user_id}", "{bet}", "{win_coin}")')
    conn.commit()


def my_games_coin(user_id):
    conn = sqlite3.connect('database/logs.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM coin_logs WHERE user_id = "{user_id}"')
    games = cursor.fetchall()

    amount_games = len(games)

    win_money = 0
    lose_money = 0

    if len(games) < int(1000):
        amount = len(games)
    else:
        amount = int(1000)


    for i in range(amount):
        if games[i][2] == 'win':
            win_money += float(games[i][3])


        elif games[i][2] == 'lose':
            lose_money += float(games[i][3])


    profit_money = win_money - lose_money
    profit_money = '{:.2f}'.format(profit_money)

    win_money = '{:.2f}'.format(win_money)
    lose_money = '{:.2f}'.format(lose_money)

    msg = my_games_txt.format(
        amount_games,
        win_money,
        lose_money,
        profit_money,
    )

    return msg

def rating_coin(user_id):
    conn = sqlite3.connect('database/logs.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM coin_stats WHERE user_id = "{user_id}"')
    user = cursor.fetchall()

    if len(user) == 0:
        cursor.execute(f'INSERT INTO coin_stats VALUES("{user_id}", "0")')
        conn.commit()

        user_money = 0
    else:
        user_money = user[0][1]

    cursor.execute(f'SELECT * FROM coin_stats')
    games = cursor.fetchall()

    games = sorted(games, key=lambda money: float(money[1]), reverse=True)


    size_top = len(games)
    user_top = 0

    for i in games:
        user_top += 1

        if i[0] == str(user_id):
            break

    msg = raiting_txt.format(
        func.profile(games[0][0])[1],
        '{}'.format(games[0][1]),
        func.profile(games[1][0])[1],
        '{}'.format(games[1][1]),
        func.profile(games[2][0])[1],
        '{}'.format(games[2][1]),
        func.profile(games[3][0])[1],
        '{}'.format(games[3][1]),
        func.profile(games[4][0])[1],
        '{}'.format(games[4][1]),
        user_top,
        size_top,
        user_money
    )

    return msg

def coin_game(code):
    game = Game(code)

    if game.status == False:
        return False
    else:
        msg = coin_game_info_txt.format(
            game.id_game,
            game.bet,
            game.coin,
            User(game.user_id).username
        )

        msg += f'🧑🏻‍💻  2 игрок: Ожидание...'

        markup = types.InlineKeyboardMarkup(row_width=1)


        markup.add(
            types.InlineKeyboardButton(text='🔘 Подбросить монетку', callback_data=f'start_game_coin:{game.id_game}'),
            types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back:coin')
        )

        return msg, markup

def del_games(id_games):
    conn, cursor = connect()

    cursor.execute(f'DELETE FROM coin_slep WHERE id_game = "{id_games}"')
    conn.commit()

def check_coin(code):
    conn, cursor = connect()

    info = cursor.execute(f'SELECT * FROM coin_slep WHERE id_game = "{code}"').fetchone()

    return info

def start_game_coin(user_id, game, value_сoin_1, value_coin_2):
    #user = func.profile(user_id)
    user = User(user_id)

    user.update_balance(-game.bet)

    value_сoin_1 = value_сoin_1
    value_coin_2 = value_coin_2

    win_money = ((game.bet * 2) / 100) * (100 - float(config.config('commission_percent')))
    profit_money = ((game.bet * 2) / 100) * float(config.config('commission_percent'))

    if value_сoin_1[0] == str(check_coin(game.id_game)[6]):
        user.update_balance(win_money)

        coin_write_game_log(game.id_game, user_id, 'win', win_money)
        coin_write_game_log(game.id_game, game.user_id, 'lose', win_money)

        status_1 = '✅Поздравляем с победой!'
        status_2 = '🔴Вы проиграли!'

    elif value_coin_2[0] == str(check_coin(game.id_game)[6]):
        User(game.user_id).update_balance(win_money)

        coin_write_game_log(game.id_game, game.user_id, 'win', win_money)
        coin_write_game_log(game.id_game, user_id, 'lose', win_money)

        status_1 = '🔴Вы проиграли!'
        status_2 = '✅Поздравляем с победой!'


    try:
        conn = sqlite3.connect('database/logs.db')
        cursor = conn.cursor()

        msg = f"{user_id} | {game.user_id}"

        cursor.execute(f'INSERT INTO coin_logs VALUES ("{msg}", "{profit_money}", "{datetime.datetime.now()}")')
        conn.commit()
    except:
        pass

    msg1 = coin_game_result_txt.format(
        game.id_game,
        win_money,
        User(user_id).username,
        User(game.user_id).username,
        value_сoin_1[0],
        value_coin_2[0],
        status_1
    )

    msg2 = coin_game_result_txt.format(
        game.id_game,
        win_money,
        User(user_id).username,
        User(game.user_id).username,
        value_сoin_1[0],
        value_coin_2[0],
        status_2
    )

    return [user_id, game.user_id], [msg1, msg2], [value_сoin_1[1], value_coin_2[1]]

def coin_write_game_log(id, user_id, status, bet):
    conn = sqlite3.connect('database/logs.db')
    cursor = conn.cursor()

    cursor.execute(f'INSERT INTO coin_logs VALUES("{id}", "{user_id}", "{status}", "{bet}", "{datetime.datetime.now()}")')
    conn.commit()

    cursor.execute(f'SELECT * FROM coin_stats WHERE user_id = "{user_id}"')
    stats = cursor.fetchall()

    if len(stats) == 0:
        cursor.execute(f'INSERT INTO coin_stats VALUES("{user_id}", "0")')
        conn.commit()
    else:
        cursor.execute(f'UPDATE coin_stats SET money = {float(stats[0][1]) + float(bet)} WHERE user_id = "{user_id}"')
        conn.commit()

def insert_coin(id_games, player_1, player_2, player_1_rez, player_2_rez, bet, win_coin):
    conn, cursor = connect()

    cursor.execute(f'INSERT INTO coin_slep VALUES("{id_games}", "{player_1}", "{player_2}", "{player_1_rez}", "{player_2_rez}", "{bet}", "{win_coin}")')
    conn.commit()

async def roll_coin(bot, game, user_id):
    #coin_win = ["Орел", "Решка"]
    #coin = random.choice(coin_win)
    #games = Game(game)

    if User(user_id).spin_up == 'True':
        coin = random.choice([game.coin, game.coin, "Орел", "Решка"])

        if coin == "Орел":
            value = await bot.send_sticker(user_id, 'CAACAgIAAxkBAAEBuX1f6QABHoY_GtRbAv8hJkvfWrzw-XAAAloBAAIJfAMHeHoGbEl3DsweBA')
        elif coin == "Решка":
            value = await bot.send_sticker(user_id, 'CAACAgIAAxkBAAEBuXtf6QABFyc3BQ9wyyAlEfUieBckNyEAAlgBAAIJfAMHSLMhY7LA63UeBA')

        return coin, value.message_id
    else:
        coin_win = ["Орел", "Решка"]
        coin = random.choice(coin_win)

        if coin == "Орел":
            value = await bot.send_sticker(user_id, 'CAACAgIAAxkBAAEBuX1f6QABHoY_GtRbAv8hJkvfWrzw-XAAAloBAAIJfAMHeHoGbEl3DsweBA')
        elif coin == "Решка":
            value = await bot.send_sticker(user_id, 'CAACAgIAAxkBAAEBuXtf6QABFyc3BQ9wyyAlEfUieBckNyEAAlgBAAIJfAMHSLMhY7LA63UeBA')

        return coin, value.message_id

async def start_coin(bot, game, chat_id):
    await bot.send_message(chat_id=chat_id, text='❕ подкидываем монету...')
    games = Game(game)

    value_сoin_1 = await roll_coin(bot, game, chat_id)
    value_coin_2 =  await roll_coin(bot, game, game.user_id)

    insert_coin(game.id_game, game.user_id, chat_id, value_сoin_1[0], value_coin_2[0], int(game.bet), game.coin)
    game.del_game()

    while str(value_сoin_1[0]) == str(check_coin(game.id_game)[6]) and str(value_coin_2[0]) == str(check_coin(game.id_game)[6]) or str(value_сoin_1[0]) == str(value_coin_2[0]):
        await bot.send_message(chat_id=chat_id, text='❕ Противник подкидывает монетку...')
        await bot.forward_message(chat_id=chat_id, from_chat_id=game.user_id, message_id=value_coin_2[1])
        await bot.send_message(chat_id=chat_id, text='🔵Ничья!!!\n\nПерекидываем монетку...')

        await bot.send_message(chat_id=game.user_id, text='❕ Противник подкидывает монетку...')
        await bot.forward_message(chat_id=game.user_id, from_chat_id=chat_id, message_id=value_сoin_1[1])
        await bot.send_message(chat_id=game.user_id, text='🔵Ничья!!!\n\nПерекидываем монетку...')
        value_сoin_1 = await roll_coin(bot, game, chat_id)
        value_coin_2 =  await roll_coin(bot, game, game.user_id)
        insert_coin(game.id_game, game.user_id, chat_id, value_сoin_1[0], value_coin_2[0], int(game.bet), game.coin)
        game.del_game()

    return value_сoin_1, value_coin_2


async def main_start(game, bot, chat_id):
    

    value_сoin_1, value_coin_2 = await start_coin(bot, game, chat_id)

    info = start_game_coin(chat_id, game, value_сoin_1, value_coin_2)
    del_games(game.id_game)
    from_chat_id = lambda i: 1 if i == 0 else 0 if i == 1 else 100

    for i in range(2):
        await bot.send_message(chat_id=info[0][i], text='❕ Противник подкидывает монетку...')
        #bot.forward_message(chat_id=info[0][i], from_chat_id=info[0][from_chat_id(i)], message_id=info[2][i])
        await bot.send_message(chat_id=info[0][i], text=info[1][i])



def my_games_cancel(user_id):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM coin WHERE user_id = "{user_id}"')
    games = cursor.fetchall()
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in games:
        markup.add(
            types.InlineKeyboardButton(text=f'🌀 Game_{i[0]}| {i[2]} ₽',callback_data=f'games_coin:{i[0]}'))

    return markup

def get_info_games(code):
    conn, cursor = connect()
    
    cursor.execute(f'SELECT * FROM coin WHERE id_game = "{code}"')
    info = cursor.fetchone()

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add( 
        types.InlineKeyboardButton(text=f'Удалить', callback_data=f'coin_del:{code}'),
        types.InlineKeyboardButton(text=f'Выйти', callback_data=f'back_dice'),
    )

    msg = f"""
Игра: #Game_{info[0]}

🆔 ID: {info[1]}

🕹 Link: @{User(info[1]).username}

💰 SUM: {info[2]} RUB

    """

    return msg, markup

def delete_game(id_game):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM coin WHERE id_game = "{id_game}"')
    info = cursor.fetchone()

    User(info[1]).update_balance(info[2])

    cursor.execute(f'DELETE FROM coin WHERE id_game = "{id_game}"')
    conn.commit()