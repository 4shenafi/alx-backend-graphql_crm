# crm/admin.py
from django.contrib import admin
from .models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    list_filter = ['created_at']
