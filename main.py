import asyncio
import random
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

import functions as func
import games.coin as coin
import games.dice as dice
import games.slots as slots
import keyboard as menu
import message as m
import utils.p2p_pay as p2p
from filters.chat_filters import IsPrivate
from games.blackjack import Game as Bj
from states import *
from utils.logger import *
from utils.user import *

bot = Bot(token=config.config('bot_token'), parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# await func.check_user_data(bot, message.from_user.id)

@dp.message_handler(IsPrivate(), commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    try:
        some_var = await bot.get_chat_member(-858689638, msg.from_user.id)
        check = await func.first_join(user_id=msg.from_user.id, first_name=msg.from_user.first_name,
                                      username=msg.from_user.username, code=msg.text, bot=bot)
        if check[0] is True:
            await bot.send_message(chat_id=msg.from_user.id,
                                   text=f'<b>Добро пожаловать!\n\n</b>'
                                        f'<b>Я @END_RAID - моя цель сделать '
                                        f'игру между двумя игроками самой запоминающейся!\n</b>',
                                   reply_markup=menu.main_menu())
            await bot.send_message(config.config('admin_group'),
                                   f'Новый пользователь {msg.from_user.get_mention(as_html=True)}')
            if check[1] != 0:
                func.check_in_bd(User(check[1]).update_balance(config.config('ref_reward')))
                await bot.send_message(chat_id=check[1],
                                       text=f'За приглашение {User(msg.from_user.id).first_name} вам '
                                            f'начислено {config.config("ref_reward")} ₽')
                await bot.send_message(chat_id=config.config("admin_group"),
                                       text=f'{User(check[1]).first_name} пригласил '
                                            f'@{User(msg.from_user.id).username} {msg.from_user.id}')
        else:
            if User(msg.from_user.id).ban == 'no':
                await func.check_user_data(bot, msg.from_user.id)
                if some_var.status == 'member' or some_var.status == 'administrator' or some_var.status == 'creator':
                    await bot.send_message(chat_id=msg.from_user.id,
                                           text=f'{msg.from_user.first_name} рад видеть тебя снова!',
                                           reply_markup=menu.main_menu())
                else:
                    await msg.answer(f'Вы не вступили в наш чат!\n\n'
                                     f'Подпишитесь на него чтобы получить доступ к боту.\nИ снова нажмите 👉🏻 /start 👈🏻',
                                     reply_markup=menu.channel())
            else:
                pass
    except Exception as e:
        await bot.send_message(config.config('admin_group'), f'Пизда, старт наебнулся {e}')


@dp.message_handler(IsPrivate(), commands=['admin', 'a', 'админ'])
async def admin(message: types.Message):
    if str(message.from_user.id) in config.config('admin_id'):
        await message.answer(f'{message.from_user.get_mention(as_html=True)} че ты в админке забыл?',
                             reply_markup=menu.admin_menu())


@dp.message_handler(IsPrivate())
async def send_message(message: types.Message):
    chat_id = message.from_user.id

    try:
        if User(chat_id).ban == 'no':
            some_var = await bot.get_chat_member(-858689638, message.from_user.id)
            user_status = some_var.status
            if user_status == 'member' or user_status == 'administrator' or user_status == 'creator':

                if message.text == menu.main_menu_btn[0]:
                    try:
                        await bot.send_video(chat_id=chat_id,
                                             video=open('photos/games.mp4', 'rb'),
                                             caption=f'<b>💳 Баланс: {User(chat_id).balance} RUB\n</b>'
                                                     f'<b>🕹 Выберите игру:</b>',
                                             reply_markup=menu.games_menu())
                    except Exception as e:
                        logger.error(f'Error: {e}')
                        await message.answer('Ошибка! Пропиши /start')

                elif message.text == menu.main_menu_btn[2]:
                    await bot.send_video(
                        chat_id=chat_id,
                        video=open('photos/info.mp4', 'rb'),
                        caption='<b>Информация ниже:</b>',
                        reply_markup=menu.inform_menu())

                elif message.text == menu.main_menu_btn[1]:
                    await func.check_user_data(bot, message.from_user.id)
                    info = User(chat_id)
                    await bot.send_video(
                        chat_id=chat_id,
                        video=open('photos/cabinet.mp4', 'rb'),
                        caption=m.profile.format(
                            user_id=message.from_user.id,
                            name=message.from_user.get_mention(as_html=True),
                            data=func.cheked_days(func.days_stats_users(info.date[:10])),
                            balance=info.balance),
                        reply_markup=menu.profile())

                else:
                    await func.check_user_data(bot, message.from_user.id)
                    await message.answer('Я тебя не понимаю', reply_markup=menu.main_menu())
            else:
                await message.answer(f'Вы не вступили в наш чат!\n\n'
                                     f'Подпишитесь на него чтобы получить доступ к боту.\n\nИ '
                                     f'снова нажмите 👉🏻 /start 👈🏻',
                                     reply_markup=menu.channel())
        else:
            pass
    except Exception as e:
        logger.error(e)


@dp.callback_query_handler()
async def handler_call(call: types.CallbackQuery):
    chat_id = call.from_user.id
    message_id = call.message.message_id

    if User(chat_id).ban == 'no':

        if call.data == 'rating':
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id,
                                   text='Выберите какой игры вам показать рейтинг:',
                                   reply_markup=menu.rating())

        if call.data == 'payments':
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id,
                                   text='Выберите вариант пополнения:',
                                   reply_markup=menu.payments())

        if call.data == 'p2p':
            await PayP2P.amount.set()
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id, text='Введи сумму пополнения:')

        if 'p2p_check:' in call.data:
            bill_id = call.data.split(":")[1]
            pay = p2p.check_p2p(bill_id)
            if pay.status == 'PAID':
                func.p2p_deposit(chat_id, pay.amount)
                User(chat_id).update_balance(pay.amount)
                await bot.delete_message(chat_id, message_id)
                await bot.answer_callback_query(callback_query_id=call.id,
                                                text=f'✅ Оплата прошла\nСумма: {pay.amount} RUB')
                await bot.send_message(chat_id=chat_id, text=f'<b>Успешное пополнение:</b> + {pay.amount} RUB')
                await bot.send_message(chat_id=config.config('admin_group'),
                                       text=f'♻️ Пришло пополнение p2p Qiwi!\n\n'
                                            f'🧑🏻‍🔧 От: @{User(chat_id).username}\n\n'
                                            f'💰 Сумма: {pay.amount} RUB')
            else:
                await bot.answer_callback_query(callback_query_id=call.id,
                                                text=f'💢 Платеж не найден, попробуйте еще раз')

        if call.data == 'to_games':
            await bot.delete_message(chat_id, message_id)
            await bot.send_video(chat_id=chat_id,
                                 video=open('photos/games.mp4', 'rb'),
                                 caption=f'<b>💳 Баланс: {User(chat_id).balance} RUB\n</b>'
                                         f'<b>🕹 Выберите игру:</b>',
                                 reply_markup=menu.games_menu())

        if call.data == 'roll':
            await bot.delete_message(chat_id, message_id)
            with open('photos/games.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption=m.info_dice, reply_markup=dice.dice_menu())

        if call.data == 'slots':
            await bot.delete_message(chat_id, message_id)
            with open('photos/games.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption=m.info_slots, reply_markup=slots.slots_menu())

        if call.data == 'blackjack':
            await bot.delete_message(chat_id, message_id)
            with open('photos/games.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption='Доступные игры',
                                     reply_markup=await Bj().get_main_menu())

        if call.data == 'reload:Bj':
            await bot.delete_message(chat_id, message_id)
            with open('photos/games.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption='Доступные игры',
                                     reply_markup=await Bj().get_main_menu())

        if '21_points:' in call.data:
            await bot.send_message(chat_id=chat_id,
                                   text=await Bj().get_game_info_text(call.data.split(':')[1]),
                                   reply_markup=await Bj().get_game_info_menu(call.data.split(':')[1]),
                                   disable_web_page_preview=True)

        if '21_points_play' in call.data:
            await bot.delete_message(chat_id, message_id)
            await Bj().play_21_points(bot, str(chat_id), call.data.split(':')[1])

        if '21_points_take_card:' in call.data:
            await bot.delete_message(chat_id, message_id)
            await Bj().take_card(bot, str(chat_id), call.data.split(':')[1])

        if '21_points_open_up:' in call.data:
            await bot.delete_message(chat_id, message_id)
            await Bj().open_up(bot, str(chat_id), call.data.split(':')[1])

        if call.data == 'rating_blackjack':
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text='ℹ️ Имя |🕹 Игры |🏆 Победы |☹️ Проигрыши',
                                        reply_markup=await Bj().get_menu_top())

        if call.data == 'my_games:Bj':
            text = '♻️ Ваши игры:'
            markup = await Bj().get_my_games_menu(chat_id)
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

        if call.data == 'coin':
            await bot.delete_message(chat_id, message_id)
            with open('photos/games.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption=m.info_coin, reply_markup=coin.coin_menu())

        if call.data == 'reload:coin':
            await bot.delete_message(chat_id, message_id)
            with open('photos/games.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption=m.info_coin, reply_markup=coin.coin_menu())

        if call.data == 'reload:dice':
            await bot.delete_message(chat_id, message_id)
            with open('photos/games.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption=m.info_dice, reply_markup=dice.dice_menu())

        if call.data == 'reload:slots':
            await bot.delete_message(chat_id, message_id)
            with open('photos/games.jpg', 'rb') as photo:
                await bot.send_photo(chat_id=chat_id, photo=photo,
                                     caption=m.info_slots, reply_markup=slots.slots_menu())

        if call.data == 'create_game:Bj':
            await CreateBj.bet.set()
            await call.message.answer('<b>Введи сумму ставки:</b>')

        if call.data == 'create:coin':
            await CreateCoin.bet.set()
            await bot.send_message(chat_id=chat_id, text='<b>Введи сумму ставки:</b>', )

        if call.data == 'create:dice':
            await CreateDice.game.set()
            await bot.send_message(chat_id=chat_id,
                                   text='Выберите вид игры:', reply_markup=dice.game_menu())

        if call.data == 'create:slots':
            await CreateSlots.bet.set()
            await bot.send_message(chat_id=chat_id, text='<b>Введи сумму ставки:</b>')

        if call.data == 'my_games:':
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id,
                                   text=dice.my_games(chat_id),
                                   reply_markup=dice.my_games_cancel(chat_id))

        if call.data == 'my_games:coin':
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id,
                                   text=coin.my_games_coin(chat_id),
                                   reply_markup=coin.my_games_cancel(chat_id))

        if call.data == 'my_games:slots':
            info = slots.my_games_cancel(chat_id)
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id,
                                   text=slots.my_games(chat_id),
                                   reply_markup=info)

        if call.data == 'back_dice':
            await bot.delete_message(chat_id, message_id)

        if 'games_user:' in call.data:
            game_id = call.data.split(":")[1]
            i = dice.get_info_games(game_id)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=i[0], reply_markup=i[1])

        if 'games_coin:' in call.data:
            game_id = call.data.split(":")[1]
            i = coin.get_info_games(game_id)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=i[0], reply_markup=i[1])

        if 'coin_del:' in call.data:
            game_id = call.data.split(":")[1]
            game = coin.Game(call.data.split(':')[1])
            if game.status is True:
                coin.delete_game(game_id)
                await bot.delete_message(chat_id, message_id)
                await call.message.answer('Игра удалена!')
            else:
                await call.message.answer('Ига не найдена!')

        if 'games_slot:' in call.data:
            game_id = call.data.split(":")[1]
            i = slots.get_info_games(game_id)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=i[0], reply_markup=i[1])

        if 'game_slots_del:' in call.data:
            game_id = call.data.split(":")[1]
            game = slots.Game(call.data.split(':')[1])
            if game.status is True:
                slots.delete_game(game_id)
                await bot.delete_message(chat_id, message_id)
                await call.message.answer('Игра удалена!')
            else:
                await call.message.answer('Ига не найдена!')

        if 'game_del:' in call.data:
            game_id = call.data.split(":")[1]
            game = dice.Game(call.data.split(':')[1])
            if game.status is True:
                dice.delete_game(game_id)
                await bot.delete_message(chat_id, message_id)
                await call.message.answer('Игра удалена!')
            else:
                await call.message.answer('Ига не найдена!')

        if call.data == 'rating_dice':
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=dice.rating_dice(chat_id), reply_markup=menu.exit_to_info())

        if call.data == 'rating_rubl':
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=coin.rating_coin(chat_id), reply_markup=menu.exit_to_info())

        if call.data == 'rating_slots':
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                        text=slots.rating_dice(chat_id), reply_markup=menu.exit_to_info())

        if 'coin_game:' in call.data:
            game = coin.Game(call.data.split(':')[1])
            if game.status is True:
                if game.user_id != str(chat_id):
                    info = coin.coin_game(call.data.split(':')[1])
                    if info is False:
                        await bot.send_message(chat_id=chat_id, text='💢 Игра не найдена')
                    else:
                        await bot.send_message(chat_id=chat_id, text=info[0], reply_markup=info[1])
                else:
                    await bot.send_message(chat_id=chat_id, text='💢 Нельзя играть с самим собой')
            else:
                await bot.send_message(chat_id=chat_id, text='Игра не найдена')

        if 'start_game_coin:' in call.data:
            game = coin.Game(call.data.split(':')[1])
            if game.status is True:
                if game.user_id != str(chat_id):
                    if float(User(chat_id).balance) >= float(game.bet):
                        await coin.main_start(game, bot, chat_id)
                    else:
                        await bot.send_message(chat_id, '❌Для игры пополните баланс')
                else:
                    await bot.send_message(chat_id, '💢 Нельзя играть с самим собой!')
            else:
                await bot.send_message(chat_id, '💢 Игра не найдена')

        if 'dice_game:' in call.data:
            game = dice.Game(call.data.split(':')[1])
            if game.status is True and game.user_id != str(chat_id):
                info = dice.dice_game(call.data.split(':')[1])
                if info is False:
                    await bot.send_message(chat_id=chat_id, text='💢 Игра не найдена')
                else:
                    await bot.send_message(chat_id=chat_id, text=info[0], reply_markup=info[1])
            else:
                await bot.send_message(chat_id=chat_id, text='💢 Нельзя играть с самим собой')

        if 'start_game_dice:' in call.data:
            game = dice.Game(call.data.split(':')[1])
            if game.status is not False and game.user_id != str(chat_id):
                if User(chat_id).balance >= game.bet:
                    await dice.main_start(game, bot, chat_id)
                else:
                    await bot.send_message(chat_id=chat_id, text='💢 Для игры пополните баланс')
            else:
                await bot.send_message(chat_id=chat_id, text='💢 Игра не найдена!')

        if 'slots_game:' in call.data:
            game = slots.Game(call.data.split(':')[1])
            if game.status is True and game.user_id != str(chat_id):
                info = slots.slots_game(call.data.split(':')[1])
                if info is False:
                    await bot.send_message(chat_id=chat_id, text='💢 Игра не найдена')
                else:
                    await bot.send_message(chat_id=chat_id, text=info[0], reply_markup=info[1])
            else:
                await bot.send_message(chat_id=chat_id, text='💢 Нельзя играть с самим собой')

        if 'start_game_slots:' in call.data:
            game = slots.Game(call.data.split(':')[1])
            if game.status is not False and game.user_id != str(chat_id):
                if User(chat_id).balance >= game.bet:
                    await slots.main_start(game, bot, chat_id)
                else:
                    await bot.send_message(chat_id=chat_id, text='💢 Для игры пополните баланс')
            else:
                await bot.send_message(chat_id=chat_id, text='💢 Игра не найдена!')

        if call.data == 'to_profile':
            try:
                await bot.delete_message(chat_id, message_id)
                info = User(chat_id)
                await bot.send_video(
                    chat_id=chat_id,
                    video=open('photos/cabinet.mp4', 'rb'),
                    caption=m.profile.format(
                        user_id=call.message.chat.id,
                        name=call.message.from_user.get_mention(as_html=True),
                        data=func.cheked_days(func.days_stats_users(info.date[:10])),
                        balance=info.balance),
                    reply_markup=menu.profile())
            except Exception as e:
                logger.error(f'Error: {e}')
                await bot.send_message(chat_id, 'Ошибка! Введите /start')

        if call.data == 'refferal_web':
            ref_code = func.check_ref_code(chat_id)
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id,
                                   text=m.referall.format(
                                       ref_reward=config.config("ref_reward"),
                                       ref=func.top_ref_invite(chat_id),
                                       user_id=ref_code,
                                       bot_login=config.config("bot_login")),
                                   reply_markup=menu.to_cabinet())

        if call.data == 'qiwi':
            resp = func.replenish_balance(chat_id)
            await bot.send_message(chat_id=chat_id,
                                   text=resp[0],
                                   reply_markup=resp[1])

        if call.data == 'cancel_payment':
            await bot.answer_callback_query(callback_query_id=call.id,
                                            text='💢 Вы отменили платеж')
            await bot.delete_message(chat_id, message_id)
            func.cancel_payment(chat_id)
            await bot.send_message(
                chat_id=chat_id,
                text='💢 Платеж отменен!')

        if call.data == 'check_payment':
            check = func.check_payment(chat_id)
            if check[0] == 1:
                await bot.answer_callback_query(callback_query_id=call.id,
                                                text=f'✅ Оплата прошла\nСумма: {check[1]} RUB')
                await bot.edit_message_text(chat_id=chat_id,
                                            message_id=message_id,
                                            text=f'✅ Оплата прошла\nСумма: {check[1]} RUB')
                await bot.send_message(chat_id=config.config('admin_group'),
                                       text=f'♻️ Пришло пополнение Qiwi!\n\n'
                                            f'🧑🏻‍🔧 От: @{User(chat_id).username}\n\n'
                                            f'💰 Сумма: {check[1]} RUB')
            elif check[0] == 0:
                await bot.answer_callback_query(callback_query_id=call.id,
                                                text='💢 Оплата не найдена')
            else:
                pass

        if call.data == 'banker':
            await bot.send_message(chat_id=chat_id,
                                   text='Если вы хотите оплатить чеком, просто отправьте его в сюда:')

        if call.data == 'withdraw':
            await Withdraw.qiwi.set()
            await bot.send_message(chat_id=chat_id,
                                   text=f'<b>Введите свой киви (формат 7 или 380)</b>')

        if call.data == 'to_close':
            await bot.delete_message(chat_id, message_id)

        if 'back:' in call.data:
            await bot.delete_message(chat_id, message_id)

        if call.data == 'admin_info':
            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text=func.admin_info(),
                                        reply_markup=menu.admin_menu(), )

        if call.data == 'edit_bet_sum':
            await EditMinBet.bet.set()
            await bot.send_message(chat_id=chat_id,
                                   text='Введите новую сумму минимальной ставки')

        if call.data == 'edit_with_sum':
            await EditMinWith.bet.set()
            await bot.send_message(chat_id=chat_id,
                                   text='Введите новую сумму минимального вывода')

        if call.data == 'edit_ref_sum':
            await EditRefSum.bet.set()
            await bot.send_message(chat_id=chat_id,
                                   text='Введите новую сумму реферальной награды')

        if call.data == 'email_sending':
            await bot.send_message(chat_id=chat_id,
                                   text='Выбирите вариант рассылки',
                                   reply_markup=menu.email_sending())

        if call.data == 'email_sending_photo':
            await Email_sending_photo.photo.set()
            await bot.send_message(chat_id=chat_id, text='Отправьте фото боту, только фото!')

        if call.data == 'email_sending_text':
            await Admin_sending_messages.text.set()
            await bot.send_message(chat_id=chat_id, text='Введите текст рассылки', )

        if call.data == 'withdrawal_requests':
            await bot.send_message(chat_id=chat_id, text='Лист', reply_markup=func.witchdraw_adm())

        if 'witch_' in call.data:
            info = func.get_info_withdraw(call.data.split('_')[1])

            await bot.send_message(chat_id=chat_id, text=info[0], reply_markup=info[1])

        if 'withdraw_del:' in call.data:
            func.withdraw_del(call.data.split(':')[1])
            await bot.delete_message(chat_id, message_id)
            await bot.send_message(chat_id=chat_id, text='Удалено')

        if call.data == 'admin_searsh':
            await Search.user_id.set()
            await call.message.answer('Введи айди пользователя')

        if 'ban_' in call.data:
            user_id = call.data.split('_')[1]
            func.set_ban(user_id, "yes")
            await call.message.answer(f'Пользователь @{User(user_id).username} забанен')

        if 'unban_' in call.data:
            user_id = call.data.split('_')[1]
            func.set_ban(user_id, "no")
            await call.message.answer(f'Пользователь @{User(user_id).username} разбанен')

        if 'spin_up:' in call.data:
            user_id = call.data.split(":")[1]
            func.set_spinup(user_id, "True")
            await call.message.answer(f'Пользователю @{User(user_id).username} врублена подкрутка!')

        if 'spin_down:' in call.data:
            user_id = call.data.split(":")[1]
            func.set_spinup(user_id, "False")
            await call.message.answer(f'Пользователю @{User(user_id).username} вырублена подкрутка!')

        if 'give_bal:' in call.data:
            await Admin_give_balance.user_id.set()
            await call.message.answer('Введи id пользователя')

        if call.data == 'admin_promo':
            await call.message.answer('Выбери нужное:', reply_markup=menu.promo_markup())

        if call.data == 'active_promo':
            await bot.delete_message(chat_id, message_id)
            await call.message.answer('Активные промокоды', reply_markup=func.promo_active())

        if 'promo_' in call.data:
            try:
                id_promo = call.data.split("_")[1]
                info = func.get_info_promo(id_promo)
                await bot.send_message(chat_id=chat_id, text=info[0], reply_markup=info[1])
            except Exception:
                pass

        if call.data == 'delete_promo':
            await DelPromo.name.set()
            await call.message.answer('Введи название промокода')

        if call.data == 'create_promo':
            await CreatePromo.name.set()
            await call.message.answer(
                'Введи название промокода, который хочешь создать, для отмены введи "-", без ковычек')

        if call.data == 'promocode':
            await ActivatePromo.name.set()
            await call.message.answer('Введи промокод')

    else:
        pass


