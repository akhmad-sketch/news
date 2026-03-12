"""
forms.py — формы приложения news
Упрощённая версия: только нужные поля
"""
from django import forms
from .models import Comment, News


class CommentForm(forms.ModelForm):
    """Форма добавления комментария."""

    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...',
                'class': 'form-control'
            })
        }
        labels = {
            'text': ''
        }


class NewsForm(forms.ModelForm):
    """
    Форма создания/редактирования новости.
    Только 4 поля: заголовок, картинка, текст, категория.
    """

    class Meta:
        model = News
        fields = ['title', 'image_url', 'content', 'category', 'status', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок новости'
            }),
            'image_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/image.jpg'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 12,
                'placeholder': 'Полный текст новости...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Заголовок',
            'image_url': 'Ссылка на картинку (URL)',
            'content': 'Текст новости',
            'category': 'Категория',
            'status': 'Статус',
            'is_featured': 'Показать на главной',
        }