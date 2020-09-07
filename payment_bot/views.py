from django.http import HttpResponse
from django.views import View
from telebot import TeleBot, types
import logging
from hashlib import md5
from urllib.parse import urlencode


from bots_server import settings
from .config import *
from payment.models import Payment


bot = TeleBot(settings.TOKEN_PAYMENT)
print(bot.get_me())


logger = logging.getLogger(__name__)


class TelegramBot(View):
    @staticmethod
    def get(request, *args, **kwargs):
        bot.remove_webhook()
        bot.set_webhook(url='https://bots-server.tk/payment_bot/{}'.format(settings.TOKEN_PAYMENT))
        return HttpResponse('Бот запущен')

    @staticmethod
    def post(request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])

        return HttpResponse('')


def main_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    key_day = types.InlineKeyboardButton(FIRST_OPTION_BUTTON, callback_data='option_one')
    key_week = types.InlineKeyboardButton(SECOND_OPTION_BUTTON, callback_data='option_two')
    keyboard.add(key_day, key_week)

    key_month = types.InlineKeyboardButton(THIRD_OPTION_BUTTON, callback_data='option_three')
    key_year = types.InlineKeyboardButton(FOURTH_OPTION_BUTTON, callback_data='option_four')
    keyboard.add(key_month, key_year)
    return keyboard


def url_generator(amount, order_id):
    separator = ':'
    merchant_id = settings.PAYMENT['public_key']
    secret_key = settings.PAYMENT['secret_key']
    lang = settings.PAYMENT['lang']
    params = {
        'm': merchant_id,
        'oa': amount,
        'o': order_id,
        'lang': lang,
    }

    sign_string = separator.join((merchant_id, amount, secret_key, order_id))
    sign = md5(sign_string.encode('utf-8')).hexdigest()

    params.update({'s': sign})
    params_string = urlencode(params)
    url = 'http://www.free-kassa.ru/merchant/cash.php?{}'

    return url.format(params_string)


def payment_keyboard(amount, order_id):
    keyboard_payment = types.InlineKeyboardMarkup()

    key_pay = types.InlineKeyboardButton('Оплатить подписку', url=url_generator(str(amount), str(order_id)))
    keyboard_payment.add(key_pay)
    key_back = types.InlineKeyboardButton('Назад', callback_data='back')
    keyboard_payment.add(key_back)
    return keyboard_payment


@bot.message_handler(commands=['start'])
def get_text_messages(message):
    bot.send_message(message.chat.id, HELLO_MESSAGE.format(message.from_user.username), reply_markup=main_keyboard())


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.message:
        if call.data == 'option_one':
            payment = Payment(account=call.message.from_user.id, amount=FIRST_OPTION_COST, chat_id=call.message.chat.id,
                              subscribe_days=FIRST_OPTION_DAYS)
            payment.save()
            bot.edit_message_text(FIRST_OPTION_PAYMENT_MESSAGE, call.message.chat.id,
                                  call.message.message_id, reply_markup=payment_keyboard(FIRST_OPTION_COST, payment.id))
            bot.answer_callback_query(call.id)
        elif call.data == 'option_two':
            payment = Payment(account=call.message.from_user.id, amount=SECOND_OPTION_COST,
                              chat_id=call.message.chat.id, subscribe_days=SECOND_OPTION_DAYS)
            payment.save()
            bot.edit_message_text(SECOND_OPTION_PAYMENT_MESSAGE, call.message.chat.id,
                                  call.message.message_id, reply_markup=payment_keyboard(SECOND_OPTION_COST,
                                                                                         payment.id))
            bot.answer_callback_query(call.id)
        elif call.data == 'option_three':
            payment = Payment(account=call.message.from_user.id, amount=THIRD_OPTION_COST, chat_id=call.message.chat.id,
                              subscribe_days=THIRD_OPTION_DAYS)
            payment.save()
            bot.edit_message_text(THIRD_OPTION_PAYMENT_MESSAGE, call.message.chat.id,
                                  call.message.message_id, reply_markup=payment_keyboard(THIRD_OPTION_COST, payment.id))
            bot.answer_callback_query(call.id)
        elif call.data == 'option_four':
            payment = Payment(account=call.message.from_user.id, amount=FOURTH_OPTION_COST,
                              chat_id=call.message.chat.id, subscribe_days=FOURTH_OPTION_DAYS)
            payment.save()
            bot.edit_message_text(FOURTH_OPTION_PAYMENT_MESSAGE, call.message.chat.id,
                                  call.message.message_id, reply_markup=payment_keyboard(FOURTH_OPTION_COST,
                                                                                         payment.id))
            bot.answer_callback_query(call.id)
        elif call.data == 'back':
            bot.edit_message_text(HELLO_MESSAGE, call.message.chat.id,
                                  call.message.message_id, reply_markup=main_keyboard())
            bot.answer_callback_query(call.id)


@bot.message_handler(content_types=['text'])
def alert_message(message):
    bot.send_message(message.chat.id, ALERT_MESSAGE)


def success_message(chat_id):
    keyboard_success = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(SUCCESS_BUTTON, url='https://t.me/FSKBtopVIP')
    keyboard_success.add(key)
    bot.send_message(chat_id, SUCCESS_MESSAGE, reply_markup=keyboard_success)


def failure_message(chat_id):
    bot.send_message(chat_id, FAILURE_MESSAGE)


def status_check(message):
    client = Payment.objects.get(chat_id=message.chat.id)
    if client.status:
        bot.send_message(message.chat.id, SUCCESS_MESSAGE, reply_markup=main_keyboard())