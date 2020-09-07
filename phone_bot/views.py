from django.http import HttpResponse
from django.views import View
from telebot import TeleBot, types
from bots_server import settings
from bots_server.settings import EMAIL_MESSAGE
import logging
import phonenumbers
from django.core.mail import send_mail

from .models import Lead

bot = TeleBot(settings.TOKEN_PHONE)
print(bot.get_me())


logger = logging.getLogger(__name__)


class TelegramBot(View):
    @staticmethod
    def get(request, *args, **kwargs):
        bot.remove_webhook()
        bot.set_webhook(url="https://bots-server.tk/phone_bot/{}".format(settings.TOKEN_PHONE))
        return HttpResponse("Бот запущен")

    @staticmethod
    def post(request, *args, **kwargs):
        json_str = request.body.decode('UTF-8')
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])

        return HttpResponse('')


@bot.message_handler(commands=['start'])
def test_contact(message):
    keyboard = types.ReplyKeyboardMarkup(False, True)
    reg_button = types.KeyboardButton(text='Оставить заявку', request_contact=True)
    keyboard.add(reg_button)
    response = bot.send_message(message.chat.id,
                                "You should share your phone number",
                                reply_markup=keyboard)
    print(response.contact)


@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    phone = phonenumbers.parse(message.contact.phone_number)
    country = phonenumbers.region_code_for_number(phone)
    new_lead = Lead(name=message.from_user.first_name, phone=phone, country=country)
    new_lead.save()
    # send_mail('academy54.com', 'Новый лид на академи54 \n' +
    #          EMAIL_MESSAGE.format(message.from_user.first_name, message.from_user.last_name, phone, country),
    #          'boltward@gmail.com', ['mailhandler@ltdstock.net'], fail_silently=False)
    bot.send_message(message.chat.id, 'Заявка принята. \n Ожидайте звонка специалиста! \n {} {}'.format(phone, country))