"""
Компоненты IDE для GUI и Web интерфейсов
Файловый браузер, редактор кода с подсветкой синтаксиса
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class SyntaxHighlighter:
    """Простая подсветка синтаксиса для разных языков"""
    
    # Цвета для подсветки
    COLORS = {
        'keyword': '#569cd6',
        'string': '#ce9178',
        'comment': '#6a9955',
        'function': '#dcdcaa',
        'number': '#b5cea8',
        'operator': '#d4d4d4',
        'default': '#d4d4d4',
    }
    
    # Ключевые слова для разных языков
    KEYWORDS = {
        'python': {
            'keywords': r'\b(and|as|assert|break|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|not|or|pass|print|raise|return|try|while|with|yield|True|False|None)\b',
            'functions': r'\b(def|class)\s+(\w+)',
            'strings': r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
            'comments': r'(#.*)',
            'numbers': r'\b\d+\.?\d*\b',
        },
        'javascript': {
            'keywords': r'\b(const|let|var|function|class|extends|if|else|for|while|return|import|export|default|async|await|try|catch|finally|throw|new|this|super|static|typeof|instanceof)\b',
            'functions': r'\b(function|const|let|var)\s+(\w+)\s*=',
            'strings': r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'|`(?:[^`\\]|\\.)*`)',
            'comments': r'(//.*|/\*[\s\S]*?\*/)',
            'numbers': r'\b\d+\.?\d*\b',
        },
        'html': {
            'tags': r'(&lt;/?\w+[^&gt;]*&gt;)',
            'attributes': r'(\w+)=',
            'strings': r'("(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\')',
            'comments': r'(<!--[\s\S]*?-->)',
        },
        'css': {
            'properties': r'(\w+)\s*:',
            'selectors': r'([.#]?\w+)\s*\{',
            'values': r':\s*([^;]+)',
            'comments': r'(/\*[\s\S]*?\*/)',
        },
    }
    
    @staticmethod
    def detect_language(file_path: str) -> str:
        """Определение языка по расширению файла"""
        ext_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'javascript',
            '.tsx': 'javascript',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.json': 'javascript',
            '.yaml': 'python',
            '.yml': 'python',
        }
        ext = Path(file_path).suffix.lower()
        return ext_map.get(ext, 'text')
    
    @staticmethod
    def highlight_code(text: str, language: str) -> List[tuple]:
        """
        Возвращает список (start, end, tag) для подсветки
        tag - это имя тега для tkinter
        """
        if language not in SyntaxHighlighter.KEYWORDS:
            return []
        
        patterns = SyntaxHighlighter.KEYWORDS[language]
        highlights = []
        
        # Обрабатываем комментарии (приоритет)
        if 'comments' in patterns:
            for match in re.finditer(patterns['comments'], text, re.MULTILINE):
                highlights.append((match.start(), match.end(), 'comment'))
        
        # Ключевые слова
        if 'keywords' in patterns:
            for match in re.finditer(patterns['keywords'], text):
                start, end = match.span()
                # Проверяем, не в комментарии ли
                if not any(start >= cs and end <= ce for cs, ce, _ in highlights if _ == 'comment'):
                    highlights.append((start, end, 'keyword'))
        
        # Строки
        if 'strings' in patterns:
            for match in re.finditer(patterns['strings'], text):
                start, end = match.span()
                if not any(start >= cs and end <= ce for cs, ce, _ in highlights if _ == 'comment'):
                    highlights.append((start, end, 'string'))
        
        # Функции
        if 'functions' in patterns:
            for match in re.finditer(patterns['functions'], text):
                start = match.end(1) + 1  # После def/function
                end = match.end(2)  # Конец имени функции
                if not any(start >= cs and end <= ce for cs, ce, _ in highlights):
                    highlights.append((start, end, 'function'))
        
        # Числа
        if 'numbers' in patterns:
            for match in re.finditer(patterns['numbers'], text):
                start, end = match.span()
                if not any(start >= cs and end <= ce for cs, ce, _ in highlights if _ in ('comment', 'string')):
                    highlights.append((start, end, 'number'))
        
        return highlights


class FileBrowser:
    """Класс для работы с файловой системой"""
    
    @staticmethod
    def detect_language(file_path: str) -> str:
        """Определение языка по расширению файла"""
        return SyntaxHighlighter.detect_language(file_path)
    
    @staticmethod
    def get_file_tree(root_path: str, max_depth: int = 5) -> List[Dict]:
        """Возвращает дерево файлов и папок"""
        root = Path(root_path)
        if not root.exists():
            return []
        
        def walk_directory(path: Path, depth: int = 0) -> List[Dict]:
            """Рекурсивно обходит директорию и возвращает дерево"""
            if depth > max_depth:
                return []
            
            tree = []
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                for item in items:
                    # Пропускаем скрытые файлы и папки, а также служебные директории
                    if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', '.git']:
                        continue
                    
                    node = {
                        'name': item.name,
                        'path': str(item.relative_to(root)),
                        'full_path': str(item),
                        'type': 'directory' if item.is_dir() else 'file',
                        'children': []
                    }
                    
                    if item.is_file():
                        try:
                            node['size'] = item.stat().st_size
                        except:
                            node['size'] = 0
                    
                    if item.is_dir():
                        # Рекурсивно получаем дочерние элементы
                        node['children'] = walk_directory(item, depth + 1)
                    
                    tree.append(node)
            except (PermissionError, OSError):
                pass
            
            return tree
        
        return walk_directory(root)
    
    @staticmethod
    def get_file_content(file_path: str) -> Optional[str]:
        """Читает содержимое файла с безопасной обработкой кодировок"""
        try:
            from utils.file_utils import read_file_safe
            path = Path(file_path)
            return read_file_safe(path, max_size=10*1024*1024)  # 10MB максимум
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Ошибка чтения файла {file_path}: {e}", exc_info=True)
            return None
    
    @staticmethod
    def save_file(file_path: str, content: str) -> bool:
        """Сохраняет содержимое в файл с безопасной обработкой"""
        try:
            from utils.file_utils import write_file_safe
            path = Path(file_path)
            return write_file_safe(path, content, encoding='utf-8', create_dirs=True)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка сохранения файла {file_path}: {e}", exc_info=True)
            return False