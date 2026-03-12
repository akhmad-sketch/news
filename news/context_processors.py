"""
context_processors.py — глобальные контекстные переменные

Категории добавляются во все шаблоны автоматически,
чтобы навигационное меню работало на каждой странице.
"""
from .models import Category


def categories_processor(request):
    """Передаёт список всех категорий в каждый шаблон."""
    return {
        'all_categories': Category.objects.all()
    }
