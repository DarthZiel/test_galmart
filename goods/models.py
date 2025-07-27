from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce


class Product(models.Model):
    name = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество на складе')
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    reservation_timeout = models.PositiveIntegerField(
        'Время хранения брони (мин)',
        default=15,
        help_text='Сколько минут может существовать бронь'
    )

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
            models.Index(fields=['price']),
        ]

    def __str__(self):
        return f'{self.name} (остаток: {self.quantity})'

    def available_quantity(self):
        booked_quantity = self.bookings.filter(status='PENDING').aggregate(
            total=Coalesce(Sum('quantity'), 0)
        )['total']
        return self.quantity - booked_quantity
