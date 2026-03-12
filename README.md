# 📰 NewsPortal — Учебный проект на Django + PostgreSQL + MongoDB

> **Цель проекта:** Демонстрация гибридной архитектуры с двумя базами данных в Django.
> Подходит для курсовой / лабораторной работы по дисциплинам "Базы данных" и "Веб-разработка".

---

## 🏗️ Архитектура проекта

```
┌─────────────────────────────────────────────────────────────┐
│                    КЛИЕНТ (Браузер)                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP запрос
┌────────────────────────▼────────────────────────────────────┐
│                   Django Framework                           │
│  ┌──────────┐   ┌──────────────┐   ┌────────────────────┐   │
│  │  URLs    │──▶│    Views     │──▶│    Templates       │   │
│  │ (роутер) │   │(контроллеры) │   │  (HTML + Bootstrap)│   │
│  └──────────┘   └──────┬───┬──┘   └────────────────────┘   │
└─────────────────────────│───│──────────────────────────────-┘
                          │   │
            ┌─────────────┘   └──────────────────┐
            │                                     │
┌───────────▼────────────┐         ┌──────────────▼───────────┐
│    PostgreSQL           │         │        MongoDB            │
│  (Реляционная БД)       │         │   (Документная NoSQL БД)  │
│                         │         │                           │
│  ┌─────────────────┐    │         │  ┌────────────────────┐   │
│  │ Users           │    │         │  │ news_views         │   │
│  │ id, username    │    │         │  │ {                  │   │
│  │ email, password │    │         │  │   news_id: 42,     │   │
│  └────────┬────────┘    │         │  │   views_count: 157,│   │
│           │             │         │  │   last_viewed: ...,│   │
│  ┌────────▼────────┐    │         │  │   unique_ips: [...] │  │
│  │ News            │    │         │  │ }                  │   │
│  │ id, title       │    │         │  └────────────────────┘   │
│  │ content, slug   │    │         │                           │
│  │ author_id (FK)  │    │         │  ┌────────────────────┐   │
│  │ category_id (FK)│    │         │  │ view_history       │   │
│  └────────┬────────┘    │         │  │ {                  │   │
│           │             │         │  │   news_id: 42,     │   │
│  ┌────────▼────────┐    │         │  │   user_id: 7,      │   │
│  │ Categories      │    │         │  │   ip: "1.2.3.4",   │   │
│  │ id, name, slug  │    │         │  │   viewed_at: date  │   │
│  └─────────────────┘    │         │  │ }                  │   │
│                         │         │  └────────────────────┘   │
│  ┌─────────────────┐    │         │                           │
│  │ Comments        │    │         │  Преимущества MongoDB:    │
│  │ id, text        │    │         │  ✅ Гибкая схема          │
│  │ news_id (FK)    │    │         │  ✅ Быстрый инкремент     │
│  │ author_id (FK)  │    │         │  ✅ Агрегация статистики  │
│  └─────────────────┘    │         │  ✅ Масштабируемость      │
│                         │         │                           │
│  Преимущества PostgreSQL│         └───────────────────────────┘
│  ✅ ACID транзакции     │
│  ✅ JOIN-запросы        │
│  ✅ Строгая схема       │
│  ✅ Целостность данных  │
└─────────────────────────┘
```

## 🗂️ Структура проекта

```
newsportal/
│
├── newsportal/              # Главный пакет Django проекта
│   ├── settings.py          # Конфигурация (2 БД, пути, приложения)
│   ├── urls.py              # Главный роутер URL
│   ├── wsgi.py              # WSGI для деплоя
│   └── mongo_client.py      # ★ Модуль работы с MongoDB
│
├── news/                    # Приложение: Новости
│   ├── models.py            # Модели: News, Category, Comment → PostgreSQL
│   ├── views.py             # Логика: список, детали, поиск, CRUD
│   ├── urls.py              # URL маршруты /news/, /category/, /search/
│   ├── forms.py             # Формы: CommentForm, NewsForm
│   ├── admin.py             # Регистрация в Django Admin
│   ├── context_processors.py # Категории во все шаблоны
│   └── management/
│       └── commands/
│           └── create_sample_data.py  # Команда заполнения тестовыми данными
│
├── accounts/                # Приложение: Пользователи
│   ├── models.py            # UserProfile (расширение User)
│   ├── views.py             # Регистрация, логин, профиль
│   ├── urls.py              # /accounts/register/, /login/, /profile/
│   ├── forms.py             # RegisterForm, LoginForm, ProfileForm
│   └── admin.py             # UserProfile в Admin
│
├── templates/               # HTML шаблоны с Bootstrap 5
│   ├── base.html            # Базовый шаблон (навбар, footer)
│   ├── news/
│   │   ├── news_list.html   # Главная страница и список по категории
│   │   ├── news_detail.html # ★ Страница новости (обе БД наглядно)
│   │   └── search_results.html
│   ├── accounts/
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── profile.html     # История просмотров из MongoDB
│   │   └── profile_edit.html
│   ├── admin_panel/
│   │   ├── dashboard.html   # Статистика из обеих БД
│   │   ├── news_form.html
│   │   └── news_confirm_delete.html
│   └── partials/
│       └── sidebar.html     # Популярные новости из MongoDB
│
├── static/
│   └── css/main.css         # Стили Bootstrap + кастомные
│
├── media/                   # Загружаемые файлы (изображения)
│
├── requirements.txt         # Зависимости Python
├── .env.example             # Пример переменных окружения
└── README.md                # Документация проекта
```

