from django.db import models


class Lead (models.Model):
    name = models.CharField(max_length=64, verbose_name='Имя', unique=False)
    email = models.CharField(max_length=64, unique=False, verbose_name='Email')
    phone = models.CharField(max_length=64, unique=False, verbose_name='Телефон')
    country = models.CharField(max_length=5, unique=False, verbose_name='Страна')
    created_date = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата регистрации')

    class Meta:
        verbose_name = 'Лид'
        verbose_name_plural = 'Лиды'
        ordering = ['-created_date']