import uuid
from django.db import models


class Payment (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='Номер платежа')
    account = models.CharField(max_length=256, verbose_name='Покупатель')
    chat_id = models.CharField(max_length=256, verbose_name='Номер чата с покупателем')
    amount = models.IntegerField(default=0, verbose_name='Сумма')
    subscribe_days = models.IntegerField(default=0, verbose_name='Количество дней подписки')
    status = models.BooleanField(default=False, verbose_name='Статус платежа')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_complete = models.DateTimeField(blank=True, null=True, verbose_name='Дата оплаты')
    date_expiration = models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания')

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-date_complete', '-date_expiration']