## 🚀 Быстрый старт

### 1. Клонируем и устанавливаем зависимости

```bash
# Создаём виртуальное окружение
python -m venv venv

# Активируем (Windows)
venv\Scripts\activate

# Активируем (Linux/Mac)
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 2. Настраиваем переменные окружения

```bash
# Копируем пример файла
cp .env.example .env

# Редактируем .env — указываем данные PostgreSQL
```

```env
SECRET_KEY=your-secret-key-change-me
DEBUG=True
POSTGRES_DB=newsportal_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
MONGO_URI=mongodb://localhost:27017/
MONGO_DB=newsportal_mongo
```

### 3. Создаём базу данных PostgreSQL

```sql
-- В psql или pgAdmin:
CREATE DATABASE newsportal_db;
```

### 4. Применяем миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Создаём тестовые данные

```bash
python manage.py create_sample_data
```

### 6. Запускаем сервер

```bash
python manage.py runserver
```

**Открываем в браузере:** http://127.0.0.1:8000

**Учётные данные:**
- Администратор: `admin` / `admin123`
- Пользователь: `student` / `student123`
- Django Admin: http://127.0.0.1:8000/admin/
- Панель управления: http://127.0.0.1:8000/admin-panel/

---

## 🗄️ Почему две базы данных?

### PostgreSQL (реляционная)
| Что хранит | Почему именно здесь |
|------------|---------------------|
| Users, профили | Строгая схема, авторизация через Django Auth |
| News, тексты | Нужны JOIN-запросы с автором и категорией |
| Categories | Нормализация, FK-связи |
| Comments | Связи с новостью и пользователем, целостность |

### MongoDB (документная NoSQL)
| Что хранит | Почему именно здесь |
|------------|---------------------|
| Счётчики просмотров | Частые `$inc` без блокировок таблицы |
| История просмотров | Растущая коллекция, гибкая структура документа |
| Популярные новости | Агрегационный pipeline, быстрая сортировка |

### Главное преимущество гибридного подхода
При каждом просмотре новости счётчик в MongoDB увеличивается атомарно (`$inc`) —
это не блокирует таблицу `news` в PostgreSQL и не создаёт нагрузку на реляционную БД.

---

## 🔧 Ключевые фрагменты кода

### Увеличение просмотров в MongoDB (mongo_client.py)
```python
collection.update_one(
    {'news_id': news_id},
    {
        '$inc': {'views_count': 1},       # Атомарный инкремент
        '$set': {'last_viewed': datetime.utcnow()},
        '$addToSet': {'unique_ips': ip}   # Уникальные IP
    },
    upsert=True  # Создать документ если не существует
)
```

### Получение популярных новостей (MongoDB Aggregation Pipeline)
```python
pipeline = [
    {'$sort': {'views_count': -1}},   # Сортировка по убыванию
    {'$limit': 5},                     # Топ-5
    {'$project': {'news_id': 1, 'views_count': 1}}
]
results = collection.aggregate(pipeline)
```

### Загрузка новости (views.py — два запроса к разным БД)
```python
# 1. Из PostgreSQL — текст и метаданные
news = get_object_or_404(News, slug=slug)

# 2. В MongoDB — увеличиваем счётчик
mongo_client.increment_views(news.id, user_id, ip_address)

# 3. Из MongoDB — читаем актуальное значение
views_count = mongo_client.get_views_count(news.id)
```

---

## 📊 Список URL маршрутов

| URL | Описание |
|-----|----------|
| `/` | Главная страница со списком новостей |
| `/news/<slug>/` | Страница отдельной новости |
| `/category/<slug>/` | Новости по категории |
| `/search/?q=текст` | Поиск по новостям |
| `/accounts/register/` | Регистрация |
| `/accounts/login/` | Вход в аккаунт |
| `/accounts/profile/` | Профиль пользователя |
| `/admin-panel/` | Панель управления (staff) |
| `/admin-panel/create/` | Создать новость |
| `/admin/` | Django Admin |
