"""
Общие утилиты для работы с проектом
Используются во всех интерфейсах
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, List, Dict


def open_in_explorer(path: str) -> bool:
    """
    Открыть путь в проводнике/файловом менеджере
    
    Args:
        path: Путь к файлу или директории
    
    Returns:
        True если успешно, False иначе
    """
    path_obj = Path(path)
    if not path_obj.exists():
        return False
    
    try:
        system = platform.system()
        
        if system == "Windows":
            if path_obj.is_file():
                # Для файла - открываем папку и выделяем файл
                subprocess.Popen(f'explorer /select,"{path_obj}"')
            else:
                # Для директории - просто открываем
                subprocess.Popen(f'explorer "{path_obj}"')
        
        elif system == "Darwin":  # macOS
            if path_obj.is_file():
                subprocess.Popen(["open", "-R", str(path_obj)])
            else:
                subprocess.Popen(["open", str(path_obj)])
        
        else:  # Linux
            if path_obj.is_file():
                subprocess.Popen(["xdg-open", str(path_obj.parent)])
            else:
                subprocess.Popen(["xdg-open", str(path_obj)])
        
        return True
    except Exception:
        return False


def copy_to_clipboard(text: str) -> bool:
    """
    Копировать текст в буфер обмена
    
    Args:
        text: Текст для копирования
    
    Returns:
        True если успешно, False иначе
    """
    try:
        system = platform.system()
        
        if system == "Windows":
            import subprocess
            subprocess.run(['clip'], input=text.encode('utf-8'), check=True)
        elif system == "Darwin":  # macOS
            subprocess.run(['pbcopy'], input=text.encode('utf-8'), check=True)
        else:  # Linux
            subprocess.run(['xclip', '-selection', 'clipboard'], input=text.encode('utf-8'), check=True)
        
        return True
    except Exception:
        return False


def get_file_size_str(file_path: str) -> str:
    """
    Получить размер файла в читаемом формате
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        Строка с размером (например, "1.5 MB")
    """
    try:
        size = Path(file_path).stat().st_size
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} PB"
    except Exception:
        return "Unknown"


def is_text_file(file_path: str) -> bool:
    """
    Проверить, является ли файл текстовым
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        True если файл текстовый
    """
    text_extensions = {
        '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.json',
        '.yaml', '.yml', '.md', '.txt', '.sh', '.bat', '.ps1',
        '.go', '.rs', '.java', '.cpp', '.c', '.h', '.hpp',
        '.php', '.rb', '.swift', '.kt', '.dart', '.lua',
        '.xml', '.svg', '.csv', '.ini', '.conf', '.cfg',
        '.log', '.sql', '.r', '.m', '.pl', '.pm'
    }
    
    return Path(file_path).suffix.lower() in text_extensions


def get_file_icon(file_path: str) -> str:
    """
    Получить иконку для файла
    
    Args:
        file_path: Путь к файлу
    
    Returns:
        Эмодзи иконка
    """
    ext = Path(file_path).suffix.lower()
    name = Path(file_path).name.lower()
    
    # Специальные файлы
    if name in ['readme', 'readme.md', 'readme.txt']:
        return '📖'
    if name in ['license', 'license.txt', 'license.md']:
        return '📜'
    if name.startswith('.git'):
        return '🔧'
    
    # По расширению
    icon_map = {
        '.py': '🐍', '.js': '📜', '.ts': '📘', '.jsx': '⚛️', '.tsx': '⚛️',
        '.html': '🌐', '.htm': '🌐', '.css': '🎨', '.scss': '🎨', '.sass': '🎨',
        '.json': '📋', '.yaml': '⚙️', '.yml': '⚙️', '.xml': '📄',
        '.md': '📝', '.txt': '📄', '.log': '📋',
        '.sh': '💻', '.bat': '💻', '.ps1': '💻', '.cmd': '💻',
        '.go': '🐹', '.rs': '🦀', '.java': '☕', '.kt': '🔷',
        '.cpp': '⚙️', '.c': '⚙️', '.h': '⚙️', '.hpp': '⚙️',
        '.php': '🐘', '.rb': '💎', '.swift': '🐦', '.dart': '🎯',
        '.sql': '🗄️', '.db': '🗄️', '.sqlite': '🗄️',
        '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️', '.svg': '🖼️',
        '.pdf': '📕', '.zip': '📦', '.tar': '📦', '.gz': '📦',
        '.mp3': '🎵', '.mp4': '🎬', '.avi': '🎬',
        '.exe': '⚙️', '.dll': '⚙️', '.so': '⚙️', '.dylib': '⚙️',
    }
    
    return icon_map.get(ext, '📄')


def format_file_tree(path: str, max_depth: int = 3, prefix: str = '', is_last: bool = True) -> List[str]:
    """
    Форматировать дерево файлов в текстовый формат
    
    Args:
        path: Путь к директории
        max_depth: Максимальная глубина
        prefix: Префикс для отступов
        is_last: Является ли последним элементом
    
    Returns:
        Список строк дерева
    """
    lines = []
    path_obj = Path(path)
    
    if not path_obj.exists() or not path_obj.is_dir() or max_depth < 0:
        return lines
    
    try:
        items = sorted(
            [item for item in path_obj.iterdir() 
             if not item.name.startswith('.') and item.name not in ['__pycache__', 'node_modules', '.git']],
            key=lambda x: (not x.is_dir(), x.name.lower())
        )
        
        for i, item in enumerate(items):
            is_last_item = i == len(items) - 1
            current_prefix = '└── ' if is_last_item else '├── '
            icon = '📁' if item.is_dir() else get_file_icon(str(item))
            
            lines.append(f"{prefix}{current_prefix}{icon} {item.name}")
            
            if item.is_dir() and max_depth > 0:
                next_prefix = prefix + ('    ' if is_last_item else '│   ')
                lines.extend(format_file_tree(str(item), max_depth - 1, next_prefix, is_last_item))
    except PermissionError:
        pass
    except Exception:
        pass
    
    return lines

