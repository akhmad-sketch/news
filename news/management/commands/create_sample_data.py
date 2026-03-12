"""
create_sample_data.py — команда для заполнения БД тестовыми данными

Запуск: python manage.py create_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from news.models import Category, News, Comment
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Создаёт тестовые данные для демонстрации проекта'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Создаём тестовые данные...')

        # ── Создаём суперпользователя ────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                password='admin123',
                email='admin@example.com',
                first_name='Администратор',
                last_name='Системы',
                is_staff=True
            )
            UserProfile.objects.create(user=admin, bio='Администратор системы')
            self.stdout.write(self.style.SUCCESS('  ✅ Создан admin (пароль: admin123)'))

        # ── Создаём обычного пользователя ────────────────────────────────────
        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user(
                username='student',
                password='student123',
                email='student@example.com',
                first_name='Студент',
                last_name='Иванов'
            )
            UserProfile.objects.create(user=student, bio='Обычный пользователь')
            self.stdout.write(self.style.SUCCESS('  ✅ Создан student (пароль: student123)'))

        # ── Создаём категории ────────────────────────────────────────────────
        categories_data = [
            ('Технологии', 'technology', 'bi-laptop', 'Новости мира технологий и IT'),
            ('Наука',      'science',    'bi-flask',  'Научные открытия и исследования'),
            ('Спорт',      'sport',      'bi-trophy', 'Спортивные события и результаты'),
            ('Политика',   'politics',   'bi-globe',  'Политические события в мире'),
            ('Культура',   'culture',    'bi-palette','Культура, искусство, кино'),
        ]

        categories = {}
        for name, slug, icon, desc in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'description': desc}
            )
            categories[slug] = cat
            if created:
                self.stdout.write(f'  ✅ Категория: {name}')

        # ── Создаём новости ──────────────────────────────────────────────────
        admin_user = User.objects.get(username='admin')

        news_data = [
            {
                'title': 'Django 5.0: Что нового в новой версии фреймворка',
                'slug': 'django-5-new-features',
                'short_description': 'Разработчики Django выпустили версию 5.0 с рядом значительных улучшений и новых возможностей для веб-разработки.',
                'content': '''Django 5.0 представляет собой значительный шаг вперёд в развитии популярного Python веб-фреймворка.

Основные нововведения:

1. Улучшенная система форм с поддержкой field groups
2. Новые возможности для работы с базами данных
3. Оптимизированная система маршрутизации URL
4. Улучшенная производительность ORM запросов

Django остаётся одним из самых популярных веб-фреймворков для Python благодаря принципу "batteries included" — всё необходимое уже включено в коробку.

Для обновления до версии 5.0 используйте команду:
pip install --upgrade Django==5.0

Полная документация доступна на официальном сайте Django.''',
                'category': categories['technology'],
                'is_featured': True,
                'status': 'published',
            },
            {
                'title': 'PostgreSQL vs MongoDB: Когда использовать какую базу данных?',
                'slug': 'postgresql-vs-mongodb',
                'short_description': 'Подробное сравнение реляционных и нереляционных баз данных на примере реального проекта.',
                'content': '''Выбор базы данных — одно из важнейших архитектурных решений при разработке приложения.

PostgreSQL — реляционная база данных:
- Строгая схема данных
- ACID транзакции
- Мощные JOIN-запросы
- Идеально для структурированных данных

MongoDB — документная NoSQL база:
- Гибкая схема (JSON-подобные документы)
- Горизонтальное масштабирование
- Быстрые операции с большими объёмами данных
- Идеально для аналитики и логов

В нашем проекте NewsPortal мы используем обе базы данных:
- PostgreSQL хранит основной контент: новости, пользователей, комментарии
- MongoDB хранит статистику: просмотры, рейтинги, история активности

Такая гибридная архитектура позволяет получить преимущества обоих подходов.''',
                'category': categories['technology'],
                'is_featured': True,
                'status': 'published',
            },
            {
                'title': 'Учёные открыли новый метод хранения данных в ДНК',
                'slug': 'dna-data-storage',
                'short_description': 'Международная группа учёных разработала новый способ хранения цифровых данных в молекулах ДНК.',
                'content': '''Учёные из нескольких ведущих университетов мира представили революционную технологию хранения данных.

Метод основан на кодировании бинарных данных в последовательности нуклеотидов ДНК. Теоретически, в одном грамме ДНК можно хранить до 215 петабайт информации.

Преимущества ДНК-хранилищ:
- Невероятная плотность хранения данных
- Срок хранения тысячи лет
- Низкое потребление энергии

Исследование опубликовано в журнале Nature Biotechnology и уже привлекло внимание крупнейших технологических компаний.''',
                'category': categories['science'],
                'is_featured': False,
                'status': 'published',
            },
            {
                'title': 'Чемпионат мира по футболу 2026: Расписание и группы',
                'slug': 'world-cup-2026-schedule',
                'short_description': 'Опубликовано полное расписание матчей Чемпионата мира по футболу 2026 года.',
                'content': '''Чемпионат мира по футболу 2026 пройдёт в трёх странах: США, Канаде и Мексике.

Впервые в истории турнир примет 48 сборных, разбитых на 12 групп по 4 команды. Это увеличит число матчей до 104.

Ключевые даты:
- Старт группового этапа: 11 июня 2026
- Финал: 19 июля 2026 в Нью-Йорке

Казахстан впервые в истории квалифицировался на Чемпионат мира, одержав победу в квалификационном турнире.

Болельщики со всего мира готовятся к самому масштабному спортивному событию в истории.''',
                'category': categories['sport'],
                'is_featured': False,
                'status': 'published',
            },
            {
                'title': 'ИИ в искусстве: Граница между творчеством и технологией',
                'slug': 'ai-in-art',
                'short_description': 'Как искусственный интеллект меняет мир изобразительного искусства и что думают об этом художники.',
                'content': '''Искусственный интеллект всё активнее проникает в творческие профессии, вызывая споры в художественном сообществе.

С одной стороны, ИИ-инструменты позволяют создавать удивительные визуальные образы за считанные секунды. Нейросети вроде Midjourney и DALL-E открыли возможность "рисования" людям без художественного образования.

С другой стороны, профессиональные художники выражают обеспокоенность:
- Нейросети обучаются на чужих работах без согласия авторов
- Рынок иллюстраций становится менее прибыльным
- Размывается понятие авторства

Несмотря на споры, многие художники находят способы сотрудничества с ИИ, используя его как инструмент, а не замену творчества.''',
                'category': categories['culture'],
                'is_featured': True,
                'status': 'published',
            },
        ]

        for news_info in news_data:
            _, created = News.objects.get_or_create(
                slug=news_info['slug'],
                defaults={**news_info, 'author': admin_user}
            )
            if created:
                self.stdout.write(f'  ✅ Новость: {news_info["title"][:50]}...')

        # ── Создаём комментарии ──────────────────────────────────────────────
        if News.objects.exists():
            student = User.objects.get(username='student')
            first_news = News.objects.first()

            if not Comment.objects.filter(news=first_news).exists():
                Comment.objects.create(
                    news=first_news,
                    author=student,
                    text='Отличная статья! Очень полезная информация для изучения Django.'
                )
                Comment.objects.create(
                    news=first_news,
                    author=admin_user,
                    text='Спасибо! Этот проект создан специально для студентов.'
                )
                self.stdout.write('  ✅ Добавлены тестовые комментарии')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✨ Тестовые данные успешно созданы!'))
        self.stdout.write('')
        self.stdout.write('Учётные данные:')
        self.stdout.write('  Администратор: admin / admin123')
        self.stdout.write('  Пользователь:  student / student123')
