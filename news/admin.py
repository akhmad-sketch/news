"""
admin.py — регистрация моделей в Django Admin
Упрощённая форма: только заголовок, картинка, текст, категория
"""
from django.contrib import admin
from .models import Category, News, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author', 'status', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['title', 'content']
    list_editable = ['status']

    fieldsets = (
        ('✏️ Основное', {
            'fields': ('title', 'category', 'image_url')
        }),
        ('📝 Содержание', {
            'fields': ('content',)
        }),
        ('⚙️ Настройки', {
            'fields': ('status', 'is_featured'),
            'classes': ('collapse',),  # скрыто по умолчанию
        }),
    )

    readonly_fields = ['slug', 'author', 'created_at', 'updated_at']

    def save_model(self, request, obj, form, change):
        """Автоматически ставим автора при создании."""
        if not obj.pk:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'news', 'is_approved', 'created_at']
    list_filter = ['is_approved']
    list_editable = ['is_approved']
    search_fields = ['text', 'author__username']