@dp.message_handler(state=PayP2P.amount)
async def pay_p2p(msg: types.Message, state: FSMContext):
    if msg.text.isdigit() is True:
        amount = int(msg.text)
        bill_id = random.randint(1111111, 9999999)
        # pay = p2p.create_pay(bill_id, amount)
        pay = p2p.create_bill(amount)
        await bot.send_message(chat_id=msg.from_user.id,
                               text=m.pay_p2p.format(
                                   bill_id=bill_id,
                                   amount=amount),
                               reply_markup=menu.pay_p2p(pay[0], pay[1]))
        await state.finish()
    else:
        await bot.send_message(chat_id=msg.from_user.id,
                               text='Ввводи только цифры')
        await state.finish()


@dp.message_handler(state=ActivatePromo.name)
async def activate_promo(msg: types.Message, state: FSMContext):
    name = msg.text
    i = func.get_info_promo(name)
    if i is not None:
        if i[2] > 0:
            if str(msg.from_user.id) not in i[4].split(','):
                func.activate_promo(msg.from_user.id, name)
                User(msg.from_user.id).update_balance(i[3])
                await msg.answer(f'Вам начисленно + {i[3]}')
                await bot.send_message(chat_id=config.config('admin_group'),
                                       text=f'<b>🎁 Активация промокода:</b>\n\n'
                                            f'<b>Пользователь:</b> {msg.from_user.get_mention(as_html=True)}\n\n'
                                            f'<b>Промокод:</b> {name} | <b>Сумма:</b> {i[3]}')
                await state.finish()
            else:
                await state.finish()
                await msg.answer(f'Вы уже активаировали этот промокод')
        else:
            await state.finish()
            func.promo_del(name)
            await msg.answer(f'Промокод закончился')
    else:
        await state.finish()
        await msg.answer(f'Нет такого промокода')


