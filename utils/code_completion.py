"""
Автодополнение кода с помощью jedi для Python
"""

import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def get_python_completions(
    code: str,
    line: int,
    column: int,
    file_path: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Получить автодополнения для Python кода
    
    Args:
        code: Исходный код
        line: Номер строки (1-based)
        column: Номер колонки (0-based)
        file_path: Путь к файлу (опционально)
    
    Returns:
        Список автодополнений с полями 'name', 'complete', 'type', 'description'
    """
    try:
        import jedi
        
        script = jedi.Script(code, line, column, path=file_path)
        completions = script.complete()
        
        results = []
        for completion in completions:
            results.append({
                'name': completion.name,
                'complete': completion.complete,
                'type': completion.type,
                'description': completion.description or '',
                'docstring': completion.docstring() if hasattr(completion, 'docstring') else ''
            })
        
        return results
    except ImportError:
        logger.warning("jedi не установлен. Установите: pip install jedi")
        return []
    except Exception as e:
        logger.error(f"Ошибка получения автодополнений: {e}", exc_info=True)
        return []


def get_simple_completions(
    code: str,
    line: int,
    column: int,
    language: str = 'python'
) -> List[str]:
    """
    Простое автодополнение на основе ключевых слов языка
    
    Args:
        code: Исходный код
        line: Номер строки
        column: Номер колонки
        language: Язык программирования
    
    Returns:
        Список возможных дополнений
    """
    # Получаем текущее слово
    lines = code.split('\n')
    if line > len(lines):
        return []
    
    current_line = lines[line - 1]
    word_start = column
    while word_start > 0 and (current_line[word_start - 1].isalnum() or current_line[word_start - 1] == '_'):
        word_start -= 1
    
    current_word = current_line[word_start:column]
    
    # Ключевые слова для разных языков
    keywords = {
        'python': [
            'def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while',
            'try', 'except', 'finally', 'with', 'as', 'return', 'yield', 'pass',
            'break', 'continue', 'lambda', 'and', 'or', 'not', 'in', 'is', 'None',
            'True', 'False', 'self', 'super'
        ],
        'javascript': [
            'function', 'class', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
            'try', 'catch', 'finally', 'return', 'async', 'await', 'import', 'export',
            'default', 'this', 'super', 'new', 'typeof', 'instanceof'
        ]
    }
    
    lang_keywords = keywords.get(language, [])
    
    # Фильтруем по текущему слову
    completions = [kw for kw in lang_keywords if kw.startswith(current_word)]
    
    return completions[:10]  # Ограничиваем количество

