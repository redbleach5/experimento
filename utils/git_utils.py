"""
Утилиты для работы с Git
"""

import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def get_git_status(file_path: str) -> Optional[str]:
    """
    Получить статус файла в Git
    
    Returns:
        Статус файла: 'modified', 'added', 'deleted', 'untracked', 'clean' или None
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        
        # Получаем статус файла
        result = subprocess.run(
            ['git', 'status', '--porcelain', str(path)],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=path.parent
        )
        
        if result.returncode != 0:
            return None
        
        status_line = result.stdout.strip()
        if not status_line:
            return 'clean'
        
        # Парсим статус
        status_code = status_line[0:2]
        
        if status_code[0] == 'M' or status_code[1] == 'M':
            return 'modified'
        elif status_code[0] == 'A' or status_code[1] == 'A':
            return 'added'
        elif status_code[0] == 'D' or status_code[1] == 'D':
            return 'deleted'
        elif status_code[0] == '?' or status_code[1] == '?':
            return 'untracked'
        else:
            return 'unknown'
            
    except FileNotFoundError:
        logger.debug("Git не найден")
        return None
    except subprocess.TimeoutExpired:
        logger.warning("Таймаут получения статуса Git")
        return None
    except Exception as e:
        logger.debug(f"Ошибка получения статуса Git для {file_path}: {e}")
        return None


def is_git_repo(directory: str) -> bool:
    """Проверить, является ли директория Git репозиторием"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            cwd=directory,
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def get_git_branch(directory: str) -> Optional[str]:
    """Получить текущую ветку Git"""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None