@dp.message_handler(state=CreatePromo.name)
async def create_promo(msg: types.Message, state: FSMContext):
    promo_name = msg.text

    if promo_name != '-':
        async with state.proxy() as data:
            data['name'] = promo_name
        await msg.answer('Введи награду промокода')
        await CreatePromo.next()
    else:
        await state.finish()
        await msg.answer('Отменено')


@dp.message_handler(state=CreatePromo.money)
async def create_promo2(msg: types.Message, state: FSMContext):
    amount = msg.text
    if amount.isdigit():
        async with state.proxy() as data:
            data['money'] = amount
        await msg.answer('Введи колличество активаций')
        await CreatePromo.next()
    else:
        await state.finish()
        await msg.answer('Отменено, сумма должна быть из цифр')


@dp.message_handler(state=CreatePromo.amount)
async def create_promo3(msg: types.Message, state: FSMContext):
    amount = msg.text
    if amount.isdigit():
        async with state.proxy() as data:
            name = data['name']
            money = data['money']
        await msg.answer(f'<b>Промокод успешно создан!</b>\n\n'
                         f'<b>Название:</b> <code>{name}</code>\n\n'
                         f'<b>Награда:</b> <code>{money}</code>\n\n'
                         f'<b>Активаций:</b> <code>{amount}</code>')
        func.add_promo(name, money, amount)
        await state.finish()
    else:
        await state.finish()
        await msg.answer('Отменено, сумма должна быть из цифр')


