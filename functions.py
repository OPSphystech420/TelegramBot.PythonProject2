import datetime
import json
import random
import time

import requests
from aiogram import types

import config
import keyboard as menu
import message as m
from utils.mydb import *
from utils.user import User

buy_dict = {}


class Buy:
    def __init__(self, user_id):
        self.user_id = user_id
        self.product_code = None


async def first_join(user_id, first_name, username, code, bot):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    row = cursor.fetchall()
    who_invite = code[7:]

    if who_invite == '':
        who_invite = 0

    if len(row) == 0:
        users = [f'{user_id}', f'{first_name}', f'{username}', '0', 'False', f'{who_invite}',
                 f'{datetime.datetime.now()}', 'no']
        cursor.execute(f'INSERT INTO users VALUES (?,?,?,?,?,?,?,?)', users)
        conn.commit()

        cursor.execute(f'INSERT INTO bj_stats VALUES("{user_id}", "0", "0", "0", "0", "0", "0", "0")')
        conn.commit()

        #        if who_invite != 0:
        #            try:
        #                check_in_bd(User(who_invite).update_balance(config.config('ref_reward')))
        #           except Exception as e:
        #               print(e)
        #
        return True, who_invite

    return False, 0


def check_in_bd(user_id):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    row = cursor.fetchall()

    if len(row) == 0:
        return False
    else:
        return True


def replenish_balance(user_id):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM check_payment WHERE user_id = "{user_id}"')

    code = user_id
    cursor.execute(f'INSERT INTO check_payment VALUES ("{user_id}", "{code}", "0")')
    conn.commit()

    msg = m.pay_qiwi.format(
        number=config.config("qiwi_number"),
        code=code,
    )
    url = f'https://qiwi.com/payment/form/99?extra%5B%27account%27%5D={config.config("qiwi_number")}&amountFraction=0&extra%5B%27comment%27%5D={code}&currency=643&&blocked[0]=account&&blocked[1]=comment'

    markup = menu.payment_menu(url)

    return msg, markup


def check_payment(user_id):
    try:
        conn, cursor = connect()

        session = requests.Session()
        session.headers['authorization'] = 'Bearer ' + config.config("qiwi_token")
        parameters = {'rows': '10'}
        h = session.get(
            'https://edge.qiwi.com/payment-history/v1/persons/{}/payments'.format(config.config("qiwi_number")),
            params=parameters)
        req = json.loads(h.text)

        cursor.execute(f'SELECT * FROM check_payment WHERE user_id = {user_id}')
        result = cursor.fetchone()
        comment = result[1]

        for i in range(len(req['data'])):
            if comment in str(req['data'][i]['comment']):
                if str(req['data'][i]['sum']['currency']) == '643':
                    User(user_id).update_balance(req["data"][i]["sum"]["amount"])

                    cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
                    conn.commit()

                    rub = req["data"][i]["sum"]["amount"]

                    try:
                        cursor.execute(
                            f'INSERT INTO deposit_logs VALUES ("{user_id}", "qiwi", "{rub}", '
                            f'"{datetime.datetime.now()}")')
                        conn.commit()
                    except:
                        pass

                    return 1, req["data"][i]["sum"]["amount"]

    except Exception as e:
        print(e)

    return 0, 0


def cancel_payment(user_id):
    conn, cursor = connect()

    cursor.execute(f'DELETE FROM check_payment WHERE user_id = "{user_id}"')
    conn.commit()


def profile(user_id):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    row = cursor.fetchone()

    return row


