from django.urls import path
from bots_server import settings
from django.views.decorators.csrf import csrf_exempt

from .views import TelegramBot

app_name = 'phone_bot'
urlpatterns = [
    path('{}'.format(settings.TOKEN_PHONE), csrf_exempt(TelegramBot.as_view()), name='phone_bot')
]