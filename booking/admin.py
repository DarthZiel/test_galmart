from django.contrib import admin
from .models import Booking


# Register your models here.


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__name')
    autocomplete_fields = ('user', 'product')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


