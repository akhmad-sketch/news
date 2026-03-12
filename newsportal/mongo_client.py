"""
mongo_client.py — модуль для подключения к MongoDB
"""

from pymongo import MongoClient, DESCENDING
import logging

logger = logging.getLogger(__name__)

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DB_NAME = 'newsportal_mongo'


class MongoDBClient:
    """Клиент для работы с MongoDB."""

    def __init__(self):
        self._client = None
        self._db = None
        self._connect()

    def _connect(self):
        """Устанавливает соединение с MongoDB."""
        try:
            self._client = MongoClient(
                MONGO_URI,
                serverSelectionTimeoutMS=5000
            )
            # Проверка соединения
            self._client.admin.command('ping')
            self._db = self._client[MONGO_DB_NAME]
            print("✅ MongoDB подключена успешно")
        except Exception as e:
            print(f"⚠️  MongoDB недоступна: {e}")
            self._db = None

    def is_connected(self):
        """Проверяет доступность MongoDB."""
        if self._db is None:
            self._connect()
        try:
            self._client.admin.command('ping')
            return True
        except Exception:
            return False

    # ─────────────────────────────────────────────────────────────────────────
    # ПРОСМОТРЫ
    # ─────────────────────────────────────────────────────────────────────────

    def increment_views(self, news_id: int, user_id=None, ip_address=None):
        """Увеличивает счётчик просмотров новости."""
        if not self.is_connected():
            print("⚠️ MongoDB не подключена, просмотр не записан")
            return

        from datetime import datetime
        try:
            collection = self._db['news_views']
            collection.update_one(
                {'news_id': news_id},
                {
                    '$inc': {'views_count': 1},
                    '$set': {'last_viewed': datetime.utcnow()},
                    '$setOnInsert': {'created_at': datetime.utcnow()},
                },
                upsert=True
            )

            # История просмотров
            self._db['view_history'].insert_one({
                'news_id': news_id,
                'user_id': user_id,
                'ip_address': ip_address,
                'viewed_at': datetime.utcnow(),
            })

            print(f"✅ Просмотр записан: news_id={news_id}")

        except Exception as e:
            print(f"❌ Ошибка записи просмотра: {e}")

    def get_views_count(self, news_id: int) -> int:
        """Возвращает количество просмотров новости."""
        if not self.is_connected():
            return 0
        try:
            doc = self._db['news_views'].find_one({'news_id': news_id})
            return doc['views_count'] if doc else 0
        except Exception as e:
            print(f"❌ Ошибка получения просмотров: {e}")
            return 0

    def get_views_for_multiple(self, news_ids: list) -> dict:
        """Возвращает словарь {news_id: views_count} для списка новостей."""
        if not self.is_connected() or not news_ids:
            return {}
        try:
            docs = self._db['news_views'].find({'news_id': {'$in': news_ids}})
            return {doc['news_id']: doc['views_count'] for doc in docs}
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {}

    # ─────────────────────────────────────────────────────────────────────────
    # ПОПУЛЯРНЫЕ НОВОСТИ
    # ─────────────────────────────────────────────────────────────────────────

    def get_popular_news_ids(self, limit: int = 5) -> list:
        """Возвращает ID самых просматриваемых новостей."""
        if not self.is_connected():
            return []
        try:
            pipeline = [
                {'$sort': {'views_count': DESCENDING}},
                {'$limit': limit},
                {'$project': {'news_id': 1, 'views_count': 1, '_id': 0}}
            ]
            results = list(self._db['news_views'].aggregate(pipeline))
            return [(r['news_id'], r['views_count']) for r in results]
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return []

    def get_user_view_history(self, user_id: int, limit: int = 10) -> list:
        """Возвращает историю просмотров пользователя."""
        if not self.is_connected():
            return []
        try:
            records = self._db['view_history'].find(
                {'user_id': user_id},
                {'news_id': 1, '_id': 0}
            ).sort('viewed_at', DESCENDING).limit(limit)
            return [r['news_id'] for r in records]
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return []

    def get_stats_summary(self) -> dict:
        """Возвращает общую статистику."""
        if not self.is_connected():
            return {'total_views': 0, 'unique_news_viewed': 0}
        try:
            pipeline = [
                {'$group': {
                    '_id': None,
                    'total_views': {'$sum': '$views_count'},
                    'unique_news': {'$sum': 1}
                }}
            ]
            result = list(self._db['news_views'].aggregate(pipeline))
            if result:
                return {
                    'total_views': result[0]['total_views'],
                    'unique_news_viewed': result[0]['unique_news']
                }
            return {'total_views': 0, 'unique_news_viewed': 0}
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return {'total_views': 0, 'unique_news_viewed': 0}


# Глобальный экземпляр — создаётся один раз при запуске
mongo_client = MongoDBClient()