"""
Утилиты для безопасной работы с файлами
"""

import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

# Стандартные кодировки для попытки чтения
DEFAULT_ENCODINGS = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'cp866', 'iso-8859-1']


def read_file_safe(
    file_path: Path,
    max_size: int = 10 * 1024 * 1024,  # 10MB по умолчанию
    encodings: Optional[List[str]] = None,
    errors: str = 'replace'
) -> Optional[str]:
    """
    Безопасное чтение файла с автоматическим определением кодировки
    
    Args:
        file_path: Путь к файлу
        max_size: Максимальный размер файла в байтах
        encodings: Список кодировок для попытки (по умолчанию DEFAULT_ENCODINGS)
        errors: Обработка ошибок кодировки ('replace', 'ignore', 'strict')
    
    Returns:
        Содержимое файла или None в случае ошибки
    """
    if encodings is None:
        encodings = DEFAULT_ENCODINGS
    
    file_path = Path(file_path)
    
    # Проверка существования
    if not file_path.exists():
        logger.warning(f"Файл не найден: {file_path}")
        return None
    
    if not file_path.is_file():
        logger.warning(f"Путь не является файлом: {file_path}")
        return None
    
    # Проверка размера
    try:
        file_size = file_path.stat().st_size
        if file_size > max_size:
            logger.warning(f"Файл слишком большой: {file_path} ({file_size} bytes > {max_size} bytes)")
            return None
    except (OSError, IOError) as e:
        logger.error(f"Ошибка проверки размера файла {file_path}: {e}")
        return None
    
    # Попытка чтения с разными кодировками
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, errors=errors) as f:
                content = f.read()
            logger.debug(f"Файл {file_path} успешно прочитан с кодировкой {encoding}")
            return content
        except (UnicodeDecodeError, UnicodeError) as e:
            logger.debug(f"Не удалось прочитать {file_path} с кодировкой {encoding}: {e}")
            continue
        except (OSError, IOError, PermissionError) as e:
            logger.error(f"Ошибка чтения файла {file_path}: {e}")
            return None
    
    logger.error(f"Не удалось прочитать файл {file_path} ни с одной из кодировок")
    return None


def write_file_safe(
    file_path: Path,
    content: str,
    encoding: str = 'utf-8',
    create_dirs: bool = True
) -> bool:
    """
    Безопасная запись в файл
    
    Args:
        file_path: Путь к файлу
        content: Содержимое для записи
        encoding: Кодировка (по умолчанию utf-8)
        create_dirs: Создавать ли директории если их нет
    
    Returns:
        True если успешно, False в случае ошибки
    """
    file_path = Path(file_path)
    
    try:
        # Создание директорий если нужно
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Запись файла
        with open(file_path, 'w', encoding=encoding, errors='replace') as f:
            f.write(content)
        
        logger.debug(f"Файл {file_path} успешно записан ({len(content)} символов)")
        return True
    
    except (OSError, IOError, PermissionError) as e:
        logger.error(f"Ошибка записи файла {file_path}: {e}")
        return False
    except Exception as e:
        logger.error(f"Неожиданная ошибка при записи файла {file_path}: {e}", exc_info=True)
        return False


def get_file_size(file_path: Path) -> Optional[int]:
    """
    Получить размер файла в байтах
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        Размер файла или None в случае ошибки
    """
    try:
        return Path(file_path).stat().st_size
    except (OSError, IOError) as e:
        logger.warning(f"Ошибка получения размера файла {file_path}: {e}")
        return None

