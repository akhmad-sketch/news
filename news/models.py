"""
models.py — модели приложения news для PostgreSQL
Упрощённая версия: заголовок, URL картинки, контент, категория
"""

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import re


class Category(models.Model):
    """Категория новостей. Пример: Технологии, Спорт, Политика"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    icon = models.CharField(
        max_length=50, blank=True, default='bi-folder',
        verbose_name="Иконка Bootstrap",
        help_text="Например: bi-globe, bi-laptop, bi-trophy"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._transliterate(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:by_category', kwargs={'slug': self.slug})

    @staticmethod
    def _transliterate(text):
        translit_map = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
            'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i',
            'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
            'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
            'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
            'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '',
            'э': 'e', 'ю': 'yu', 'я': 'ya',
        }
        result = text.lower()
        for ru, en in translit_map.items():
            result = result.replace(ru, en)
        result = re.sub(r'[^a-z0-9]+', '-', result)
        return result.strip('-')


class News(models.Model):
    """
    Модель новости — только самое необходимое:
    - Заголовок
    - Ссылка на картинку (URL)
    - Текст новости
    - Категория
    """

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_PUBLISHED, 'Опубликовано'),
    ]

    # ── Основные поля ──────────────────────────────────────────
    title = models.CharField(
        max_length=300,
        verbose_name="Заголовок"
    )
    slug = models.SlugField(
        max_length=300,
        unique=True,
        blank=True,
        verbose_name="URL (заполняется автоматически)"
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на картинку",
        help_text="Вставьте URL изображения, например: https://example.com/image.jpg"
    )
    content = models.TextField(
        verbose_name="Текст новости"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_list',
        verbose_name="Категория"
    )

    # ── Служебные поля ─────────────────────────────────────────
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='news_articles',
        verbose_name="Автор"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PUBLISHED,
        verbose_name="Статус"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Главная новость"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Автоматически генерируем slug из заголовка."""
        if not self.slug:
            base_slug = Category._transliterate(self.title)
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})

    @property
    def published_comments_count(self):
        return self.comments.filter(is_approved=True).count()


class Comment(models.Model):
    """Комментарий к новости."""
    news = models.ForeignKey(
        News, on_delete=models.CASCADE,
        related_name='comments', verbose_name="Новость"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments', verbose_name="Автор"
    )
    text = models.TextField(verbose_name="Текст комментария")
    is_approved = models.BooleanField(default=True, verbose_name="Одобрен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ['created_at']

    def __str__(self):
        return f"Комментарий от {self.author.username} к '{self.news.title[:30]}'"