def admin_info():
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM users')
    row = cursor.fetchall()

    d = datetime.timedelta(days=1)
    h = datetime.timedelta(hours=1)
    date = datetime.datetime.now()

    amount_user_all = 0
    amount_user_day = 0
    amount_user_hour = 0

    for i in row:
        amount_user_all += 1

        if date - datetime.datetime.fromisoformat(i[6]) <= d:
            amount_user_day += 1
        if date - datetime.datetime.fromisoformat(i[6]) <= h:
            amount_user_hour += 1

    cursor.execute(f'SELECT * FROM deposit_logs')
    row = cursor.fetchall()

    qiwi = 0
    all_qiwi = 0
    btc = 0
    all_btc = 0
    p2p = 0
    all_p2p = 0

    for i in row:
        if i[1] == 'qiwi':
            if date - datetime.datetime.fromisoformat(i[3]) <= d:
                qiwi += i[2]

            all_qiwi += i[2]

            all_btc += i[2]
        elif i[1] == 'p2p':
            if date - datetime.datetime.fromisoformat(i[3]) <= d:
                p2p += i[2]

            all_p2p += i[2]

    cursor.execute(f'SELECT * FROM withdraw_logs')
    row = cursor.fetchall()

    withdraw = 0
    all_withdraw = 0

    for i in row:
        if date - datetime.datetime.fromisoformat(i[2]) <= d:
            withdraw += i[1]

        all_withdraw += i[1]

    msg = f"""
❕ Информаци о пользователях:

❕ За все время - <b>{amount_user_all}</b>
❕ За день - <b>{amount_user_day}</b>
❕ За час - <b>{amount_user_hour}</b>

❕ Пополнений за 24 часа
❕ QIWI: <b>{qiwi} ₽</b>
❕ P2P: <b>{p2p} ₽</b>

❕ Выводы за 24 часа
❕ <b>{withdraw} ₽</b>

⚠️ Ниже приведены данные за все время
❕ Пополнения QIWI: <b>{all_qiwi} ₽</b>
❕ Пополнения P2P: <b>{all_p2p} ₽</b>
❕ Выводы: <b>{all_withdraw} ₽</b>
"""

    return msg


def give_balance(balance, user_id):
    conn, cursor = connect()

    cursor.execute(f'UPDATE users SET balance = "{balance}" WHERE user_id = "{user_id}"')
    conn.commit()


def get_users_list():
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM users')
    users = cursor.fetchall()

    return users


def add_sending(info):
    conn, cursor = connect()
    
    sec = 60
    mm = sec
    hrs = sec * mm
    dd = hrs * 24
    const_date = info['date'].split(':')
    d = (int(const_date[0]) - int(time.strftime('%d', time.localtime()))) * dd
    h = (int(const_date[1]) - int(time.strftime('%H', time.localtime()))) * hrs
    m = (int(const_date[2]) - int(time.strftime('%M', time.localtime()))) * mm

    date = float(time.time()) + d + h + m

    cursor.execute(
        f'INSERT INTO sending VALUES ("{info["type_sending"]}", "{info["text"]}", "{info["photo"]}", "{date}")')
    conn.commit()


def sending_check():
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM sending')
    row = cursor.fetchall()

    for i in row:
        if float(i[3]) <= time.time():
            cursor.execute(f'DELETE FROM sending WHERE photo = "{i[2]}"')
            conn.commit()

            return i

    return False


async def check_user_data(bot, user_id):
    chat = await bot.get_chat(user_id)
    user = User(user_id)

    conn, cursor = connect()

    if user.username != f'{chat.username}':
        cursor.execute(f'UPDATE users SET username = "{chat.username}" WHERE user_id = "{user_id}"')
        conn.commit()
    if user.first_name != chat.first_name:
        cursor.execute(f'UPDATE users SET first_name = "{chat.first_name}" WHERE user_id = "{user_id}"')
        conn.commit()


def check_ref_code(user_id):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
    user = cursor.fetchone()

    try:
        if int(user[3]) == '':
            cursor.execute(f'UPDATE users SET who_invite = {user_id} WHERE user_id = "{user_id}"')
            conn.commit()
    except:
        cursor.execute(f'UPDATE users SET who_invite = {user_id} WHERE user_id = "{user_id}"')
        conn.commit()

    return user_id


def top_ref_invite(user_id):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM users WHERE who_invite = {user_id}')
    check = cursor.fetchall()

    return len(check)


def check_all_profit_user(user_id):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM ref_log WHERE user_id = "{user_id}"')
    user = cursor.fetchall()

    if len(user) == 0:
        return 0
    else:
        return user[0][1]


def days_stats_users(day):
    start = day
    days = str(datetime.datetime.today() - (datetime.datetime.strptime(start, '%Y-%m-%d'))).split()[0]
    return days


def cheked_days(day):
    if day.split(':')[0] == '0':
        return '0'
    else:
        return day

    cursor.execute('SELECT * FROM btc_list')
    btc_list = cursor.fetchall()

    return btc_list


def witchdraw_qiwi(id_witchdraw, user_id, qiwi_number, summa):
    conn, cursor = connect()

    row = [id_witchdraw, user_id, qiwi_number, summa, datetime.datetime.now()]
    cursor.execute("INSERT INTO witchdraw (id_witchdraw, user_id, qiwi_number, summa, data) VALUES (?,?,?,?,?)", row)
    conn.commit()


