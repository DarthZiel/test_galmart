from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.core.exceptions import ValidationError

from booking.services import create_booking, confirm_booking, cancel_booking
from booking.models import Booking
from goods.models import Product
from booking.booking_logger import log_booking_event
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from booking.serializers import BookingCreateSerializer, BookingResponseSerializer


class BookingCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(request_body=BookingCreateSerializer,
                         responses={201: openapi.Response('Бронь создана'),
                                    400: 'Ошибка валидации',
                                    404: 'Товар не найден'})
    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            quantity = int(request.data.get('quantity', 1))

            booking = create_booking(request.user, product_id, quantity)
            log_booking_event(booking, 'created', request)
            return Response({'message': 'Бронь создана'}, status=201)

        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

        except Product.DoesNotExist:
            return Response({'error': 'Товар не найден'}, status=404)


class ConfirmBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Подтверждение брони",
        responses={
            200: BookingResponseSerializer,
            400: 'Ошибка валидации',
            404: 'Бронь не найдена'
        }
    )
    def post(self, request, booking_id):
        try:
            booking = confirm_booking(request.user, booking_id)
            log_booking_event(booking, 'confirmed', request)

            return Response(BookingResponseSerializer(booking).data)

        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

        except Booking.DoesNotExist:
            return Response({'error': 'Бронь не найдена'}, status=404)


class CancelBookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Отмена брони",
        responses={
            200: BookingResponseSerializer,
            400: 'Ошибка валидации',
            404: 'Бронь не найдена'
        }
    )
    def post(self, request, booking_id):
        try:
            booking = cancel_booking(request.user, booking_id)
            log_booking_event(booking, 'canceled', request)

            return Response(BookingResponseSerializer(booking).data)

        except ValidationError as e:
            return Response({'error': str(e)}, status=400)

        except Booking.DoesNotExist:
            return Response({'error': 'Бронь не найдена'}, status=404)
