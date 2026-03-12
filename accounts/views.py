"""
views.py — представления для аккаунтов пользователей
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import RegisterForm, LoginForm, ProfileForm
from .models import UserProfile
from news.models import News, Comment
from newsportal.mongo_client import mongo_client


def register_view(request):
    """Страница регистрации нового пользователя."""
    if request.user.is_authenticated:
        return redirect('news:list')

    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # Создаём пользователя в PostgreSQL
            user = form.save()
            # Создаём пустой профиль
            UserProfile.objects.create(user=user)
            # Автоматически входим после регистрации
            login(request, user)
            messages.success(request, f'🎉 Добро пожаловать, {user.username}!')
            return redirect('news:list')

    return render(request, 'accounts/register.html', {
        'form': form,
        'title': 'Регистрация'
    })


def login_view(request):
    """Страница входа в аккаунт."""
    if request.user.is_authenticated:
        return redirect('news:list')

    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                messages.success(request, f'👋 Добро пожаловать, {user.username}!')
                # Перенаправляем на страницу, с которой пришли
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный логин или пароль.')

    return render(request, 'accounts/login.html', {
        'form': form,
        'title': 'Вход'
    })


def logout_view(request):
    """Выход из аккаунта."""
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('news:list')


@login_required
def profile_view(request):
    """Страница профиля текущего пользователя."""
    # Получаем или создаём профиль
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # Статистика из PostgreSQL
    user_news = News.objects.filter(
        author=request.user,
        status=News.STATUS_PUBLISHED
    ).order_by('-created_at')

    user_comments = Comment.objects.filter(
        author=request.user
    ).select_related('news').order_by('-created_at')[:5]

    # История просмотров из MongoDB
    history_ids = mongo_client.get_user_view_history(request.user.id, limit=5)
    viewed_news = []
    if history_ids:
        news_map = {n.id: n for n in News.objects.filter(id__in=history_ids)}
        viewed_news = [news_map[nid] for nid in history_ids if nid in news_map]

    context = {
        'profile': profile,
        'user_news': user_news,
        'user_comments': user_comments,
        'viewed_news': viewed_news,
        'title': f'Профиль: {request.user.username}',
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    """Редактирование профиля."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ Профиль обновлён!')
            return redirect('accounts:profile')

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
        'title': 'Редактировать профиль'
    })
