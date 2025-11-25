"""
Утилиты для проекта
"""

from .logger import setup_logger, get_logger
from .file_utils import read_file_safe, write_file_safe

__all__ = ['setup_logger', 'get_logger', 'read_file_safe', 'write_file_safe']

