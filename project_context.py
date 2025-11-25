"""
Модуль для автоматической загрузки и управления контекстом проекта
Позволяет моделям видеть структуру проекта и работать с файлами
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
import yaml
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)


class ProjectContext:
    """Класс для управления контекстом проекта"""
    
    def __init__(self, project_root: str = "."):
        """
        Инициализация контекста проекта
        
        Args:
            project_root: Корневая директория проекта
        """
        self.project_root = Path(project_root).resolve()
        self.context_cache: Dict[str, any] = {}
        self.ignored_patterns: Set[str] = {
            '__pycache__', '.git', '.venv', 'venv', 'node_modules',
            '.pytest_cache', '.mypy_cache', '.idea', '.vscode',
            '*.pyc', '*.pyo', '*.pyd', '.DS_Store', '*.egg-info'
        }
    
    def get_project_structure(self, max_depth: int = 3, include_files: bool = True) -> str:
        """
        Получает структуру проекта в виде текста
        
        Args:
            max_depth: Максимальная глубина вложенности
            include_files: Включать ли файлы (или только директории)
        
        Returns:
            Текстовая структура проекта
        """
        lines = [f"Структура проекта: {self.project_root.name}\n"]
        lines.append("=" * 60)
        
        def build_tree(path: Path, prefix: str = "", depth: int = 0):
            if depth > max_depth:
                return
            
            try:
                items = sorted(
                    [item for item in path.iterdir() 
                     if not any(item.name.startswith(pat.replace('*', '')) 
                               for pat in self.ignored_patterns)],
                    key=lambda x: (x.is_file(), x.name.lower())
                )
                
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{current_prefix}{item.name}")
                    
                    if item.is_dir():
                        extension = "    " if is_last else "│   "
                        build_tree(item, prefix + extension, depth + 1)
                    elif include_files and item.is_file():
                        # Показываем размер файла
                        try:
                            size = item.stat().st_size
                            size_str = self._format_size(size)
                            lines[-1] += f" ({size_str})"
                        except (OSError, IOError) as e:
                            logger.debug(f"Ошибка получения размера файла {item}: {e}")
            except PermissionError as e:
                logger.warning(f"Нет доступа к директории {path}: {e}")
        
        build_tree(self.project_root)
        return "\n".join(lines)
    
    def get_readme_content(self) -> Optional[str]:
        """Получает содержимое README файла"""
        readme_names = ['README.md', 'README.txt', 'README.rst', 'README']
        
        for name in readme_names:
            readme_path = self.project_root / name
            if readme_path.exists() and readme_path.is_file():
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return f"README ({name}):\n{content}"
                except (OSError, IOError, UnicodeDecodeError) as e:
                    logger.warning(f"Ошибка чтения README {name}: {e}")
                    return f"README ({name}): [Ошибка чтения: {e}]"
        
        return None
    
    def get_config_files(self) -> Dict[str, str]:
        """Получает содержимое конфигурационных файлов"""
        config_files = {}
        config_names = [
            'config.yaml', 'config.yml', 'pyproject.toml', 'setup.py',
            'requirements.txt', 'package.json', 'Cargo.toml', 'go.mod',
            '.env.example', 'docker-compose.yml', 'Dockerfile'
        ]
        
        for name in config_names:
            config_path = self.project_root / name
            if config_path.exists() and config_path.is_file():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Ограничиваем размер для больших файлов
                    if len(content) > 5000:
                        content = content[:5000] + "\n... [файл обрезан]"
                    config_files[name] = content
                except (OSError, IOError, UnicodeDecodeError) as e:
                    logger.debug(f"Ошибка чтения конфига {name}: {e}")
                    pass
        
        return config_files
    
    def get_main_files(self, extensions: List[str] = None) -> Dict[str, str]:
        """
        Получает содержимое основных файлов проекта
        
        Args:
            extensions: Список расширений файлов для включения
                      (по умолчанию: .py, .js, .ts, .jsx, .tsx, .java, .go, .rs)
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.cpp', '.c']
        
        main_files = {}
        
        # Ищем файлы с основными именами
        main_names = [
            'main', 'app', 'index', 'server', 'client', 'init',
            'run', 'start', 'entry', 'entrypoint'
        ]
        
        for ext in extensions:
            for name in main_names:
                for pattern in [f"{name}{ext}", f"{name}.{ext.lstrip('.')}"]:
                    file_path = self.project_root / pattern
                    if file_path.exists() and file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            # Ограничиваем размер
                            if len(content) > 10000:
                                content = content[:10000] + "\n... [файл обрезан]"
                            main_files[str(file_path.relative_to(self.project_root))] = content
                        except (OSError, IOError, UnicodeDecodeError) as e:
                            logger.debug(f"Ошибка чтения файла {pattern}: {e}")
                            pass
        
        # Также получаем файлы из корня проекта
        for item in self.project_root.iterdir():
            if item.is_file() and item.suffix in extensions:
                rel_path = str(item.relative_to(self.project_root))
                if rel_path not in main_files:
                    try:
                        with open(item, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if len(content) > 10000:
                            content = content[:10000] + "\n... [файл обрезан]"
                        main_files[rel_path] = content
                    except (OSError, IOError, UnicodeDecodeError) as e:
                        logger.debug(f"Ошибка чтения файла {item}: {e}")
                        pass
        
        return main_files
    
    def get_project_summary(self, max_chars: int = 2000) -> str:
        """
        Получает краткое описание проекта
        
        Args:
            max_chars: Максимальное количество символов (по умолчанию 3000)
        """
        summary_parts = []
        
        # Для очень маленьких моделей - только структура
        if max_chars < 1500:
            structure = self.get_project_structure(max_depth=1, include_files=False)
            summary_parts.append(structure[:max_chars] if len(structure) > max_chars else structure)
            result = "\n".join(summary_parts)
            if len(result) > max_chars:
                result = result[:max_chars] + "\n... [Контекст обрезан]"
            return result
        
        # Структура проекта (ограниченная)
        structure = self.get_project_structure(max_depth=2, include_files=False)
        structure_limit = min(800, max_chars // 3)
        summary_parts.append(structure[:structure_limit] if len(structure) > structure_limit else structure)
        summary_parts.append("")
        
        # README (ограниченный)
        readme = self.get_readme_content()
        if readme:
            readme_limit = min(600, max_chars // 4)
            if len(readme) > readme_limit:
                readme = readme[:readme_limit] + "\n... [README обрезан]"
            summary_parts.append(readme)
            summary_parts.append("")
        
        # Конфигурационные файлы (только важные, ограниченные)
        configs = self.get_config_files()
        if configs:
            summary_parts.append("Конфигурационные файлы:")
            summary_parts.append("-" * 60)
            remaining_chars = max_chars - len("\n".join(summary_parts))
            config_limit_per_file = min(300, remaining_chars // (len(configs) + 1))
            
            for name, content in list(configs.items())[:2]:  # Только первые 2
                if len(content) > config_limit_per_file:
                    content = content[:config_limit_per_file] + "\n... [файл обрезан]"
                summary_parts.append(f"\n{name}:")
                summary_parts.append(content)
                summary_parts.append("")
        
        # Основные файлы (только первый, сильно ограниченный)
        main_files = self.get_main_files()
        if main_files:
            remaining_chars = max_chars - len("\n".join(summary_parts))
            if remaining_chars > 200:
                summary_parts.append("Основной файл:")
                summary_parts.append("-" * 60)
                path, content = list(main_files.items())[0]
                file_limit = min(400, remaining_chars - 100)
                if len(content) > file_limit:
                    content = content[:file_limit] + "\n... [файл обрезан]"
                summary_parts.append(f"\n{path}:")
                summary_parts.append("```")
                summary_parts.append(content)
                summary_parts.append("```")
                summary_parts.append("")
        
        result = "\n".join(summary_parts)
        
        # Если результат слишком длинный, обрезаем
        if len(result) > max_chars:
            result = result[:max_chars] + "\n\n... [Контекст проекта обрезан для экономии токенов]"
        
        return result
    
    @lru_cache(maxsize=128)
    def get_file_content(self, file_path: str, max_size: int = 50000) -> Optional[str]:
        """
        Получает содержимое файла с кэшированием
        
        Args:
            file_path: Путь к файлу (относительно project_root или абсолютный)
            max_size: Максимальный размер файла для чтения (в байтах)
        
        Returns:
            Содержимое файла или None
        """
        from utils.file_utils import read_file_safe
        
        path = Path(file_path)
        project_root_resolved = self.project_root.resolve()
        
        # Нормализуем путь
        if not path.is_absolute():
            path = project_root_resolved / path
        else:
            # Если абсолютный путь, проверяем что он в project_root
            if not str(path.resolve()).startswith(str(project_root_resolved)):
                logger.warning(f"Попытка доступа к файлу вне project_root: {file_path}")
                return None
        
        path = path.resolve()
        
        # Строгая проверка - путь должен быть внутри project_root
        try:
            relative = path.relative_to(project_root_resolved)
            # Дополнительная проверка - не должно быть .. в относительном пути
            if '..' in str(relative) or str(relative).startswith('..'):
                logger.warning(f"Path traversal detected в пути: {file_path}")
                return None
        except ValueError:
            # Путь не находится внутри project_root
            logger.warning(f"Попытка доступа к файлу вне project_root: {file_path}")
            return None
        
        if not path.exists() or not path.is_file():
            return None
        
        # Проверяем размер
        try:
            if path.stat().st_size > max_size:
                return f"[Файл слишком большой: {self._format_size(path.stat().st_size)}]"
        except (OSError, IOError) as e:
            logger.warning(f"Ошибка проверки размера файла {file_path}: {e}")
            return None
        
        # Используем безопасное чтение с автоматическим определением кодировки
        content = read_file_safe(path, max_size=max_size)
        return content
    
    def invalidate_cache(self):
        """Очистка кэша при изменении проекта"""
        self.get_file_content.cache_clear()
        logger.debug("Кэш файлов очищен")
    
    def find_files_by_pattern(self, pattern: str) -> List[str]:
        """
        Находит файлы по паттерну
        
        Args:
            pattern: Паттерн для поиска (например, "*.py", "test_*")
        
        Returns:
            Список путей к найденным файлам
        """
        found_files = []
        
        # Простой поиск по имени
        for item in self.project_root.rglob(pattern):
            if item.is_file():
                rel_path = str(item.relative_to(self.project_root))
                if not any(ignored in rel_path for ignored in self.ignored_patterns):
                    found_files.append(rel_path)
        
        return found_files
    
    def get_relevant_files_for_query(self, query: str, max_files: int = 3, max_file_size: int = 1500, max_depth: int = 5) -> Dict[str, str]:
        """
        Находит релевантные файлы для запроса
        
        Args:
            query: Текст запроса
            max_files: Максимальное количество файлов (по умолчанию 3)
            max_file_size: Максимальный размер каждого файла в символах (по умолчанию 1500)
            max_depth: Максимальная глубина поиска (по умолчанию 5)
        
        Returns:
            Словарь {путь: содержимое}
        """
        query_lower = query.lower()
        relevant_files = {}
        
        # Ключевые слова для поиска
        keywords = []
        for word in query_lower.split():
            if len(word) > 3:  # Игнорируем короткие слова
                keywords.append(word)
        
        # Константы для ограничений
        MAX_FILE_SIZE_FOR_SEARCH = 100 * 1024  # 100KB
        
        # Ищем файлы с ограничением глубины
        for depth in range(max_depth + 1):
            if len(relevant_files) >= max_files:
                break
            
            # Строим паттерн для поиска на определенной глубине
            if depth == 0:
                pattern = "*"
            else:
                pattern = "*/" * depth + "*"
            
            try:
                for item in self.project_root.glob(pattern):
                    if item.is_file() and len(relevant_files) < max_files:
                        # Пропускаем большие файлы и бинарные
                        try:
                            if item.stat().st_size > MAX_FILE_SIZE_FOR_SEARCH:
                                continue
                        except (OSError, IOError, PermissionError) as e:
                            logger.debug(f"Ошибка проверки размера файла {item}: {e}")
                            continue
                        
                        # Проверяем имя файла
                        name_lower = item.name.lower()
                        if any(kw in name_lower for kw in keywords):
                            content = self.get_file_content(str(item.relative_to(self.project_root)), max_size=50000)
                            if content:
                                # Ограничиваем размер содержимого
                                if len(content) > max_file_size:
                                    content = content[:max_file_size] + "\n... [файл обрезан]"
                                relevant_files[str(item.relative_to(self.project_root))] = content
                                continue
                        
                        # Проверяем содержимое (только для текстовых файлов)
                        if item.suffix in ['.py', '.js', '.ts', '.md', '.txt', '.yaml', '.yml']:
                            try:
                                content = self.get_file_content(str(item.relative_to(self.project_root)), max_size=50000)
                                if content and any(kw in content.lower() for kw in keywords):
                                    # Ограничиваем размер содержимого
                                    if len(content) > max_file_size:
                                        content = content[:max_file_size] + "\n... [файл обрезан]"
                                    relevant_files[str(item.relative_to(self.project_root))] = content
                            except (OSError, IOError, UnicodeDecodeError) as e:
                                logger.debug(f"Ошибка чтения содержимого {item}: {e}")
                                continue
            except (OSError, IOError, PermissionError) as e:
                logger.debug(f"Ошибка поиска на глубине {depth}: {e}")
                continue
        
        return relevant_files
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Форматирует размер файла"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


def load_project_context(project_root: str = ".") -> ProjectContext:
    """
    Загружает контекст проекта
    
    Args:
        project_root: Корневая директория проекта
    
    Returns:
        Объект ProjectContext
    """
    return ProjectContext(project_root)