@dp.message_handler(state=DelPromo.name)
async def delete_promo(msg: types.Message, state: FSMContext):
    try:
        promo_name = msg.text
        if func.check_in_promo(promo_name) != 0:
            func.promo_del(promo_name)
            await msg.answer(f'Промокод {promo_name} удален!')
            await state.finish()
        else:
            await state.finish()
            await msg.answer('Нет такого промокода')
    except:
        await state.finish()
        await msg.answer('Нет такого промокода')


@dp.message_handler(state=Admin_give_balance.user_id)
async def give_balance(msg: types.Message, state: FSMContext):
    user_id = msg.text
    if int(func.check_in_bd(user_id)) != 0:
        async with state.proxy() as data:
            data['user_id'] = user_id
        await bot.delete_message(msg.from_user.id, msg.message_id)
        await msg.answer('Введи значение, на которое изменится баланс')
        await Admin_give_balance.next()
    else:
        await state.finish()
        await msg.answer('Нет такого пользователя')


@dp.message_handler(state=Admin_give_balance.balance)
async def give_balance2(msg: types.Message, state: FSMContext):
    balance = msg.text
    if balance.isdigit():
        async with state.proxy() as data:
            user_id = data['user_id']
        func.update_balance(user_id, float(balance))
        await bot.delete_message(msg.from_user.id, msg.message_id)
        await msg.answer(f'Баланс @{User(user_id).username} успешно изменен на {balance} RUB')
        await state.finish()
    else:
        await state.finish()
        await msg.answer('Вводить нужно только цифры')


