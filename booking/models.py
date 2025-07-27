from django.db import models
from django.contrib import admin

STATUSES = [
    ('PENDING', 'Ожидает подтверждения пользователя'),
    ('CONFIRMED', 'Подтверждена'),
    ('CANCELED', 'Отменена'),
]


class Booking(models.Model):
    user = models.ForeignKey(
        'auth.User',
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'goods.Product',
        verbose_name='Товар',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    quantity = models.PositiveIntegerField('Количество')
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    status = models.CharField(
        'Статус',
        max_length=30,
        choices=STATUSES,
        default='PENDING'
    )

    class Meta:
        verbose_name = 'Бронь'
        verbose_name_plural = 'Бронирования'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['product']),
            models.Index(fields=['product', 'status']),
        ]

    def __str__(self):
        return f'Бронь #{self.pk} — {self.product} x {self.quantity} ({self.get_status_display()})'
