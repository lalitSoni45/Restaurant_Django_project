from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Category, 
    MenuItem, 
    Feedback, 
    TableBooking, 
    Contact,
    CartItem, 
    Order, 
    Payment
)

# CustomUser admin registration will be implemented in phase 2
"""
# Register the custom user model with the admin site
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Phone Information', {'fields': ('phone_number',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Phone Information', {'fields': ('phone_number',)}),
    )
    list_display = ('username', 'email', 'phone_number', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone_number', 'first_name', 'last_name')

admin.site.register(CustomUser, CustomUserAdmin)
"""

admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Feedback)
admin.site.register(TableBooking)
admin.site.register(Contact)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(Payment)
