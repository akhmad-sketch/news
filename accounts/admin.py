from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'website', 'bio']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
