from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError

from booking.models import Booking
from goods.models import Product
from booking.tasks import delete_booking_after_timeout


@transaction.atomic
def create_booking(user, product_id, quantity):
    if not product_id or quantity < 1:
        raise ValidationError('Неверные данные')

    product = Product.objects.select_for_update().get(id=product_id)

    booked_quantity = product.bookings.filter(status='PENDING').aggregate(
        total=Coalesce(Sum('quantity'), 0)
    )['total']

    available_quantity = product.quantity - booked_quantity
    if quantity > available_quantity:
        raise ValidationError('Недостаточно товара')

    booking = Booking.objects.create(
        user=user,
        product=product,
        quantity=quantity,
        status='PENDING'
    )

    delete_booking_after_timeout.apply_async(
        (booking.id,),
        countdown=product.reservation_timeout * 60
    )

    return booking


@transaction.atomic
def confirm_booking(user, booking_id):
    booking = Booking.objects.select_for_update().select_related('product').get(
        id=booking_id,
        user=user
    )

    if booking.status != 'PENDING':
        raise ValidationError('Бронь неактивна')

    if booking.product.quantity < booking.quantity:
        raise ValidationError('Недостаточно товара на складе')

    booking.product.quantity -= booking.quantity
    booking.product.save()

    booking.status = 'CONFIRMED'
    booking.save()

    return booking


@transaction.atomic
def cancel_booking(user, booking_id):
    booking = Booking.objects.select_for_update().get(id=booking_id, user=user)

    if booking.status != 'PENDING':
        raise ValidationError('Нельзя отменить завершённую бронь')

    booking.status = 'CANCELED'
    booking.save()

    return booking
