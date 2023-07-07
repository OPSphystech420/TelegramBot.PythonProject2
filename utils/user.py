from utils.mydb import *

import config


class User():
    
    def __init__(self, user_id=None, username=None):
        if username != None:
            conn, cursor = connect()

            cursor.execute(f'SELECT * FROM users WHERE username = "{username}"')
            user = cursor.fetchone()

            if user != None:
                user_id = user[0]
            else:
                self.user_id = None
                return

        conn, cursor = connect()
        cursor.execute(f'SELECT * FROM users WHERE user_id = "{user_id}"')
        user = cursor.fetchone()

        self.user_id = user[0]
        self.first_name = user[1]
        self.username = user[2]
        self.balance = user[3]
        self.spin_up = user[4]
        self.who_invite = user[5]
        self.date = user[6]
        self.ban = user[7]


    def update_balance(self, value):
        conn, cursor = connect()
        cursor.execute(f'UPDATE users SET balance = {float(self.balance) + float(value)} WHERE user_id = "{self.user_id}"')
        conn.commit()

        return True


    def give_ref_reward(self, money):
        conn, cursor = connect()

        if self.who_invite != '0':
            User(self.who_invite).update_balance(float(float(money) / 100 * float(config.config("ref_percent"))))

            cursor.execute(f'SELECT * FROM stats WHERE user_id = "{self.who_invite}"')
            user = cursor.fetchall()

            if len(user) == 0:
                cursor.execute(f'INSERT INTO stats VALUES("{self.who_invite}", "0", "1", "{config.config("ref_reward")}")')
                conn.commit()
            else:
                if user[0][2] == None or user[0][3] == None:
                    cursor.execute(f'UPDATE stats SET ref_profit = 0 WHERE user_id = "{self.who_invite}"')
                    conn.commit()

                    cursor.execute(f'UPDATE stats SET ref_amount = 0 WHERE user_id = "{self.who_invite}"')
                    conn.commit()

                    cursor.execute(f'SELECT * FROM stats WHERE user_id = "{self.who_invite}"')
                    user = cursor.fetchall()

                cursor.execute(
                    f'UPDATE stats SET ref_profit = {float(user[0][3]) + float(float(money) / 100 * float(config.config("ref_percent")))} WHERE user_id = "{self.who_invite}"')
                conn.commit()

    def get_stats(self):
        conn, cursor = connect()

        cursor.execute(f'SELECT * FROM bj_stats WHERE user_id = "{self.user_id}"')
        user = cursor.fetchone()

        self.ref_profit = float(user[1])
        self.ref_amount = int(user[2])
        self.amount_games = int(user[3])
        self.lose_money = float(user[4])
        self.win_money = float(user[5])
        self.amount_win_games = int(user[6])
        self.amount_lose_games = int(user[7])

    def update_stats(self, ref_profit=0, ref_amount=0, amount_games=0, lose_money=0, win_money=0, amount_win_games=0,
                     amount_lose_games=0):
        conn, cursor = connect()

        cursor.execute("""
UPDATE bj_stats SET ref_profit = ref_profit + %s, 
                 ref_amount = ref_amount + %s, 
                 amount_games = amount_games + %s,
                 lose_money = lose_money + %s,
                 win_money = win_money + %s,
                 amount_win_games = amount_win_games + %s,
                 amount_lose_games = amount_lose_games + %s WHERE user_id = "%s" """ % (ref_profit,
                                                                                        ref_amount,
                                                                                        amount_games,
                                                                                        lose_money,
                                                                                        win_money,
                                                                                        amount_win_games,
                                                                                        amount_lose_games,
                                                                                        self.user_id))

        conn.commit()
