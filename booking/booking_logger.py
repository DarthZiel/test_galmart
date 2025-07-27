from pymongo import MongoClient
from datetime import datetime
from django.conf import settings

client = MongoClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]
collection = db['booking_events']


def log_booking_event(booking, action, request=None):
    doc = {
        'booking_id': str(booking.id),
        'user_id': booking.user_id,
        'product_id': booking.product_id,
        'quantity': booking.quantity,
        'status': booking.status,
        'action': action,
        'timestamp': datetime.utcnow(),
    }

    if request:
        doc['ip'] = request.META.get('REMOTE_ADDR')
        doc['user_agent'] = request.META.get('HTTP_USER_AGENT')

    try:
        collection.insert_one(doc)
    except Exception as e:
        print(f"[MongoLogError] {e}")