@dp.message_handler(state=Search.user_id)
async def SearchUser(msg: types.Message, state: FSMContext):
    try:
        user = User(msg.text)
        await bot.send_message(chat_id=msg.from_user.id,
                               text=f'<b>Данные по пользователю:</b>\n\n'
                                    f'<b>Линк:</b> @{user.username}\n\n'
                                    f'<b>Баланс:</b> {user.balance} RUB\n\n'
                                    f'<b>Подкрутка:</b> {user.spin_up}\n\n'
                                    f'<b>Бан:</b> {user.ban}\n\n'
                                    f'<b>Дней в боте:</b> {func.cheked_days(func.days_stats_users(user.date[:10]))}\n\n'
                                    f'<b>Кем приглашен:</b> {user.who_invite}',
                               reply_markup=menu.admin_user_markup(msg.text))
        await state.finish()
    except Exception:
        await state.finish()
        await msg.answer('Нет такого пользователя')


@dp.message_handler(state=CreateCoin.bet)
async def create_coin(msg: types.Message, state: FSMContext):
    try:
        user = User(msg.from_user.id)
        if msg.text.isdigit() is True:
            bet = float(msg.text)
            if bet >= float(config.config('min_bank')):
                if bet <= user.balance:
                    id_games = random.randint(111, 999)
                    coin_1 = ["Орел", "Решка"]
                    win_coin = random.choice(coin_1)
                    user.update_balance(-bet)
                    coin.create_game(id_games, msg.from_user.id, bet, win_coin)
                    await bot.send_message(msg.from_user.id, 'Ваша ставка принята!')
                    await bot.send_message(config.config('channel_id'),
                                           text=f'<b>🕹 Новая игра Монетка:</b>\n\n'
                                                f'<b>🔘 Игра:</b> #Game_{id_games}\n'
                                                f'<b>💳 Ставка:</b> {bet}\n'
                                                f'<b>🧑🏻‍💻 Игрок:</b> @{msg.from_user.username}')
                    await state.finish()
                else:
                    await state.finish()
                    await bot.send_message(msg.from_user.id, 'Пополните балаланс!')
            else:
                await state.finish()
                await bot.send_message(msg.from_user.id, f'Минимальная ставка {config.config("min_bank")}')
        else:
            await state.finish()
            await msg.answer('Стака должна быть в цифрах!')
    except Exception:
        await state.finish()
        await bot.send_message(msg.from_user.id, 'Ошибка!')


