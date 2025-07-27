from rest_framework import serializers

from booking.models import Booking


class BookingCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class BookingResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'product', 'quantity', 'status', 'created_at']