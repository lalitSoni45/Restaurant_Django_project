from django.contrib import admin
from .models import Category, MenuItem, Feedback, TableBooking, Contact

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_featured', 'is_available')
    list_filter = ('category', 'is_featured', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_featured', 'is_available')

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)
    list_filter = ('created_at',)

@admin.register(TableBooking)
class TableBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'guests', 'status')
    list_filter = ('status', 'date')
    search_fields = ('name', 'email', 'phone')
    list_editable = ('status',)
    readonly_fields = ('created_at',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('address', 'phone', 'email')
