from django.contrib import admin

from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'account', 'chat_id', 'subscribe_days', 'date_create')


admin.site.register(Payment, PaymentAdmin)

admin.site.site_header = 'Телеграм боты'