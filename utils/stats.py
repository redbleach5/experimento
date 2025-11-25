"""
Статистика и аналитика использования
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)

STATS_FILE = Path('logs/stats.json')


class StatsCollector:
    """Сборщик статистики"""
    
    def __init__(self, stats_file: Path = STATS_FILE):
        self.stats_file = stats_file
        self.stats_file.parent.mkdir(exist_ok=True)
        self.stats: Dict = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Загрузить статистику из файла"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Ошибка загрузки статистики: {e}")
        
        return {
            'total_requests': 0,
            'total_tokens': 0,
            'total_time': 0.0,
            'requests_by_model': defaultdict(int),
            'requests_by_provider': defaultdict(int),
            'average_response_time': 0.0,
            'requests_today': 0,
            'last_request_date': None,
            'popular_queries': defaultdict(int)
        }
    
    def _save_stats(self):
        """Сохранить статистику в файл"""
        try:
            # Конвертируем defaultdict в обычный dict для JSON
            stats_to_save = {}
            for key, value in self.stats.items():
                if isinstance(value, defaultdict):
                    stats_to_save[key] = dict(value)
                else:
                    stats_to_save[key] = value
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(stats_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}", exc_info=True)
    
    def record_request(
        self,
        model: str,
        provider: str,
        tokens: int,
        response_time: float,
        query: Optional[str] = None
    ):
        """Записать запрос в статистику"""
        today = datetime.now().date().isoformat()
        
        # Обновляем общую статистику
        self.stats['total_requests'] += 1
        self.stats['total_tokens'] += tokens
        self.stats['total_time'] += response_time
        
        # Статистика по моделям и провайдерам
        self.stats['requests_by_model'][model] += 1
        self.stats['requests_by_provider'][provider] += 1
        
        # Среднее время ответа
        if self.stats['total_requests'] > 0:
            self.stats['average_response_time'] = (
                self.stats['total_time'] / self.stats['total_requests']
            )
        
        # Запросы за сегодня
        if self.stats['last_request_date'] != today:
            self.stats['requests_today'] = 1
        else:
            self.stats['requests_today'] += 1
        self.stats['last_request_date'] = today
        
        # Популярные запросы
        if query:
            # Берем первые 50 символов
            query_short = query[:50]
            self.stats['popular_queries'][query_short] += 1
        
        self._save_stats()
    
    def get_stats(self) -> Dict:
        """Получить статистику"""
        return self.stats.copy()
    
    def get_summary(self) -> str:
        """Получить текстовую сводку статистики"""
        stats = self.stats
        summary = f"""
Статистика использования:
- Всего запросов: {stats['total_requests']}
- Всего токенов: {stats['total_tokens']:,}
- Среднее время ответа: {stats['average_response_time']:.2f}с
- Запросов сегодня: {stats['requests_today']}

Популярные модели:
"""
        # Топ-3 модели
        models = sorted(
            stats['requests_by_model'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        for model, count in models:
            summary += f"  - {model}: {count} запросов\n"
        
        return summary

