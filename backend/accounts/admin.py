from django.contrib import admin
from .models import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'state', 'postal_code', 'default']
    list_filter = ['default', 'state', 'country']
    search_fields = ['full_name', 'street_address', 'city', 'postal_code']
