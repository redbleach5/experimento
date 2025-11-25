"""
Утилиты для форматирования кода
"""

import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def format_python_code(code: str) -> Optional[str]:
    """
    Форматирование Python кода с помощью black
    
    Args:
        code: Исходный код
    
    Returns:
        Отформатированный код или None в случае ошибки
    """
    try:
        import black
        mode = black.FileMode()
        formatted = black.format_str(code, mode=mode)
        return formatted
    except ImportError:
        logger.warning("black не установлен. Установите: pip install black")
        return None
    except Exception as e:
        logger.error(f"Ошибка форматирования Python кода: {e}", exc_info=True)
        return None


def format_js_code(code: str) -> Optional[str]:
    """
    Форматирование JavaScript/TypeScript кода с помощью prettier
    
    Args:
        code: Исходный код
    
    Returns:
        Отформатированный код или None в случае ошибки
    """
    try:
        # Проверяем наличие prettier
        result = subprocess.run(
            ['prettier', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            logger.warning("prettier не найден. Установите: npm install -g prettier")
            return None
        
        # Форматируем через prettier
        process = subprocess.Popen(
            ['prettier', '--stdin-filepath', 'file.js'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=code, timeout=10)
        
        if process.returncode == 0:
            return stdout
        else:
            logger.error(f"Ошибка prettier: {stderr}")
            return None
            
    except FileNotFoundError:
        logger.warning("prettier не найден. Установите: npm install -g prettier")
        return None
    except subprocess.TimeoutExpired:
        logger.error("Таймаут форматирования кода")
        return None
    except Exception as e:
        logger.error(f"Ошибка форматирования JS кода: {e}", exc_info=True)
        return None


def format_code(code: str, language: str) -> Optional[str]:
    """
    Форматирование кода в зависимости от языка
    
    Args:
        code: Исходный код
        language: Язык программирования ('python', 'javascript', 'typescript')
    
    Returns:
        Отформатированный код или None
    """
    if language == 'python':
        return format_python_code(code)
    elif language in ['javascript', 'typescript', 'js', 'ts']:
        return format_js_code(code)
    else:
        logger.warning(f"Форматирование для языка {language} не поддерживается")
        return None

