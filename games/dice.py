from aiogram import types
from utils.user import User
from utils.mydb import *
import functions as func
import sqlite3
import random
import datetime
import config
import time

my_games_txt = """
🃏 Мои игры: {}

💖 Выигрыш: {} RUB
💔 Проигрыш: {} RUB
📊 Профит: {} RUB

Данные приведены за все время
"""

raiting_txt = """
📊 ТОП 5 игроков Dice:

🥇  1 место: <b>{}</b> | {} RUB

🥈 2 место: <b>{}</b> | {} RUB

🥉 3 место: <b>{}</b> | {} RUB

🏅 4 место: <b>{}</b> | {} RUB

🏅 5 место: <b>{}</b> | {} RUB

🏆 Ваше место в рейтинге: {} из {} ({} RUB)

Рейтинг обновляется каждые 5 минут.
"""


dice_game_info_txt = """
{} #Game_{}
💰 Ставка: {} RUB
 
🧑🏻‍💻 1 игрок: @{}
"""


dice_game_result_txt = """
🎲Кости #{}
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

        cursor.execute(f'SELECT * FROM dice WHERE id = "{code}"')
        info = cursor.fetchall()

        if len(info) == 0:
            self.status = False
        else:
            self.status = True

            self.id_game = info[0][0]
            self.game = info[0][1]
            self.user_id = info[0][2]
            self.bet = float(info[0][3])

    def del_game(self):
        conn, cursor = connect()

        cursor.execute(f'DELETE FROM dice WHERE id = "{self.id_game}"')
        conn.commit()


def dice_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='Создать игру', callback_data='create:dice'),
        types.InlineKeyboardButton(text='Обновить', callback_data='reload:dice'),
    )

    markup = get_games_menu(markup)

    markup.add(
        types.InlineKeyboardButton(text='📝Мои игры', callback_data='my_games:')
    )

    return markup

def game_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='🎲 Кубик', callback_data='🎲'),
        types.InlineKeyboardButton(text='🎯 Дартс', callback_data='🎯'),
        types.InlineKeyboardButton(text='🏀 Баскетбол', callback_data='🏀'),
        types.InlineKeyboardButton(text='🎳 Боулинг', callback_data='🎳'),
        types.InlineKeyboardButton(text='⚽️ Футбол', callback_data='⚽️'),
    )

    return markup

def get_games_menu(markup):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM dice')
    games = cursor.fetchall()

    for i in games:
        markup.add(types.InlineKeyboardButton(text=f'{i[1]} #Game_{i[0]} | {i[3]} RUB', callback_data=f'dice_game:{i[0]}'))

    return markup


def cancel_dice():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='❌', callback_data='cancel_dice')
    )

    return markup


def back_dice():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton(text='⬅️Назад', callback_data='back_dice')
    )

    return markup


def create_game(game, user_id, id_game,  bet):
    conn, cursor = connect()

    game = [f"{id_game}", f"{game}", f"{user_id}", f"{bet}"]
    cursor.execute(f'INSERT INTO dice VALUES(?,?,?,?)', game)
    conn.commit()


def my_games(user_id):
    conn = sqlite3.connect('database/logs.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM dice_logs WHERE user_id = "{user_id}"')
    games = cursor.fetchall()

    amount_games = len(games)

    win_money = 0
    lose_money = 0

    if len(games) < int(10000):
        amount = len(games)
    else:
        amount = int(10000)


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


def rating_dice(user_id):
    conn = sqlite3.connect('database/logs.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT * FROM dice_stats WHERE user_id = "{user_id}"')
    user = cursor.fetchall()

    if len(user) == 0:
        cursor.execute(f'INSERT INTO dice_stats VALUES("{user_id}", "0")')
        conn.commit()

        user_money = 0
    else:
        user_money = user[0][1]

    cursor.execute(f'SELECT * FROM dice_stats')
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
        '{:.2f}'.format(games[0][1]),
        func.profile(games[1][0])[1],
        '{:.2f}'.format(games[1][1]),
        func.profile(games[2][0])[1],
        '{:.2f}'.format(games[2][1]),
        func.profile(games[3][0])[1],
        '{:.2f}'.format(games[3][1]),
        func.profile(games[4][0])[1],
        '{:.2f}'.format(games[4][1]),
        user_top,
        size_top,
        user_money
    )

    return msg


def dice_game(code):
    game = Game(code)

    if game.status == False:
        return False
    else:
        msg = dice_game_info_txt.format(
            game.game,
            game.id_game,
            game.bet,
            User(game.user_id).username
        )

        msg += f'🧑🏻‍💻 2 Игрок: Ожидание...'

        markup = types.InlineKeyboardMarkup(row_width=1)


        markup.add(
            types.InlineKeyboardButton(text='🕹 Бросить 🕹', callback_data=f'start_game_dice:{game.id_game}'),
            types.InlineKeyboardButton(text='⬅️ Назад', callback_data=f'back_dice')
        )

        return msg, markup


def start_game_dice(user_id, game, value_dice1, value_dice2):
    user = User(user_id)

    user.update_balance(-game.bet)
    user = User(user_id)

    value_dice1 = value_dice1
    value_dice2 = value_dice2

    win_money = ((game.bet * 2) / 100) * (100 - float(config.config('commission_percent')))
    profit_money = ((game.bet * 2) / 100) * float(config.config('commission_percent'))

    if value_dice1[0] > value_dice2[0]:
        user.update_balance(win_money)

        dice_write_game_log(game.id_game, user_id, 'win', win_money)
        dice_write_game_log(game.id_game, game.user_id, 'lose', win_money)

        status1 = '✅ Поздравляем с победой!'
        status2 = '🔴 Вы проиграли!'

    elif value_dice1[0] < value_dice2[0]:
        User(game.user_id).update_balance(win_money)

        dice_write_game_log(game.id_game, game.user_id, 'win', win_money)
        dice_write_game_log(game.id_game, user_id, 'lose', win_money)

        status1 = '🔴 Вы проиграли!'
        status2 = '✅ Поздравляем с победой!'


    try:
        conn = sqlite3.connect('database/database.db')
        cursor = conn.cursor()

        msg = f"{user_id} | {game.user_id}"

        cursor.execute(f'INSERT INTO profit_dice VALUES ("{msg}", "{profit_money}", "{datetime.datetime.now()}")')
        conn.commit()
    except:
        pass

    msg1 = dice_game_result_txt.format(
        game.id_game,
        win_money,
        User(user_id).username,
        User(game.user_id).username,
        value_dice1[0],
        value_dice2[0],
        status1
    )

    msg2 = dice_game_result_txt.format(
        game.id_game,
        win_money,
        User(user_id).username,
        User(game.user_id).username,
        value_dice2[0],
        value_dice1[0],
        status2
    )

    return [user_id, game.user_id], [msg1, msg2], [value_dice2[1], value_dice1[1]]


def dice_write_game_log(id, user_id, status, bet):
    conn = sqlite3.connect('database/logs.db')
    cursor = conn.cursor()

    cursor.execute(f'INSERT INTO dice_logs VALUES("{id}", "{user_id}", "{status}", "{bet}", "{datetime.datetime.now()}")')
    conn.commit()

    cursor.execute(f'SELECT * FROM dice_stats WHERE user_id = "{user_id}"')
    stats = cursor.fetchall()

    if len(stats) == 0:
        cursor.execute(f'INSERT INTO dice_stats VALUES("{user_id}", "0")')
        conn.commit()
    else:
        cursor.execute(f'UPDATE dice_stats SET money = {float(stats[0][1]) + float(bet)} WHERE user_id = "{user_id}"')
        conn.commit()


def profit_logs(user_id, profit):
    conn, cursor = connect()

    cursor.execute(
        f'INSERT INTO profit_dice VALUES("{user_id}", "{profit}", "{datetime.datetime.now()}")')
    conn.commit()


async def roll_dice(bot, game, user_id):
    value = await bot.send_dice(user_id, emoji=game)

    return int(value.dice.value), value.message_id

async def spin_up(bot, game, user_id):
    if User(user_id).spin_up == 'True':
        value = await roll_dice(bot, game.game, user_id)
        while int(value[0]) < 5:
            value = await roll_dice(bot, game.game, user_id)

        return int(value[0]), value[1]
    else:
        value = await roll_dice(bot, game.game, user_id)
        return int(value[0]), value[1]

async def start_roll(bot, game, chat_id):
    await bot.send_message(chat_id=chat_id, text='❕ Бросаем эмоджи...')



    value1 = await spin_up(bot, game, chat_id)
    value2 = await spin_up(bot, game, game.user_id)


    if value1[0] == value2[0]:
        await bot.send_message(chat_id=chat_id, text='❕ Противник бросает эмоджи...')
        await bot.forward_message(chat_id=chat_id, from_chat_id=game.user_id, message_id=value2[1])
        await bot.send_message(chat_id=chat_id, text='🔹🔹 Ничья!!!')

        await bot.send_message(chat_id=game.user_id, text='❕ Противник бросает эмоджи...')
        await bot.forward_message(chat_id=game.user_id, from_chat_id=chat_id, message_id=value1[1])
        await bot.send_message(chat_id=game.user_id, text='🔹🔹 Ничья!!!')

        return await start_roll(bot, game, chat_id)
    else:
        return value1, value2


def check_win(value1, value2):
    if value1 > value2:
        return True
    else:
        return False


async def main_start(game, bot, chat_id):
    game.del_game()

    value_dice1, value_dice2 = await start_roll(bot, game, chat_id)

    info = start_game_dice(chat_id, game, value_dice1, value_dice2)

    from_chat_id = lambda i: 1 if i == 0 else 0 if i == 1 else 100

    for i in range(2):
        await bot.send_message(chat_id=info[0][i], text='❕ Противник бросает эмоджи...')
        await bot.forward_message(chat_id=info[0][i], from_chat_id=info[0][from_chat_id(i)], message_id=info[2][i])
        await bot.send_message(chat_id=info[0][i], text=info[1][i])


def get_list_users(game, user_id):
    user_list = [user_id]

    user_list.append(game.user_id)

    if game.user_id2 != '0':
        user_list.append(game.user_id2)
    if game.user_id3 != '0':
        user_list.append(game.user_id3)
    if game.user_id4 != '0':
        user_list.append(game.user_id4)

    return user_list


def my_games_cancel(user_id):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM dice WHERE user_id = "{user_id}"')
    games = cursor.fetchall()
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i in games:
        markup.add(
            types.InlineKeyboardButton(text=f'🌀 Game_{i[0]} {i[1]}| {i[3]} ₽',callback_data=f'games_user:{i[0]}'))

    return markup

def get_info_games(code):
    conn, cursor = connect()
    
    cursor.execute(f'SELECT * FROM dice WHERE id = "{code}"')
    info = cursor.fetchone()

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add( 
        types.InlineKeyboardButton(text=f'Удалить', callback_data=f'game_del:{code}'),
        types.InlineKeyboardButton(text=f'Выйти', callback_data=f'back_dice'),
    )

    msg = f"""
Игра: #Game_{info[0]}

🆔 ID: {info[2]}

🕹 Link: @{User(info[2]).username}

💰 SUM: {info[3]} RUB

    """

    return msg, markup

def delete_game(id_game):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM dice WHERE id = "{id_game}"')
    info = cursor.fetchone()

    User(info[2]).update_balance(info[3])

    cursor.execute(f'DELETE FROM dice WHERE id = "{id_game}"')
    conn.commit()