@dp.callback_query_handler(state=CreateDice.game)
async def CreateDice_game(call: types.CallbackQuery, state: FSMContext):
    try:
        game = call.data

        async with state.proxy() as data:
            data['game'] = game
        await bot.delete_message(call.from_user.id, call.message.message_id)
        await call.message.answer(f'<b>Введите сумму ставки</b> (min. {config.config("min_bank")})')
        await CreateDice.next()
    except:
        await state.finish()


@dp.message_handler(state=CreateDice.bet)
async def CreateDice_bet(msg: types.Message, state: FSMContext):
    try:
        amount = float('{:.2f}'.format(float(msg.text)))
        user = User(msg.from_user.id)
        chat_id = msg.from_user.id
        async with state.proxy() as data:
            game = data['game']

        id_game = random.randint(111, 999)
        if amount <= user.balance:
            if amount >= float(config.config('min_bank')):
                dice.create_game(game, chat_id, id_game, amount)
                await msg.answer('Ставка принята')
                await bot.send_message(config.config('channel_id'),
                                       text=f'<b>🕹 Новая игра:</b>\n\n'
                                            f'<b>{game} Игра:</b> #Game_{id_game}\n'
                                            f'<b>💳 Ставка:</b> {amount}\n'
                                            f'<b>🧑🏻‍💻 Игрок:</b> @{msg.from_user.username}')
                user.update_balance(-amount)
                await state.finish()
            else:
                await state.finish()
                await msg.answer(f'<b>Минимальная ставка</b> {config.config("min_bank")}')
        else:
            await state.finish()
            await msg.answer(f'<bПополни баланс!</b>')
    except:
        await state.finish()
        await msg.answer('Ошибка!')


@dp.message_handler(state=CreateBj.bet)
async def create_Bj(msg: types.Message, state: FSMContext):
    try:
        await state.finish()
        if msg.text.isdigit() is True:
            bet = float(msg.text)
            user = User(msg.from_user.id)
            if user.balance >= bet:
                if bet >= float(config.config('min_bank')):
                    if await Bj().create_game(msg.from_user.id, bet) is True:
                        await msg.answer('Ставка принята')
                        await bot.send_message(config.config('channel_id'),
                                               text=f'<b>🕹 Новая игра:</b>\n\n'
                                                    f'<b>🀄️ Игра: </b> BlackJack\n'
                                                    f'<b>💳 Ставка:</b> {bet}\n'
                                                    f'<b>🧑🏻‍💻 Игрок:</b> @{msg.from_user.username}')
                    else:
                        await msg.answer('<bПополни баланс!</b>')
                else:
                    await msg.answer(f'<b>Минимальная ставка</b> {config.config("min_bank")}')
            else:
                await msg.answer('<bПополни баланс!</b>')
        else:
            await msg.answer('Cтавка должна быть из цифр!')
    except Exception:
        await msg.answer('Ошибка!')


@dp.message_handler(state=CreateSlots.bet)
async def CreateSlots_bet(msg: types.Message, state: FSMContext):
    try:
        amount = float('{:.2f}'.format(float(msg.text)))
        user = User(msg.from_user.id)
        chat_id = msg.from_user.id

        id_game = random.randint(111, 999)
        if amount <= user.balance:
            if amount >= float(config.config('min_bank')):
                slots.create_game(chat_id, id_game, amount)
                await msg.answer('Ставка принята')
                await bot.send_message(config.config('channel_id'),
                                       text=f'<b>🕹 Новая игра:</b>\n\n'
                                            f'<b>🎰 Игра:</b> #Game_{id_game}\n'
                                            f'<b>💳 Ставка:</b> {amount}\n'
                                            f'<b>🧑🏻‍💻 Игрок:</b> @{msg.from_user.username}')
                user.update_balance(-amount)
                await state.finish()
            else:
                await state.finish()
                await msg.answer(f'<b>Минимальная ставка</b> {config.config("min_bank")}')
        else:
            await state.finish()
            await msg.answer(f'<bПополни баланс!</b>')
    except:
        await state.finish()
        await msg.answer('Ошибка!')


