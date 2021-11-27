from hashlib import md5
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta

from bots_server import settings
from payment_bot.views import success_message, failure_message
from .models import Payment


def date_generator(days):
    return datetime.now()+timedelta(days=days)


@csrf_exempt
def payment(request):
    """ Check responce from payment system """
    
    allow_ips = {
        '136.243.38.147',
        '136.243.38.149',
        '136.243.38.150',
        '136.243.38.151',
        '136.243.38.189',
        '88.198.88.98'
    }
    required_params = {
        'MERCHANT_ID',
        'AMOUNT',
        'intid',
        'MERCHANT_ORDER_ID',
        'CUR_ID',
        'SIGN',
    }

    ip_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip_forwarded_for:
        ip = ip_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if ip not in allow_ips:
        raise Http404()

    if any(required_param not in request.POST for required_param in required_params):
        return HttpResponse('Invalid request')

    data = request.POST.copy()
    merchant_id = settings.PAYMENT['public_key']
    key = settings.PAYMENT['secret_key2']
    order_id = data.get('MERCHANT_ORDER_ID')
    amount = data.get('AMOUNT')

    payment_obj = get_object_or_404(Payment, id=order_id)

    if payment_obj.status:
        failure_message(payment_obj.chat_id)
        return HttpResponse('Order has already been paid')

    if amount != str(payment_obj.amount):
        failure_message(payment_obj.chat_id)
        return HttpResponse('Invalid amount')

    if data.get('MERCHANT_ID') != merchant_id:
        failure_message(payment_obj.chat_id)
        return HttpResponse('Invalid checkout id')

    sign_string = ':'.join((merchant_id, amount, key, order_id))
    sign = md5(sign_string.encode('utf-8')).hexdigest()

    if data.get('SIGN') != sign:
        failure_message(payment_obj.chat_id)
        return HttpResponse('Incorrect digital signature')

    success_message(payment_obj.chat_id)
    payment_obj.status = True
    payment_obj.date_expiration = date_generator(payment_obj.subscribe_days)
    payment_obj.date_complete = datetime.now()
    payment_obj.save()
    return HttpResponse('YES')
