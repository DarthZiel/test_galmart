from django.urls import path
from booking.views import BookingCreateView, ConfirmBookingView, CancelBookingView

urlpatterns = [
    path('booking/', BookingCreateView.as_view(), name='booking-create'),
    path('booking/<int:booking_id>/confirm/', ConfirmBookingView.as_view(), name='booking-confirm'),
    path('booking/<int:booking_id>/cancel/', CancelBookingView.as_view(), name='booking-cancel'),
]
