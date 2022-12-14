from aiogram import types
from utils.user import User
#from utils.Admin import *
from utils.mydb import *

# import sqlite3
import random
import datetime
import config


game_help_text = """
На данный момент пользователи сыграли %d игр на сумму %d рублей.
"""

game_profile_text = """
🧟‍♂ id: %s
💰 Баланс: %s

📊 Статистика:

➖ Игры: %s
➖ Победы: %s
➖ Прогрыши: %s
"""

game_info_text = """
🀄️ 21 Очко #%s
Ставка: %s RUB

Создал: <a href="t.me/%s">%s</a>
"""

game_play_text = """
ℹ️ Количество карт: %s

🔄 Количество очков: %s
"""

game_info_join_text = """
✅ <a href="t.me/%s">%s</a> присоединился к #%s, ожидайте свой ход.
"""

game_info_end_play = """
✔️ <a href="t.me/%s">%s</a> закончил играть и у него %s карт, банкуй
"""

game_info_win = """
⚔️ <a href="t.me/%s">%s</a>: %s VS <a href="t.me/%s">%s</a>: %s

🎉 Победитель: <a href="t.me/%s">%s</a>
💰 Выиграл: %sр
"""


class Game:
    def __init__(self):
        self.game_id = None
        self.user_id1 = None
        self.user_id2 = None
        self.score_user1 = None
        self.score_user2 = None
        self.status = None
        self.bet = None
        self.amount_card_user1 = None
        self.amount_card_user2 = None

    async def get_main_menu(self):
        markup = types.InlineKeyboardMarkup(row_width=2)

        markup.add(
            types.InlineKeyboardButton(text='✔️ Создать игру', callback_data='create_game:bj'), 
            types.InlineKeyboardButton(text='♻️ Обновить', callback_data='reload:bj'),
        )
        markup = await self.get_game_btns(markup)
        markup.add(
            types.InlineKeyboardButton(text='🗂 Мои игры', callback_data='my_games:bj'),
        )

        return markup

    @staticmethod
    async def get_game_btns(markup):
        conn, cursor = connect()

        cursor.execute(f'SELECT * FROM blackjack WHERE status = "wait"')
        games = cursor.fetchall()

        for i in games:
            markup.add(
                types.InlineKeyboardButton(text=f'🀄️ #{i[0]} | Сумма {i[6]}р', callback_data=f'21_points:{i[0]}'),
            )

        return markup

    async def get_text_help(self):
        amount_games = await self.get_amount_games()
        sum_all_games = await self.get_sum_all_games()

        text = game_help_text % (amount_games, sum_all_games)

        return text

    @staticmethod
    async def get_all_games():
        conn, cursor = connect()

        cursor.execute(f'SELECT * FROM bj_logs')
        games = cursor.fetchall()

        return games

    async def get_sum_all_games(self):
        games = await self.get_all_games()

        sum_all_games = 0

        for i in range(len(games)):
            if i % 2 == 0:
                sum_all_games += float(games[i][6])

        return sum_all_games

    async def get_amount_games(self):
        games = await self.get_all_games()

        return len(games)

    async def get_text_profile(self, user_id):
        balance = User(user_id).balance

        user = User(user_id)
        user.get_stats()

        text = game_profile_text % (user_id, balance, user.amount_games, user.amount_win_games, user.amount_lose_games)

        return text

    @staticmethod
    async def get_user_games(user_id):
        conn, cursor = connect()

        cursor.execute(f'SELECT * FROM bj_logs WHERE user_id1 = "%s" OR user_id2 = "%s"' % (user_id, user_id))
        games = cursor.fetchall()

        return games

    @staticmethod
    async def get_list_stats():
        conn, cursor = connect()

        cursor.execute(f'SELECT * FROM bj_stats')
        users = cursor.fetchall()

        return users

    async def get_menu_top(self):
        users = await self.get_list_stats()

        users.sort(key=lambda x: int(x[3]), reverse=True)

        markup = types.InlineKeyboardMarkup(row_width=2)

        amount = 0

        for i in users:
            amount += 1

            markup.add(
                types.InlineKeyboardButton(text='ℹ️ %s |🕹 %s |🏆 %s |☹️ %s' % (User(i[0]).first_name, i[3], i[6], i[7]),
                                           url='t.me/%s' % User(i[0]).username)
            )

            if amount >= 10:
                break

        return markup

    @staticmethod
    async def create_game(user_id, bet):
        conn, cursor = connect()

        user = User(user_id)

        if user.balance >= bet:
            user.update_balance(-bet)

            game_id = random.randint(11111111, 99999999)

            cursor.execute('INSERT INTO blackjack VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (game_id, user_id, 0, 0, 0, 'wait', bet, 0, 0))
            conn.commit()
            return True
        else:
            return False

    async def get_info_game(self, game_id):
        conn, cursor = connect()

        cursor.execute(f'SELECT * FROM blackjack WHERE game_id = "%s"' % game_id)
        game = cursor.fetchone()

        a = [0, 1, 2, 3, 4, 5, 6, 7, 8]
        self.game_id, self.user_id1, self.user_id2, self.score_user1, self.score_user2, self.status, self.bet, \
        self.amount_card_user1, self.amount_card_user2 = a

    async def get_game_info_text(self, game_id):
        await self.get_info_game(game_id)

        user = User(self.user_id1)

        text = game_info_text % (self.game_id, self.bet, user.username, user.first_name)

        return text

    @staticmethod
    async def get_game_info_menu(game_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(text='🀄️ Играть', callback_data=f'21_points_play:{game_id}'),
            types.InlineKeyboardButton(text='Назад', callback_data='back_dice'),
        )

        return markup

    async def play_21_points(self, bot, user_id, game_id):
        await self.get_info_game(game_id)

        if self.user_id1 == user_id:
            await bot.send_message(chat_id=user_id, text='Нельзя играть с самим собой')
        else:
            user = User(user_id)

            if user.balance >= self.bet:
                if self.status == 'wait':
                    user.update_balance(-self.bet)

                    await self.change_status(game_id, 'play:2')
                    await self.change_2player(game_id, user_id)

                    await self.send_play_message(bot, user_id, game_id)

                    text = game_info_join_text % (user.username, user.first_name, game_id)

                    try:
                        await bot.send_message(chat_id=self.user_id1, text=text, disable_web_page_preview=True)
                    except:
                        pass
            else:
                try:
                    await bot.send_message(chat_id=user_id, text='❕ Пополните баланс')
                except:
                    pass

    @staticmethod
    async def change_2player(game_id, user_id):
        conn, cursor = connect()

        cursor.execute(f'UPDATE blackjack SET user_id2 = "%s" WHERE game_id = "%s"' % (user_id, game_id))
        conn.commit()

    async def send_play_message(self, bot, user_id, game_id):
        user = User(user_id)

        text = await self.get_play_text(game_id, user_id)
        markup = await self.get_play_menu(game_id)

        try:
            await bot.send_message(chat_id=user_id, text=text, reply_markup=markup, disable_web_page_preview=True)
        except:
            pass

    async def get_play_text(self, game_id, user_id):
        await self.get_info_game(game_id)

        if user_id == self.user_id1:
            amount_card = self.amount_card_user1
            amount_score = self.score_user1
        else:
            amount_card = self.amount_card_user2
            amount_score = self.score_user2

        text = game_play_text % (amount_card, amount_score)

        return text

    @staticmethod
    async def get_play_menu(game_id):
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(text='➕ Взять еще карту', callback_data='21_points_take_card:%s' % game_id),
            types.InlineKeyboardButton(text='✔️ Хватит, вскрываемся', callback_data='21_points_open_up:%s' % game_id),
        )

        return markup

    @staticmethod
    async def change_status(game_id, status):
        conn, cursor = connect()

        cursor.execute(f'UPDATE blackjack SET status = "%s" WHERE game_id = "%s"' % (status, game_id))
        conn.commit()

    async def take_card(self, bot, user_id, game_id):
        await self.get_info_game(game_id)

        status = self.status.split(':')
        if status[0] == 'play':
            number_user = await self.get_number_user(user_id, game_id)
            if int(status[1]) == number_user:
                card = ['2', '3', '4', '10', '7', '8', '11']
                score = random.choice(card)

                await self.update_info_game(game_id, score, number_user)

                await self.send_play_message(bot, user_id, game_id)

    @staticmethod
    async def update_info_game(game_id, score, number_user):
        conn, cursor = connect()

        cursor.execute(f'UPDATE blackjack SET score_user%s = score_user%s + %s, amount_card_user%s = amount_card_user%s + 1 WHERE game_id = "%s"' % (
            number_user,
            number_user,
            score,
            number_user,
            number_user,
            game_id))
        conn.commit()

    async def get_number_user(self, user_id, game_id):
        await self.get_info_game(game_id)

        if self.user_id1 == user_id:
            return 1
        else:
            return 2

    async def open_up(self, bot, user_id, game_id):
        await self.get_info_game(game_id)

        status = self.status.split(':')

        if status[0] == 'play':
            number_user = await self.get_number_user(user_id, game_id)

            if int(status[1]) == number_user:

                if number_user == 1:
                    await self.change_status(game_id, 'end')

                    await self.end_game(bot, game_id)
                else:
                    await self.change_status(game_id, 'play:1')

                    user = User(self.user_id2)

                    text = game_info_end_play % (user.username, user.first_name, self.amount_card_user2)

                    try:
                        await bot.send_message(chat_id=self.user_id1, text=text, disable_web_page_preview=True,)
                    except:
                        pass

                    try:
                        await bot.send_message(chat_id=self.user_id2, text='✅ Ожидайте окончания игры.')
                    except:
                        pass

                    await self.send_play_message(bot, self.user_id1, game_id)

    async def end_game(self, bot, game_id):
        await self.get_info_game(game_id)

        win_money = self.bet * 2 / 100 * (100 - float(config.config('commission_percent')))

        info_profit_log = f'%s VS %s:21_points' % (self.user_id1, self.user_id2)

        #await Admin().write_profit_log(info_profit_log, self.bet * 2, config.config('commission_percent'))
        await self.write_game_logs(game_id)

        user1 = User(self.user_id1)
        user2 = User(self.user_id2)

        if self.score_user2 == self.amount_card_user1 or self.score_user1 > 21 and self.score_user2 > 21:
            win_user_id = 'БАНКИР'
            win_username = config.config('bot_login')

            user1.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)
            user2.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)

        elif self.score_user2 == 21:
            win_user_id = user2.user_id
            win_username = user2.username

            user2.update_stats(win_money=win_money, amount_games=1, amount_win_games=1)
            user1.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)

            user2.update_balance(win_money)
        elif self.score_user1 == 21:
            win_user_id = user1.user_id
            win_username = user1.username

            user1.update_stats(win_money=win_money, amount_games=1, amount_win_games=1)
            user2.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)

            user1.update_balance(win_money)
        elif self.score_user2 > 21:
            win_user_id = user1.user_id
            win_username = user1.username

            user1.update_stats(win_money=win_money, amount_games=1, amount_win_games=1)
            user2.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)

            user1.update_balance(win_money)
        elif self.score_user1 > 21:
            win_user_id = user2.user_id
            win_username = user2.username

            user2.update_stats(win_money=win_money, amount_games=1, amount_win_games=1)
            user1.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)

            user2.update_balance(win_money)
        elif self.score_user1 > self.score_user2:
            win_user_id = user1.user_id
            win_username = user1.username

            user1.update_stats(win_money=win_money, amount_games=1, amount_win_games=1)
            user2.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)

            user1.update_balance(win_money)
        elif self.score_user1 < self.score_user2:
            win_user_id = user2.user_id
            win_username = user2.username

            user2.update_stats(win_money=win_money, amount_games=1, amount_win_games=1)
            user1.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)

            user2.update_balance(win_money)
        else:
            win_user_id = 'БАНКИР'
            win_username = config.config('bot_login')

            user1.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)
            user2.update_stats(lose_money=self.bet, amount_games=1, amount_lose_games=1)

        text = game_info_win % (
            user1.username,
            user1.user_id,
            self.score_user1,
            user2.username,
            user2.user_id,
            self.score_user2,
            win_username,
            win_user_id,
            win_money
        )
        for i in [self.user_id1, self.user_id2]:
            try:
                await bot.send_message(chat_id=i, text=text, disable_web_page_preview=True)
            except Exception as e:
                pass


    async def write_game_logs(self, game_id):
        conn, cursor = connect()

        await self.get_info_game(game_id)

        cursor.execute('INSERT INTO bj_logs VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")' % (self.game_id,
                                                                                                                self.user_id1,
                                                                                                                self.user_id2,
                                                                                                                self.score_user1,
                                                                                                                self.score_user2,
                                                                                                                self.status,
                                                                                                                self.bet,
                                                                                                                self.amount_card_user1,
                                                                                                                self.amount_card_user2))
        conn.commit()

    async def get_my_games_menu(self, user_id):
        games = await self.get_user_games(user_id)

        markup = types.InlineKeyboardMarkup(row_width=2)

        for i in games:
            markup.add(
                types.InlineKeyboardButton(text=f'Сумма: {i[6]}р | Статус: {i[5]}', callback_data='my_games'),
            )

        markup.add(types.InlineKeyboardButton(text='⬅️ Назад', callback_data='back_dice'))

        return markup
