"""
views.py — представления (контроллеры) приложения news

Ключевой момент: при открытии страницы новости происходит:
  1. Загрузка новости из PostgreSQL (Django ORM)
  2. Увеличение счётчика просмотров в MongoDB (pymongo)
  3. Запись в историю просмотров (MongoDB)
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import News, Category, Comment
from .forms import CommentForm, NewsForm
from newsportal.mongo_client import mongo_client



def news_list(request):
    """
    Главная страница — список всех опубликованных новостей.
    Добавляет к каждой новости счётчик просмотров из MongoDB.
    """
    news_qs = News.objects.filter(
        status=News.STATUS_PUBLISHED
    ).select_related('author', 'category')

    featured_news = news_qs.filter(is_featured=True)[:3]

    paginator = Paginator(news_qs, 9)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    news_ids = [n.id for n in page_obj]
    views_data = mongo_client.get_views_for_multiple(news_ids)

    for news_item in page_obj:
        news_item.views_count = views_data.get(news_item.id, 0)

    popular_news = _get_popular_news(limit=5)

    context = {
        'page_obj': page_obj,
        'featured_news': featured_news,
        'popular_news': popular_news,
        'title': 'Новостной портал',
    }
    return render(request, 'news/news_list.html', context)


def news_detail(request, slug):
    
    news = get_object_or_404(
        News.objects.select_related('author', 'category'),
        slug=slug,
        status=News.STATUS_PUBLISHED
    )
    ip_address = _get_client_ip(request)
    user_id = request.user.id if request.user.is_authenticated else None

    mongo_client.increment_views(
        news_id=news.id,
        user_id=user_id,
        ip_address=ip_address
    )

    views_count = mongo_client.get_views_count(news.id)

    comments = news.comments.filter(is_approved=True).select_related('author')

    comment_form = CommentForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Для комментирования нужно войти в аккаунт.')
            return redirect('accounts:login')

        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.news = news
            comment.author = request.user
            comment.save()
            messages.success(request, '✅ Ваш комментарий добавлен!')
            return redirect('news:detail', slug=slug)

    popular_news = _get_popular_news(limit=5)

    # Похожие новости из той же категории
    related_news = []
    if news.category:
        related_news = News.objects.filter(
            category=news.category,
            status=News.STATUS_PUBLISHED
        ).exclude(id=news.id)[:3]

    context = {
        'news': news,
        'comments': comments,
        'comment_form': comment_form,
        'views_count': views_count,
        'popular_news': popular_news,
        'related_news': related_news,
        'title': news.title,
    }
    return render(request, 'news/news_detail.html', context)


def news_by_category(request, slug):
    """Список новостей по категории."""
    category = get_object_or_404(Category, slug=slug)
    news_qs = News.objects.filter(
        category=category,
        status=News.STATUS_PUBLISHED
    ).select_related('author', 'category')

    paginator = Paginator(news_qs, 9)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    news_ids = [n.id for n in page_obj]
    views_data = mongo_client.get_views_for_multiple(news_ids)
    for news_item in page_obj:
        news_item.views_count = views_data.get(news_item.id, 0)

    context = {
        'page_obj': page_obj,
        'category': category,
        'popular_news': _get_popular_news(),
        'title': f'Категория: {category.name}',
    }
    return render(request, 'news/news_list.html', context)


def news_search(request):
    """Поиск по заголовку и тексту новостей в PostgreSQL."""
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # ✅ Исправлено: убрано поле short_description которого больше нет
        results = News.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query),
            status=News.STATUS_PUBLISHED
        ).select_related('author', 'category').distinct()

        news_ids = [n.id for n in results]
        views_data = mongo_client.get_views_for_multiple(news_ids)
        for news_item in results:
            news_item.views_count = views_data.get(news_item.id, 0)

    context = {
        'results': results,
        'query': query,
        'title': f'Поиск: {query}',
    }
    return render(request, 'news/search_results.html', context)


# ─────────────────────────────────────────────────────────────────────────────
# АДМИНИСТРАТИВНЫЕ СТРАНИЦЫ
# ─────────────────────────────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    """Административная панель со статистикой из обеих БД."""
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещён.')
        return redirect('news:list')

    total_news = News.objects.count()
    published_news = News.objects.filter(status=News.STATUS_PUBLISHED).count()
    total_comments = Comment.objects.count()
    recent_news = News.objects.select_related('author', 'category').order_by('-created_at')[:10]

    # Статистика из MongoDB
    mongo_stats = mongo_client.get_stats_summary()
    popular_news = _get_popular_news(limit=5)

    context = {
        'total_news': total_news,
        'published_news': published_news,
        'total_comments': total_comments,
        'mongo_stats': mongo_stats,
        'recent_news': recent_news,
        'popular_news': popular_news,
        'mongo_connected': mongo_client.is_connected(),
        'title': 'Панель управления',
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def news_create(request):
    """Создание новой новости (только для staff)."""
    if not request.user.is_staff:
        return redirect('news:list')

    form = NewsForm()
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            messages.success(request, f'✅ Новость "{news.title}" создана!')
            return redirect('news:detail', slug=news.slug)

    return render(request, 'admin_panel/news_form.html', {
        'form': form,
        'title': 'Добавить новость',
        'action': 'Создать'
    })


@login_required
def news_edit(request, slug):
    """Редактирование новости (только для staff)."""
    if not request.user.is_staff:
        return redirect('news:list')

    news = get_object_or_404(News, slug=slug)
    form = NewsForm(instance=news)

    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Новость "{news.title}" обновлена!')
            return redirect('news:detail', slug=news.slug)

    return render(request, 'admin_panel/news_form.html', {
        'form': form,
        'news': news,
        'title': f'Редактировать: {news.title}',
        'action': 'Сохранить'
    })


@login_required
def news_delete(request, slug):
    """Удаление новости (только для staff)."""
    if not request.user.is_staff:
        return redirect('news:list')

    news = get_object_or_404(News, slug=slug)

    if request.method == 'POST':
        title = news.title
        news.delete()
        messages.success(request, f'🗑️ Новость "{title}" удалена.')
        return redirect('news:admin_dashboard')

    return render(request, 'admin_panel/news_confirm_delete.html', {
        'news': news,
        'title': f'Удалить: {news.title}'
    })


# ─────────────────────────────────────────────────────────────────────────────
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────────────────────────────────────────

def _get_popular_news(limit: int = 5) -> list:
    """
    Популярные новости — комбинирует данные из MongoDB и PostgreSQL.
    MongoDB даёт ID самых просматриваемых → PostgreSQL загружает детали.
    """
    popular_ids_with_views = mongo_client.get_popular_news_ids(limit=limit)

    if not popular_ids_with_views:
        # MongoDB недоступна — показываем просто последние новости
        return list(News.objects.filter(
            status=News.STATUS_PUBLISHED
        ).select_related('category')[:limit])

    popular_ids = [item[0] for item in popular_ids_with_views]
    views_map = {item[0]: item[1] for item in popular_ids_with_views}

    news_qs = News.objects.filter(
        id__in=popular_ids,
        status=News.STATUS_PUBLISHED
    ).select_related('category')

    news_dict = {n.id: n for n in news_qs}
    popular_news = []
    for news_id in popular_ids:
        if news_id in news_dict:
            news_item = news_dict[news_id]
            news_item.views_count = views_map.get(news_id, 0)
            popular_news.append(news_item)

    return popular_news


def _get_client_ip(request) -> str:
    """Получает IP-адрес клиента."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')