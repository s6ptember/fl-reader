from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'reading_progress', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'author']
    readonly_fields = ['id', 'created_at']