def witchdraw_adm():
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM witchdraw')
    info = cursor.fetchall()
    markup = types.InlineKeyboardMarkup()
    for i in info:
        markup.add(types.InlineKeyboardButton(text=f'🌀 #Senior_{i[0]} | {i[3]} ₽', callback_data=f'witch_{i[0]}'))

    return markup


def get_info_withdraw(code):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM witchdraw WHERE id_witchdraw = "{code}"')
    info = cursor.fetchone()

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text=f'Удалить', callback_data=f'withdraw_del:{code}'),
        types.InlineKeyboardButton(text=f'Выйти', callback_data=f'to_close'),
    )

    msg = f"""
<b>Вывод:</b> #Senior_{info[0]}

<b>🆔 ID:</b> {info[1]}

<b>🕹 Link:</b> @{profile((info[1]))[1]}

<b>💳 Qiwi:</b> +{info[2]}

<b>💰 SUM:</b> {info[3]} RUB

<b>📆 DATE:</b> {info[4][:16]}
    """

    return msg, markup


def withdraw_del(id_with):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM witchdraw WHERE id_witchdraw = "{id_with}"')
    withdraw = cursor.fetchone()

    cursor.execute(f'DELETE FROM witchdraw WHERE id_witchdraw = "{id_with}"')
    conn.commit()

    cursor.execute(f'INSERT INTO withdraw_logs VALUES ("{withdraw[1]}", "{withdraw[3]}", "{datetime.datetime.now()}")')
    conn.commit()


def set_ban(user_id, value):
    conn, cursor = connect()

    cursor.execute(f'UPDATE users SET ban = "{value}" WHERE user_id = "{user_id}"')
    conn.commit()


def set_spinup(user_id, value):
    conn, cursor = connect()

    cursor.execute(f'UPDATE users SET spin_up = "{value}" WHERE user_id = "{user_id}"')
    conn.commit()


def update_balance(user_id, value):
    conn, cursor = connect()

    cursor.execute(f'UPDATE users SET balance = "{value}" WHERE user_id = "{user_id}"')
    conn.commit()


def btc_deposit(user_id, rub):
    conn, cursor = connect()
    cursor.execute(f'INSERT INTO deposit_logs VALUES ("{user_id}", "banker", "{rub}", "{datetime.datetime.now()}")')
    conn.commit()


def p2p_deposit(user_id, rub):
    conn, cursor = connect()
    cursor.execute(f'INSERT INTO deposit_logs VALUES ("{user_id}", "p2p", "{rub}", "{datetime.datetime.now()}")')
    conn.commit()


def promo_active():
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM promo')
    info = cursor.fetchall()
    markup = types.InlineKeyboardMarkup()
    for i in info:
        markup.add(types.InlineKeyboardButton(text=f'🎁 {i[1]}| Kol: {i[2]} | {i[3]} ₽', callback_data=f'promo_{i[0]}'))

    return markup


def get_info_promo(code):
    conn, cursor = connect()

    info = cursor.execute(f'SELECT * FROM promo WHERE id_promo = "{code}"').fetchone()

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(text='Выйти', callback_data='to_close'),
    )

    msg = f"""
<b>🕹 ID PROMO:</b> {info[0]}

<b>🕹 Название:</b> {info[1]}

<b>🔗 Активаций:</b> {info[2]}

<b>💰 Награда:</b> {info[3]} RUB

    """

    return msg, markup


def promo_del(code):
    conn, cursor = connect()

    cursor.execute(f'DELETE FROM promo WHERE name = "{code}"')
    conn.commit()


def check_in_promo(code):
    conn, cursor = connect()

    cursor.execute(f'SELECT * FROM promo WHERE name = "{code}"')
    row = cursor.fetchall()

    if len(row) == 0:
        return False
    else:
        return True


def add_promo(name, money, amount):
    conn, cursor = connect()

    promo = [random.randint(111, 999), name, amount, money, "0,"]
    cursor.execute(f'INSERT INTO promo VALUES (?,?,?,?,?)', promo)
    conn.commit()


def get_info_promo(promo):
    conn, cursor = connect()

    promo_info = cursor.execute(f'SELECT * FROM promo WHERE name = "{promo}"').fetchone()

    return promo_info


def activate_promo(user_id, promo):
    conn, cursor = connect()
    info = cursor.execute(f'SELECT * FROM promo WHERE name = "{promo}"').fetchone()

    users = f"{info[4]}{user_id},"
    cursor.execute(f'UPDATE promo SET amount = amount - 1, user_list = "{users}" WHERE name = "{promo}"')
    conn.commit()
