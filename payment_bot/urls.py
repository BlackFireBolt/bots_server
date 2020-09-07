from django.urls import path
from bots_server import settings
from django.views.decorators.csrf import csrf_exempt

from .views import TelegramBot

app_name = 'payment_bot'
urlpatterns = [
    path('{}'.format(settings.TOKEN_PAYMENT), csrf_exempt(TelegramBot.as_view()), name='payment_bot')
]