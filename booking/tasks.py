from celery import shared_task


@shared_task
def delete_booking_after_timeout(booking_id):
    from booking.models import Booking
    from django.db import transaction

    try:
        with transaction.atomic():
            booking = Booking.objects.select_for_update().get(id=booking_id)
            booking.delete()

    except Booking.DoesNotExist:
        pass