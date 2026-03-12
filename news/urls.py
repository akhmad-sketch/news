"""
urls.py — маршруты приложения news
"""
from django.urls import path
from . import views

app_name = 'news'

urlpatterns = [
    path('', views.news_list, name='list'),
    path('news/<slug:slug>/', views.news_detail, name='detail'),
    path('category/<slug:slug>/', views.news_by_category, name='by_category'),
    path('search/', views.news_search, name='search'),

    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/create/', views.news_create, name='create'),
    path('admin-panel/edit/<slug:slug>/', views.news_edit, name='edit'),
    path('admin-panel/delete/<slug:slug>/', views.news_delete, name='delete'),
]