@dp.message_handler(state=Email_sending_photo.photo, content_types=['photo'])
async def email_sending_photo_1(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['photo'] = random.randint(111111111, 999999999)

        await message.photo[-1].download(f'photos/{data["photo"]}.jpg')
        await Email_sending_photo.next()
        await message.answer('Введите текст рассылки')
    except:
        await state.finish()
        await message.answer('⚠️ ERROR ⚠️')


@dp.message_handler(state=Email_sending_photo.text)
async def email_sending_photo_2(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['text'] = message.text

            with open(f'photos/{data["photo"]}.jpg', 'rb') as photo:
                await message.answer_photo(photo, data['text'], parse_mode='html')

            await Email_sending_photo.next()
            await message.answer('Выбери дальнейшее действие', reply_markup=menu.admin_sending())
    except:
        await state.finish()
        await message.answer('⚠️ ERROR ⚠️')


@dp.message_handler(state=Email_sending_photo.action)
async def email_sending_photo_3(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    try:
        if message.text in menu.admin_sending_btn:
            if message.text == menu.admin_sending_btn[0]:  # Начать

                users = func.get_users_list()

                start_time = time.time()
                amount_message = 0
                amount_bad = 0
                async with state.proxy() as data:
                    photo_name = data["photo"]
                    text = data["text"]

                await state.finish()

                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f'✅ Вы запустили рассылку',
                        reply_markup=menu.main_menu()
                    )
                except:
                    pass

                for i in range(len(users)):
                    print(photo_name)
                    try:
                        with open(f'photos/{photo_name}.jpg', 'rb') as photo:
                            await bot.send_photo(
                                chat_id=users[i][0],
                                photo=photo,
                                caption=text,
                                parse_mode='html')
                        amount_message += 1
                    except Exception:
                        amount_bad += 1

                sending_time = time.time() - start_time

                try:
                    await bot.send_message(
                        chat_id=chat_id,
                        text=f'✅ Рассылка окончена\n'
                             f'👍 Отправлено: {amount_message}\n'
                             f'👎 Не отправлено: {amount_bad}\n'
                             f'🕐 Время выполнения рассылки - {sending_time} секунд'

                    )
                except:
                    pass

            elif message.text == menu.admin_sending_btn[1]:
                await state.finish()

                await bot.send_message(
                    message.from_user.id,
                    text='Рассылка отменена',
                    reply_markup=menu.main_menu()
                )

                await bot.send_message(
                    message.from_user.id,
                    text='Меню админа',
                    reply_markup=menu.admin_menu()
                )
        else:
            await bot.send_message(
                message.from_user.id,
                text='Не верная команда, повторите попытку',
                reply_markup=menu.admin_sending())

    except Exception:
        await state.finish()
        await bot.send_message(
            chat_id=message.from_user.id,
            text='⚠️ ERROR ⚠️'
        )


@dp.message_handler(state=Admin_sending_messages.text)
async def admin_sending_messages_1(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text

        await message.answer(data['text'], parse_mode='html')

        await Admin_sending_messages.next()
        await bot.send_message(
            chat_id=message.from_user.id,
            text='Выбери дальнейшее действие',
            reply_markup=menu.admin_sending()
        )


@dp.message_handler(state=Admin_sending_messages.action)
async def admin_sending_messages_2(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id

    if message.text in menu.admin_sending_btn:
        if message.text == menu.admin_sending_btn[0]:  # Начать

            users = func.get_users_list()

            start_time = time.time()
            amount_message = 0
            amount_bad = 0

            async with state.proxy() as data:
                text = data['text']

            await state.finish()

            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f'✅ Вы запустили рассылку',
                    reply_markup=menu.main_menu())
            except:
                pass

            for i in range(len(users)):
                try:
                    await bot.send_message(users[i][0], text, parse_mode='html')
                    amount_message += 1
                except Exception:
                    amount_bad += 1

            sending_time = time.time() - start_time

            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=f'✅ Рассылка окончена\n'
                         f'👍 Отправлено: {amount_message}\n'
                         f'👎 Не отправлено: {amount_bad}\n'
                         f'🕐 Время выполнения рассылки - {sending_time} секунд'

                )
            except:
                print('ERROR ADMIN SENDING')

        elif message.text == menu.admin_sending_btn[1]:
            await bot.send_message(
                message.from_user.id,
                text='Рассылка отменена',
                reply_markup=menu.main_menu()
            )
            await bot.send_message(
                message.from_user.id,
                text='Меню админа',
                reply_markup=menu.admin_menu()
            )
            await state.finish()
        else:
            await bot.send_message(
                message.from_user.id,
                text='Неверная команда, повторите попытку',
                reply_markup=menu.admin_sending())


@dp.message_handler(state=Withdraw.qiwi)
async def withdraw_sum(message: types.Message, state: FSMContext):
    try:
        qiwi = message.text

        if qiwi[:1] == '7' and len(qiwi) == 11 or qiwi[:3] == '380' and len(qiwi[3:]) == 9 or qiwi[:3] == '375' and len(
                qiwi) <= 12:
            if qiwi.isdigit() is True:
                async with state.proxy() as data:
                    data['qiwi'] = qiwi
                await Withdraw.next()
                await message.answer('<b>Введите сумму вывода:</b>')
            else:
                await state.finish()
                await message.answer('<b>💢 Неверно указан кошелек!</b>')
        else:
            await state.finish()
            await message.answer('<b>💢 Неверно указан кошелек!</b>')
    except Exception:
        await state.finish()
        await send_message.answer('<b>⚠️ Что-то пошло не по плану</b>')


@dp.message_handler(state=Withdraw.amount)
async def withdraw_info(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    try:
        async with state.proxy() as data:
            qiwi = data['qiwi']
        print(qiwi)
        amount = message.text
        if float(User(chat_id).balance) >= float(amount):
            min_with = config.config('min_withdraw_sum')
            if float(amount) >= float(min_with):
                id_witch = random.randint(11, 99)
                User(chat_id).update_balance(-float(amount))
                func.witchdraw_qiwi(id_witch, chat_id, qiwi, amount)
                await bot.send_message(
                    chat_id=config.config('admin_group'),
                    text=f'🛎 Выплата!\n\n'
                         f'🛡 user: <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>\n'
                         f'🧲 ID: <code>{message.from_user.id}</code>\n\n'
                         f'📆 Qiwi Кошелек: <code>{qiwi}</code>\n'
                         f'💰 Сумма: <code>{amount}</code> RUB')
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=f'<b>Oжидайте перевод !</b>\n\n'
                         f'<b>💈 Сумма выплаты:</b> <code>{amount}</code> <b>RUB</b>\n\n'
                         f'<b>💈 Реквизиты:</b>  <code>{qiwi}</code>')
                await state.finish()
            else:
                await state.finish()
                await message.answer(f'<b>🛎 Минимальный вывод: {config.config("min_withdraw_sum")}</b>')
        else:
            await state.finish()
            await message.answer('<b>Недостаточно средств!</b>')
    except Exception:
        await state.finish()
        await bot.send_message(chat_id=message.chat.id, text='⚠️ Что-то пошло не по плану')


@dp.message_handler(state=EditMinBet.bet)
async def edit_min_with(message: types.Message, state: FSMContext):
    try:
        config.edit_config('min_bank', message.text)
        await bot.send_message(message.from_user.id, f'Минимальная ставка изменена на {message.text}')
        await state.finish()
    except Exception as e:
        print(e)
        await state.finish()
        await bot.send_message(message.from_user.id, 'Ошибка!')


@dp.message_handler(state=EditRefSum.bet)
async def edit_min_with(message: types.Message, state: FSMContext):
    try:
        if float(message.text) <= 5:
            config.edit_config('ref_reward', message.text)
            await bot.send_message(message.from_user.id, f'реф награда изменена на {message.text}')
            await state.finish()
        else:
            await state.finish()
            await bot.send_message(message.from_user.id, 'слишком большая награда')
    except Exception:
        await state.finish()
        await bot.send_message(message.from_user.id, 'Ошибка!')


@dp.message_handler(state=EditMinWith.bet)
async def edit_min_with(message: types.Message, state: FSMContext):
    try:
        config.edit_config('min_withdraw_sum', message.text)
        await bot.send_message(message.from_user.id, f'Минимальный вывод изменен на {message.text}')
        await state.finish()
    except Exception as e:
        print(e)
        await state.finish()
        await bot.send_message(message.from_user.id, 'Ошибка!')


async def sending_check(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        try:
            info = func.sending_check()

            if info is not False:
                users = func.get_users_list()

                start_time = time.time()
                amount_message = 0
                amount_bad = 0

                if info[0] == 'text':
                    try:
                        await bot.send_message(
                            chat_id=config.config('admin_group'),
                            text=f'✅ Запуск рассылки')
                    except:
                        pass

                    for i in range(len(users)):
                        try:
                            await bot.send_message(users[i][0], info[1], parse_mode='html')
                            amount_message += 1
                        except Exception:
                            amount_bad += 1

                    sending_time = time.time() - start_time

                    try:
                        await bot.send_message(
                            chat_id=config.config('admin').split(':')[0],
                            text=f'✅ Рассылка окончена\n'
                                 f'👍 Отправлено: {amount_message}\n'
                                 f'👎 Не отправлено: {amount_bad}\n'
                                 f'🕐 Время выполнения рассылки - {sending_time} секунд'

                        )
                    except:
                        print('ERROR ADMIN SENDING')

                elif info[0] == 'photo':
                    try:
                        await bot.send_message(
                            chat_id=config.config('admin_group'),
                            text=f'✅ Запуск рассылки')
                    except:
                        pass

                    for i in range(len(users)):
                        try:
                            with open(f'photos/{info[2]}.jpg', 'rb') as photo:
                                await bot.send_photo(
                                    chat_id=users[i][0],
                                    photo=photo,
                                    caption=info[1],
                                    parse_mode='html')
                            amount_message += 1
                        except:
                            amount_bad += 1

                    sending_time = time.time() - start_time

                    try:
                        await bot.send_message(
                            chat_id=config.config('admin_group'),
                            text=f'✅ Рассылка окончена\n'
                                 f'👍 Отправлено: {amount_message}\n'
                                 f'👎 Не отправлено: {amount_bad}\n'
                                 f'🕐 Время выполнения рассылки - {sending_time} секунд'

                        )
                    except:
                        print('ERROR ADMIN SENDING')

            else:
                pass
        except Exception as e:
            print(e)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
