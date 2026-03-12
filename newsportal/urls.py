"""
urls.py — главный файл маршрутизации проекта NewsPortal
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Стандартная административная панель Django
    path('admin/', admin.site.urls),

    # Маршруты приложения новостей (главная страница, список, детали)
    path('', include('news.urls')),

    # Маршруты аккаунтов (регистрация, логин, профиль)
    path('accounts/', include('accounts.urls')),
]

# В режиме разработки Django сам отдаёт медиа-файлы
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
