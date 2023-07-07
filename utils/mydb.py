import sqlite3


def connect():
    conn = sqlite3.connect("database/database.db")

    cursor = conn.cursor()

    return conn, cursor


conn, cursor = connect()


def create_tables():
    try:
        cursor.execute(
            f'CREATE TABLE users (user_id TEXT, first_name TEXT, username TEXT, balance DECIMAL(10, 2), spin_up TEXT, who_invite TEXT, date TEXT, ban TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE check_payment (user_id TEXT, code TEXT, referral_code TEXT)')
        conn.commit()
    except:
        pass
    try:

        cursor.execute(f'CREATE TABLE sending (type TEXT, text TEXT, photo TEXT, date TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE game_logs (id TEXT, user_id TEXT, status TEXT, bet DECIMAL(10, 2), date TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE stats (user_id TEXT, money DECIMAL(10, 2))')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE list (type TEXT, text TEXT, photo TEXT, date TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE deposit_logs (user_id TEXT, type TEXT, sum DECIMAL(10, 2), date TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE withdraw_logs (user_id TEXT, sum DECIMAL(10, 2), date TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE profit_logs (user_id TEXT, sum DECIMAL(10, 2), date TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            f'CREATE TABLE bj_logs (game_id TEXT, user_id1 TEXT, user_id2 TEXT, score_user1 INT, score_user2 INT, status TEXT, bet DECIMAL(10, 2), amount_card_user1 INT, amount_card_user2 INT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE basket (id TEXT, user_id TEXT, bet DECIMAL(10, 2))')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            f'CREATE TABLE bj_stats (user_id TEXT, ref_profit DECIMAL(10, 2), ref_amount INT, amount_games INT, lose_money DECIMAL(10, 2), win_money DECIMAL(10, 2), amount_win_games INT, amount_lose_games INT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            f'CREATE TABLE blackjack (game_id TEXT, user_id1 TEXT, user_id2 TEXT, score_user1 INT, score_user2 INT, status TEXT, bet DECIMAL(10, 2), amount_card_user1 INT, amount_card_user2 INT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE bowl (id TEXT, user_id TEXT, bet DECIMAL(10, 2))')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE coin (id_game TEXT, user_id TEXT, bet DECIMAL(10, 2), coin_win TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            f'CREATE TABLE coin_slep (id_game TEXT, player_1 TEXT, player_2 TEXT, player_1_rez TEXT, player_2_rez TEXT, bet TEXT, coin_win TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE dice (id TEXT, game TEXT, user_id TEXT, bet DECIMAL(10, 2))')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            f'CREATE TABLE promo (id_promo TEXT, name TEXT, amount INT, money DECIMAL(10, 2), user_list TEXT)')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(f'CREATE TABLE slots (id TEXT, user_id TEXT, bet DECIMAL(10, 2))')
        conn.commit()
    except:
        pass

    try:
        cursor.execute(
            f'CREATE TABLE witchdraw (id_witchdraw TEXT, user_id TEXT, qiwi_number TEXT, summa TEXT, data TEXT)')
        conn.commit()
    except:
        pass


create_tables()
