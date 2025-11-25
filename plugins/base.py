"""
Базовые классы для плагинной системы
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class Plugin(ABC):
    """Базовый класс для плагинов"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
        self.enabled = True
    
    @abstractmethod
    def on_init(self, app: Any) -> None:
        """Вызывается при инициализации плагина"""
        pass
    
    def on_file_open(self, file_path: str) -> Optional[Dict]:
        """Вызывается при открытии файла"""
        return None
    
    def on_file_save(self, file_path: str, content: str) -> Optional[Dict]:
        """Вызывается при сохранении файла"""
        return None
    
    def register_commands(self) -> List[Dict[str, Any]]:
        """
        Регистрация команд плагина
        
        Returns:
            Список команд в формате:
            [
                {
                    'name': 'command_name',
                    'handler': callable,
                    'shortcut': 'Ctrl+Key',
                    'description': 'Описание команды'
                }
            ]
        """
        return []
    
    def register_menu_items(self) -> List[Dict[str, Any]]:
        """
        Регистрация пунктов меню
        
        Returns:
            Список пунктов меню
        """
        return []
    
    def get_info(self) -> Dict[str, str]:
        """Получить информацию о плагине"""
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled
        }


class PluginManager:
    """Менеджер плагинов"""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.app: Optional[Any] = None
    
    def register_plugin(self, plugin: Plugin):
        """Регистрация плагина"""
        if plugin.name in self.plugins:
            logger.warning(f"Плагин {plugin.name} уже зарегистрирован, заменяем")
        
        self.plugins[plugin.name] = plugin
        logger.info(f"Плагин {plugin.name} зарегистрирован")
    
    def initialize_plugins(self, app: Any):
        """Инициализация всех плагинов"""
        self.app = app
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    plugin.on_init(app)
                    logger.info(f"Плагин {plugin.name} инициализирован")
                except Exception as e:
                    logger.error(f"Ошибка инициализации плагина {plugin.name}: {e}", exc_info=True)
    
    def get_all_commands(self) -> List[Dict[str, Any]]:
        """Получить все команды от всех плагинов"""
        commands = []
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    plugin_commands = plugin.register_commands()
                    commands.extend(plugin_commands)
                except Exception as e:
                    logger.error(f"Ошибка получения команд от плагина {plugin.name}: {e}")
        return commands
    
    def get_all_menu_items(self) -> List[Dict[str, Any]]:
        """Получить все пункты меню от всех плагинов"""
        items = []
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    plugin_items = plugin.register_menu_items()
                    items.extend(plugin_items)
                except Exception as e:
                    logger.error(f"Ошибка получения пунктов меню от плагина {plugin.name}: {e}")
        return items
    
    def handle_file_open(self, file_path: str) -> Optional[Dict]:
        """Обработка открытия файла через плагины"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    result = plugin.on_file_open(file_path)
                    if result:
                        return result
                except Exception as e:
                    logger.error(f"Ошибка обработки открытия файла плагином {plugin.name}: {e}")
        return None
    
    def handle_file_save(self, file_path: str, content: str) -> Optional[Dict]:
        """Обработка сохранения файла через плагины"""
        for plugin in self.plugins.values():
            if plugin.enabled:
                try:
                    result = plugin.on_file_save(file_path, content)
                    if result:
                        return result
                except Exception as e:
                    logger.error(f"Ошибка обработки сохранения файла плагином {plugin.name}: {e}")
        return None
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """Список всех плагинов"""
        return [plugin.get_info() for plugin in self.plugins.values()]

