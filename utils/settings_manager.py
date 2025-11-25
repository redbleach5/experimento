"""
Менеджер настроек - экспорт/импорт
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SettingsManager:
    """Менеджер для экспорта и импорта настроек"""
    
    def __init__(self, settings_dir: Path = Path('settings')):
        self.settings_dir = settings_dir
        self.settings_dir.mkdir(exist_ok=True)
    
    def export_settings(
        self,
        config: Dict[str, Any],
        theme: str,
        workspace: str,
        output_file: Optional[Path] = None
    ) -> Path:
        """
        Экспорт настроек в файл
        
        Args:
            config: Конфигурация агента
            theme: Текущая тема
            workspace: Текущая рабочая директория
            output_file: Путь к файлу экспорта (опционально)
        
        Returns:
            Путь к файлу экспорта
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.settings_dir / f"settings_export_{timestamp}.json"
        
        export_data = {
            'version': '1.0',
            'export_date': datetime.now().isoformat(),
            'config': config,
            'theme': theme,
            'workspace': workspace
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Настройки экспортированы в {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Ошибка экспорта настроек: {e}", exc_info=True)
            raise
    
    def import_settings(self, import_file: Path) -> Dict[str, Any]:
        """
        Импорт настроек из файла
        
        Args:
            import_file: Путь к файлу импорта
        
        Returns:
            Словарь с настройками
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Валидация версии
            if import_data.get('version') != '1.0':
                logger.warning(f"Несовместимая версия настроек: {import_data.get('version')}")
            
            logger.info(f"Настройки импортированы из {import_file}")
            return import_data
        except Exception as e:
            logger.error(f"Ошибка импорта настроек: {e}", exc_info=True)
            raise
    
    def export_to_yaml(self, config: Dict[str, Any], output_file: Path):
        """Экспорт конфигурации в YAML"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"Конфигурация экспортирована в YAML: {output_file}")
        except Exception as e:
            logger.error(f"Ошибка экспорта в YAML: {e}", exc_info=True)
            raise

