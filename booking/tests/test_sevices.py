import pytest
from django.core.exceptions import ValidationError
from booking.models import Booking
from goods.models import Product
from booking.services import create_booking, confirm_booking, cancel_booking
from unittest.mock import patch
from django.contrib.auth.models import User

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create(username='testuser')


@pytest.fixture
def product():
    return Product.objects.create(
        name='Test Product',
        description='',
        price=100,
        quantity=10,
        reservation_timeout=5
    )


def test_create_booking_success(user, product):
    with patch('booking.services.delete_booking_after_timeout.apply_async') as mock_async:
        booking = create_booking(user, product.id, 3)

    assert booking.status == 'PENDING'
    assert booking.quantity == 3
    assert booking.product == product
    assert booking.user == user
    mock_async.assert_called_once()
    args, kwargs = mock_async.call_args
    assert args[0] == (booking.id,)
    assert kwargs['countdown'] == product.reservation_timeout * 60


def test_create_booking_invalid_data(user):
    with pytest.raises(ValidationError):
        create_booking(user, None, 3)

    with pytest.raises(ValidationError):
        create_booking(user, 1, 0)


def test_create_booking_not_enough_quantity(user, product):
    Booking.objects.create(user=user, product=product, quantity=9, status='PENDING')

    with pytest.raises(ValidationError, match='Недостаточно товара'):
        create_booking(user, product.id, 2)


def test_confirm_booking_success(user, product):
    booking = Booking.objects.create(user=user, product=product, quantity=4, status='PENDING')

    confirmed = confirm_booking(user, booking.id)

    product.refresh_from_db()
    booking.refresh_from_db()

    assert confirmed.status == 'CONFIRMED'
    assert product.quantity == 6


def test_confirm_booking_not_pending(user, product):
    booking = Booking.objects.create(user=user, product=product, quantity=2, status='CONFIRMED')

    with pytest.raises(ValidationError, match='Бронь неактивна'):
        confirm_booking(user, booking.id)


def test_confirm_booking_not_enough_product(user, product):
    booking = Booking.objects.create(user=user, product=product, quantity=20, status='PENDING')

    with pytest.raises(ValidationError, match='Недостаточно товара на складе'):
        confirm_booking(user, booking.id)


def test_cancel_booking_success(user, product):
    booking = Booking.objects.create(user=user, product=product, quantity=1, status='PENDING')

    result = cancel_booking(user, booking.id)

    assert result.status == 'CANCELED'
    booking.refresh_from_db()
    assert booking.status == 'CANCELED'


def test_cancel_booking_invalid_status(user, product):
    booking = Booking.objects.create(user=user, product=product, quantity=1, status='CONFIRMED')

    with pytest.raises(ValidationError, match='Нельзя отменить завершённую бронь'):
        cancel_booking(user, booking.id)


def test_concurrent_booking_conflict():
    user1 = User.objects.create(username='user1')
    user2 = User.objects.create(username='user2')
    product = Product.objects.create(
        name='Test Product',
        description='',
        price=100,
        quantity=100,
        reservation_timeout=5
    )

    create_booking(user1, product.id, 51)

    with pytest.raises(ValidationError, match='Недостаточно товара'):
        create_booking(user2, product.id, 50)



def test_confirm_booking_rollback_on_failure(user, product):
    booking = Booking.objects.create(user=user, product=product, quantity=20, status='PENDING')

    # Сначала симулируем нехватку товара
    product.quantity = 10
    product.save()

    with pytest.raises(ValidationError):
        confirm_booking(user, booking.id)

    booking.refresh_from_db()
    product.refresh_from_db()

    # Проверим, что статус остался прежним и количество не изменилось
    assert booking.status == 'PENDING'
    assert product.quantity == 10


@pytest.mark.parametrize("quantities,expected_final", [
    ([20, 30, 50], 0),
    ([10, 10, 10, 10], 60),
])
def test_massive_booking_and_remaining(quantities, expected_final):
    user = User.objects.create(username='bulk_user')
    product = Product.objects.create(
        name='MassProduct',
        description='',
        price=10,
        quantity=100,
        reservation_timeout=10
    )

    for qty in quantities:
        create_booking(user, product.id, qty)

    assert product.available_quantity() == expected_final
