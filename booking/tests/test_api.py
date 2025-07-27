import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from booking.models import Booking
from goods.models import Product

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def product(db):
    return Product.objects.create(name='Тестовый товар', price=100, quantity=10)


@pytest.fixture
def create_booking():
    def _create(user, product):
        return Booking.objects.create(user=user, product=product, quantity=1)
    return _create


@pytest.mark.django_db
def test_booking_creation(client, user, product):
    client.force_authenticate(user=user)
    response = client.post('/api/v1/booking/', {'product_id': product.id, 'quantity': 1})
    assert response.status_code == 201
    assert Booking.objects.filter(user=user, product=product).exists()


@pytest.mark.django_db
def test_booking_confirm(client, user, product, create_booking):
    booking = create_booking(user, product)
    client.force_authenticate(user=user)
    response = client.post(f'/api/v1/booking/{booking.id}/confirm/')
    booking.refresh_from_db()
    assert response.status_code == 200
    assert booking.status == 'CONFIRMED'


@pytest.mark.django_db
def test_booking_cancel(client, user, product, create_booking):
    booking = create_booking(user, product)
    client.force_authenticate(user=user)
    response = client.post(f'/api/v1/booking/{booking.id}/cancel/')
    booking.refresh_from_db()
    assert response.status_code == 200
    assert booking.status == 'CANCELED'
