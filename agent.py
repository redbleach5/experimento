"""
AI Agent для помощи в написании кода
Поддерживает локальные модели через Ollama и прямую работу с transformers
"""

import os
import json
import yaml
import re
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Generator
import requests
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализация console
console = Console()

# Инициализация логирования
from utils.logger import setup_logger
logger = setup_logger('code_agent')

# Импорт MCP инструментов
try:
    from mcp_tools import MCPToolManager, format_tools_for_prompt
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    console.print("[yellow]MCP tools not available[/yellow]")

# Импорт контекста проекта
try:
    from project_context import ProjectContext, load_project_context
    PROJECT_CONTEXT_AVAILABLE = True
except ImportError:
    PROJECT_CONTEXT_AVAILABLE = False
    console.print("[yellow]Project context not available[/yellow]")

# Импорт адаптера модели
try:
    from model_adapter import ModelAdapter, create_model_adapter
    MODEL_ADAPTER_AVAILABLE = True
except ImportError:
    MODEL_ADAPTER_AVAILABLE = False
    console.print("[yellow]Model adapter not available[/yellow]")


class CodeAgent:
    """AI агент для помощи в написании кода"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Инициализация агента"""
        self.config = self._load_config(config_path)
        
        # Безопасное получение конфигурации с значениями по умолчанию
        model_config = self.config.get('model', {})
        self.provider = model_config.get('provider', 'ollama')
        self.model_name = model_config.get('model_name', 'deepseek-coder:6.7b')
        
        agent_config = self.config.get('agent', {})
        history_path = agent_config.get('history_path', './history')
        
        self.history: List[Dict] = []
        self.history_path = Path(history_path)
        self.history_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализация MCP инструментов
        self.use_mcp = self.config.get('mcp', {}).get('enabled', True) and MCP_AVAILABLE
        if self.use_mcp:
            self.mcp_tools = MCPToolManager()
            console.print(f"[green]MCP инструменты загружены: {len(self.mcp_tools.list_tools())} доступно[/green]")
        else:
            self.mcp_tools = None
        
        # Инициализация адаптера модели
        self.use_adapter = MODEL_ADAPTER_AVAILABLE
        if self.use_adapter:
            base_url = None
            if self.provider == "ollama":
                base_url = self.config.get('ollama', {}).get('base_url', 'http://localhost:11434')
            elif self.provider == "lmstudio":
                base_url = self.config.get('lmstudio', {}).get('base_url', 'http://localhost:1234')
            elif self.provider in ["openai", "openai_compatible", "anthropic", "custom"]:
                # Для OpenAI-совместимых API получаем base_url из конфигурации провайдера
                provider_config = self.config.get(self.provider, {})
                base_url = provider_config.get('base_url')
                if not base_url:
                    # Пробуем определить по провайдеру
                    if self.provider == "openai":
                        base_url = "https://api.openai.com/v1"
                    elif self.provider == "anthropic":
                        base_url = "https://api.anthropic.com/v1"
            
            try:
                self.model_adapter = create_model_adapter(self.provider, self.model_name, base_url)
                self.model_adapter.print_info()
                
                # Адаптируем конфигурацию под модель
                self.config = self.model_adapter.get_optimal_config(self.config)
            except Exception as e:
                console.print(f"[yellow]Ошибка создания адаптера модели: {e}[/yellow]")
                self.model_adapter = None
                self.use_adapter = False
        else:
            self.model_adapter = None
        
        # Инициализация контекста проекта
        self.use_project_context = self.config.get('agent', {}).get('load_project_context', True) and PROJECT_CONTEXT_AVAILABLE
        if self.use_project_context:
            # Проверяем, стоит ли включать контекст проекта для этой модели
            if self.use_adapter and self.model_adapter:
                if not self.model_adapter.should_include_project_context():
                    console.print(f"[yellow]Контекст проекта отключен для модели с маленьким контекстом ({self.model_adapter.capabilities.max_context} токенов)[/yellow]")
                    self.use_project_context = False
            
            if self.use_project_context:
                project_root = self.config.get('agent', {}).get('project_root', '.')
                try:
                    self.project_context = load_project_context(project_root)
                    console.print(f"[green]Контекст проекта загружен: {self.project_context.project_root}[/green]")
                except Exception as e:
                    console.print(f"[yellow]Ошибка загрузки контекста проекта: {e}[/yellow]")
                    self.project_context = None
                    self.use_project_context = False
        else:
            self.project_context = None
        
        # Инициализация провайдера
        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "lmstudio":
            self._init_lmstudio()
        elif self.provider == "local_transformers":
            self._init_transformers()
        elif self.provider in ["openai", "openai_compatible", "anthropic", "custom"]:
            self._init_openai_compatible()
        else:
            # Пробуем как OpenAI-совместимый API
            console.print(f"[yellow]Провайдер '{self.provider}' не распознан, пробуем как OpenAI-совместимый API[/yellow]")
            self._init_openai_compatible()
    
    def _load_config(self, config_path: str) -> Dict:
        """Загрузка и валидация конфигурации"""
        if not os.path.exists(config_path):
            logger.warning(f"Конфигурация не найдена, используем значения по умолчанию: {config_path}")
            console.print(f"[yellow]Конфигурация не найдена, используем значения по умолчанию[/yellow]")
            return self._default_config()
        
        try:
            from utils.file_utils import read_file_safe
            from utils.config_validator import validate_config
            
            content = read_file_safe(Path(config_path))
            if content is None:
                logger.warning("Не удалось прочитать конфигурацию, используем значения по умолчанию")
                return self._default_config()
            
            config = yaml.safe_load(content)
            if config is None:
                logger.warning("Конфигурация пуста, используем значения по умолчанию")
                console.print(f"[yellow]Конфигурация пуста, используем значения по умолчанию[/yellow]")
                return self._default_config()
            
            # Валидация конфигурации
            is_valid, validated_config, error_msg = validate_config(config)
            if is_valid and validated_config:
                logger.info("Конфигурация успешно загружена и валидирована")
                return validated_config.to_dict()
            else:
                logger.warning(f"Ошибка валидации конфигурации: {error_msg}, используем как есть")
                if error_msg:
                    console.print(f"[yellow]Предупреждение валидации: {error_msg}[/yellow]")
                return config
                
        except yaml.YAMLError as e:
            logger.error(f"Ошибка парсинга YAML конфигурации: {e}", exc_info=True)
            console.print(f"[red]Ошибка парсинга конфигурации: {e}[/red]")
            console.print(f"[yellow]Используем значения по умолчанию[/yellow]")
            return self._default_config()
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}", exc_info=True)
            console.print(f"[red]Ошибка чтения конфигурации: {e}[/red]")
            console.print(f"[yellow]Используем значения по умолчанию[/yellow]")
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Конфигурация по умолчанию"""
        return {
            'model': {
                'provider': 'ollama',
                'model_name': 'deepseek-coder:6.7b',
                'device': 'cuda',
                'generation': {
                    'max_tokens': 4096,
                    'temperature': 0.2,
                    'top_p': 0.95,
                    'top_k': 40,
                    'repetition_penalty': 1.1
                }
            },
            'agent': {
                'system_prompt': 'Ты опытный AI-ассистент для программирования.',
                'history_path': './history',
                'max_context_length': 8192,
                'save_history': True,
                'load_project_context': True,
                'project_root': '.'
            },
            'ollama': {
                'base_url': 'http://localhost:11434',
                'timeout': 300
            },
            'lmstudio': {
                'base_url': 'http://localhost:1234',
                'timeout': 300
            },
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'api_key': '',  # Укажите OPENAI_API_KEY или в переменных окружения
                'timeout': 300
            },
            'anthropic': {
                'base_url': 'https://api.anthropic.com/v1',
                'api_key': '',  # Укажите ANTHROPIC_API_KEY или в переменных окружения
                'timeout': 300
            },
            'mcp': {
                'enabled': True,
                'max_iterations': 5
            }
        }
    
    def _init_ollama(self):
        """Инициализация Ollama"""
        self.ollama_url = self.config.get('ollama', {}).get('base_url', 'http://localhost:11434')
        self.timeout = self.config.get('ollama', {}).get('timeout', 300)
        
        # Проверяем доступность Ollama
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                console.print(f"[green]Ollama подключен. Доступные модели: {', '.join(model_names)}[/green]")
                
                # Проверяем наличие нужной модели
                if self.model_name not in model_names:
                    console.print(f"[yellow]Модель {self.model_name} не найдена. Используйте: ollama pull {self.model_name}[/yellow]")
            else:
                console.print(f"[red]Ollama недоступен. Убедитесь, что Ollama запущен.[/red]")
        except Exception as e:
            console.print(f"[red]Ошибка подключения к Ollama: {e}[/red]")
            console.print(f"[yellow]Установите Ollama: https://ollama.ai[/yellow]")
    
    def _init_lmstudio(self):
        """Инициализация LM Studio"""
        self.lmstudio_url = self.config.get('lmstudio', {}).get('base_url', 'http://localhost:1234')
        self.timeout = self.config.get('lmstudio', {}).get('timeout', 300)
        self.available_models = []  # Список доступных моделей
        self.lmstudio_model_map = {}  # Маппинг имен моделей
        
        # Пробуем несколько раз с разными таймаутами
        for attempt in range(3):
            try:
                timeout = 5 + (attempt * 5)  # 5, 10, 15 секунд
                response = requests.get(f"{self.lmstudio_url}/v1/models", timeout=timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    models = data.get('data', [])
                    
                    # Извлекаем все возможные идентификаторы моделей
                    model_ids = []
                    for m in models:
                        # Пробуем разные поля
                        model_id = m.get('id') or m.get('model') or m.get('name') or ''
                        if model_id:
                            model_ids.append(model_id)
                            # Сохраняем все варианты имени для поиска
                            self.lmstudio_model_map[model_id.lower()] = model_id
                            # Также сохраняем без расширения и с разными вариантами
                            model_base = model_id.split('/')[-1].split(':')[0].lower()
                            if model_base not in self.lmstudio_model_map:
                                self.lmstudio_model_map[model_base] = model_id
                    
                    self.available_models = model_ids
                    
                    if model_ids:
                        console.print(f"[green]LM Studio подключен. Найдено моделей: {len(model_ids)}[/green]")
                        for i, mid in enumerate(model_ids, 1):
                            console.print(f"  {i}. {mid}")
                        
                        # Если модель не указана или не найдена, используем первую доступную
                        if not self.model_name or self.model_name not in model_ids:
                            if model_ids:
                                # Пробуем найти похожую модель (частичное совпадение)
                                found_model = None
                                if self.model_name:
                                    model_name_lower = self.model_name.lower()
                                    # Сначала пробуем точное совпадение в маппинге
                                    if model_name_lower in self.lmstudio_model_map:
                                        found_model = self.lmstudio_model_map[model_name_lower]
                                    else:
                                        # Ищем модель с похожим именем
                                        for mid in model_ids:
                                            mid_lower = mid.lower()
                                            # Проверяем различные варианты совпадения
                                            if (model_name_lower in mid_lower or 
                                                mid_lower in model_name_lower or
                                                model_name_lower.split(':')[0] in mid_lower or
                                                mid_lower.split(':')[0] in model_name_lower):
                                                found_model = mid
                                                break
                                
                                # Если не нашли похожую, используем первую доступную
                                self.model_name = found_model or model_ids[0]
                                if found_model:
                                    console.print(f"[yellow]Используется похожая модель: {self.model_name}[/yellow]")
                                else:
                                    console.print(f"[yellow]Используется первая доступная модель: {self.model_name}[/yellow]")
                                console.print(f"[cyan]Доступно моделей: {len(model_ids)}. Можно использовать любую из них.[/cyan]")
                        else:
                            console.print(f"[green]Используется указанная модель: {self.model_name}[/green]")
                            console.print(f"[cyan]Доступно моделей: {len(model_ids)}. Можно использовать любую из них.[/cyan]")
                        return
                    else:
                        console.print(f"[yellow]Модели не найдены в ответе API[/yellow]")
                        console.print(f"[yellow]Полный ответ: {data}[/yellow]")
                
                elif response.status_code == 502:
                    if attempt < 2:
                        import time
                        wait_time = (attempt + 1) * 3
                        console.print(f"[yellow]Сервер возвращает 502, попытка {attempt + 1}/3, ждем {wait_time}с...[/yellow]")
                        time.sleep(wait_time)
                        continue
                    else:
                        console.print(f"[yellow]LM Studio сервер отвечает, но возвращает 502[/yellow]")
                        console.print(f"[yellow]Модель может быть еще не готова. Используем указанную модель: {self.model_name}[/yellow]")
                        return
                else:
                    console.print(f"[yellow]LM Studio вернул код {response.status_code}[/yellow]")
                    if attempt < 2:
                        continue
                    
            except requests.exceptions.Timeout:
                if attempt < 2:
                    console.print(f"[yellow]Таймаут подключения, попытка {attempt + 1}/3...[/yellow]")
                    continue
                else:
                    console.print(f"[yellow]Не удалось подключиться к LM Studio (таймаут)[/yellow]")
            except requests.exceptions.ConnectionError:
                if attempt < 2:
                    import time
                    time.sleep(2)
                    continue
                else:
                    console.print(f"[red]Не удалось подключиться к LM Studio[/red]")
                    console.print(f"[yellow]Убедитесь, что LM Studio запущен и Local Server включен[/yellow]")
                    console.print(f"[yellow]Запустите test_lmstudio.py для диагностики[/yellow]")
            except Exception as e:
                console.print(f"[red]Ошибка подключения к LM Studio: {e}[/red]")
                if attempt < 2:
                    import time
                    time.sleep(2)
                    continue
        
        # Если не удалось получить модели, но модель указана в конфиге - используем ее
        if self.model_name:
            console.print(f"[yellow]Используем модель из конфигурации: {self.model_name}[/yellow]")
            console.print(f"[yellow]Если модель не работает, проверьте её наличие в LM Studio[/yellow]")
            console.print(f"[cyan]Наше ПО поддерживает любую модель из LM Studio - просто загрузите её в LM Studio[/cyan]")
            console.print(f"[cyan]Запустите test_lmstudio.py для диагностики подключения[/cyan]")
    
    def _init_transformers(self):
        """Инициализация transformers (для прямого использования моделей)"""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            model_path = self.config['model'].get('model_path') or self.model_name
            device = self.config['model'].get('device', 'cuda')
            
            console.print(f"[cyan]Загрузка модели {model_path}...[/cyan]")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
                device_map='auto' if device == 'cuda' else None,
            )
            
            if device == 'cpu':
                self.model = self.model.to(device)
            
            console.print(f"[green]Модель загружена[/green]")
        except Exception as e:
            console.print(f"[red]Ошибка загрузки модели: {e}[/red]")
            raise
    
    def _init_openai_compatible(self):
        """Инициализация OpenAI-совместимого API (OpenAI, Anthropic, кастомные провайдеры)"""
        # Получаем конфигурацию провайдера
        provider_config = self.config.get(self.provider, {})
        
        # Определяем базовый URL
        if self.provider == "openai":
            self.openai_url = provider_config.get('base_url', 'https://api.openai.com/v1')
            self.api_key = provider_config.get('api_key') or os.getenv('OPENAI_API_KEY')
        elif self.provider == "anthropic":
            self.openai_url = provider_config.get('base_url', 'https://api.anthropic.com/v1')
            self.api_key = provider_config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        else:
            # Кастомный провайдер
            self.openai_url = provider_config.get('base_url')
            if not self.openai_url:
                raise ValueError(f"Для провайдера '{self.provider}' необходимо указать base_url в конфигурации")
            self.api_key = provider_config.get('api_key') or os.getenv(f'{self.provider.upper()}_API_KEY')
        
        self.timeout = provider_config.get('timeout', 300)
        
        # Проверяем подключение
        try:
            # Пробуем получить список моделей
            headers = {}
            if self.api_key:
                if self.provider == "anthropic":
                    headers['x-api-key'] = self.api_key
                else:
                    headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = requests.get(
                f"{self.openai_url}/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                model_names = [m.get('id', m.get('name', '')) for m in models if m.get('id') or m.get('name')]
                console.print(f"[green]{self.provider.upper()} подключен. Доступно моделей: {len(model_names)}[/green]")
                
                # Проверяем наличие указанной модели
                if self.model_name and self.model_name not in model_names:
                    # Пробуем найти похожую
                    found = None
                    for m in model_names:
                        if self.model_name.lower() in m.lower() or m.lower() in self.model_name.lower():
                            found = m
                            break
                    
                    if found:
                        console.print(f"[yellow]Модель '{self.model_name}' не найдена, используем похожую: '{found}'[/yellow]")
                        self.model_name = found
                    else:
                        console.print(f"[yellow]Модель '{self.model_name}' не найдена в списке. Будет использована как указано.[/yellow]")
            else:
                console.print(f"[yellow]Не удалось получить список моделей (код {response.status_code}), но продолжаем работу[/yellow]")
        except Exception as e:
            console.print(f"[yellow]Не удалось проверить подключение к {self.provider}: {e}[/yellow]")
            console.print(f"[cyan]Продолжаем работу, модель будет использована как указано в конфигурации[/cyan]")
    
    def _estimate_tokens(self, text: str) -> int:
        """Оценивает количество токенов в тексте"""
        if self.use_adapter and self.model_adapter:
            return self.model_adapter.estimate_tokens(text)
        # Простая оценка: примерно 4 символа на токен
        return len(text) // 4
    
    def _build_messages(self, user_prompt: str) -> List[Dict]:
        """Построение списка сообщений для модели"""
        messages = []
        
        # Оцениваем размер истории
        history_tokens = sum(self._estimate_tokens(msg.get('content', '')) for msg in self.history[-10:])
        
        # Системный промпт
        system_prompt = self.config.get('agent', {}).get('system_prompt', '')
        
        # Проверяем, стоит ли включать контекст проекта
        should_include_project = False
        if self.use_project_context and self.project_context:
            if self.use_adapter and self.model_adapter:
                should_include_project = self.model_adapter.should_include_project_context(history_tokens)
            else:
                # Fallback: только если нет истории
                should_include_project = len(self.history) == 0
        
        # Добавляем контекст проекта в системный промпт (только при первом запросе и если разрешено)
        if should_include_project and len(self.history) == 0:
            try:
                # Используем адаптер для определения размера контекста
                if self.use_adapter and self.model_adapter:
                    max_project_context = self.model_adapter.get_max_context_for_project()
                else:
                    # Fallback на старый метод
                    max_context_length = self.config.get('agent', {}).get('max_context_length', 8192)
                    max_project_context = int(max_context_length * 0.3 * 4)
                
                project_summary = self.project_context.get_project_summary(max_chars=max_project_context)
                
                # Оптимизируем контекст через адаптер
                if self.use_adapter and self.model_adapter:
                    project_summary = self.model_adapter.optimize_context(project_summary, max_project_context)
                
                if project_summary:
                    system_prompt += "\n\n" + "=" * 60
                    system_prompt += "\nКОНТЕКСТ ПРОЕКТА:\n"
                    system_prompt += "=" * 60 + "\n"
                    system_prompt += project_summary
                    system_prompt += "\n" + "=" * 60
                    console.print(f"[cyan]Контекст проекта добавлен в системный промпт ({len(project_summary)} символов)[/cyan]")
            except Exception as e:
                console.print(f"[yellow]Ошибка добавления контекста проекта: {e}[/yellow]")
        
        # Добавляем информацию о MCP инструментах в системный промпт
        if self.use_mcp and self.mcp_tools:
            tools_info = format_tools_for_prompt(self.mcp_tools)
            if tools_info:
                system_prompt += "\n\n" + tools_info
        
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Форматируем сообщения под модель через адаптер
        if self.use_adapter and self.model_adapter:
            messages = self.model_adapter.format_messages_for_model(messages)
        
        # Оцениваем текущий размер контекста
        current_context_tokens = (
            self._estimate_tokens(system_prompt) +
            history_tokens +
            self._estimate_tokens(user_prompt)
        )
        
        # Определяем доступное место для релевантных файлов
        if self.use_adapter and self.model_adapter:
            max_context = self.model_adapter.capabilities.max_context
            available_tokens = max_context - current_context_tokens - 500  # Оставляем запас для ответа
            
            # Для маленьких моделей - не добавляем релевантные файлы если места мало
            if available_tokens < 200 or max_context <= 4096:
                console.print(f"[yellow]Мало места для релевантных файлов ({available_tokens} токенов доступно), пропускаем[/yellow]")
            else:
                # Добавляем релевантные файлы для текущего запроса (ограниченные)
                if self.use_project_context and self.project_context:
                    try:
                        max_relevant_files_size = self.model_adapter.get_max_relevant_files_size()
                        # Ограничиваем доступным местом
                        max_relevant_chars = min(max_relevant_files_size, available_tokens * 3)
                        max_file_size = min(800, max_relevant_chars // 2)  # Еще более консервативно
                        
                        relevant_files = self.project_context.get_relevant_files_for_query(
                            user_prompt, 
                            max_files=1,  # Только 1 файл для маленьких моделей
                            max_file_size=max_file_size
                        )
                        if relevant_files:
                            context_files = "\n\nРелевантный файл:\n"
                            context_files += "-" * 60 + "\n"
                            for file_path, content in list(relevant_files.items())[:1]:  # Только первый
                                context_files += f"\n{file_path}:\n```\n{content}\n```\n"
                            user_prompt = context_files + "\n" + user_prompt
                            console.print(f"[cyan]Добавлен 1 релевантный файл ({len(content)} символов)[/cyan]")
                    except Exception as e:
                        console.print(f"[yellow]Ошибка загрузки релевантных файлов: {e}[/yellow]")
        else:
            # Fallback: не добавляем релевантные файлы для маленьких моделей
            max_context_length = self.config.get('agent', {}).get('max_context_length', 8192)
            if max_context_length > 6000 and self.use_project_context and self.project_context:
                try:
                    max_relevant_files_size = int(max_context_length * 0.10 * 3)  # 10% консервативно
                    max_file_size = min(800, max_relevant_files_size // 2)
                    
                    relevant_files = self.project_context.get_relevant_files_for_query(
                        user_prompt, 
                        max_files=1,
                        max_file_size=max_file_size
                    )
                    if relevant_files:
                        context_files = "\n\nРелевантный файл:\n"
                        context_files += "-" * 60 + "\n"
                        for file_path, content in list(relevant_files.items())[:1]:
                            context_files += f"\n{file_path}:\n```\n{content}\n```\n"
                        user_prompt = context_files + "\n" + user_prompt
                except Exception as e:
                    console.print(f"[yellow]Ошибка загрузки релевантных файлов: {e}[/yellow]")
        
        # История диалога (ограниченная)
        history_messages = self.history[-10:]  # Последние 10 сообщений
        
        # Для маленьких моделей ограничиваем историю
        if self.use_adapter and self.model_adapter:
            if self.model_adapter.capabilities.max_context <= 4096:
                # Для 4K моделей - только последние 3 сообщения
                history_messages = self.history[-3:]
            elif self.model_adapter.capabilities.max_context < 6000:
                # Для 4K-6K моделей - последние 5 сообщений
                history_messages = self.history[-5:]
        
        for msg in history_messages:
            messages.append(msg)
        
        # Текущий запрос
        messages.append({
            'role': 'user',
            'content': user_prompt
        })
        
        # Финальная проверка размера контекста
        if self.use_adapter and self.model_adapter:
            total_tokens = sum(self._estimate_tokens(msg.get('content', '')) for msg in messages)
            max_context = self.model_adapter.capabilities.max_context
            
            if total_tokens > max_context * 0.9:  # Если превышаем 90% контекста
                console.print(f"[yellow]⚠ Предупреждение: контекст большой ({total_tokens}/{max_context} токенов)[/yellow]")
                
                # Агрессивно обрезаем системный промпт если нужно
                if total_tokens > max_context:
                    system_msg = messages[0] if messages and messages[0].get('role') == 'system' else None
                    if system_msg:
                        # Оставляем только базовый системный промпт
                        base_prompt = self.config.get('agent', {}).get('system_prompt', '')
                        if len(system_msg['content']) > len(base_prompt) * 2:
                            system_msg['content'] = base_prompt + "\n\n[Контекст проекта был удален для экономии токенов]"
                            console.print("[yellow]Контекст проекта удален из системного промпта для экономии токенов[/yellow]")
        
        return messages
    
    def _call_ollama(self, messages: List[Dict], stream: bool = False) -> Generator[str, None, None]:
        """Вызов Ollama API"""
        url = f"{self.ollama_url}/api/chat"
        
        generation_config = self.config.get('model', {}).get('generation', {})
        
        # Используем адаптер для оптимизации параметров
        if self.use_adapter and self.model_adapter:
            # Адаптер уже оптимизировал конфигурацию при инициализации
            max_tokens = generation_config.get('max_tokens', self.model_adapter.capabilities.max_tokens)
            temperature = generation_config.get('temperature', self.model_adapter.capabilities.optimal_temperature)
            top_p = generation_config.get('top_p', self.model_adapter.capabilities.optimal_top_p)
            top_k = generation_config.get('top_k', self.model_adapter.capabilities.optimal_top_k)
        else:
            max_tokens = generation_config.get('max_tokens', 4096)
            temperature = generation_config.get('temperature', 0.2)
            top_p = generation_config.get('top_p', 0.95)
            top_k = generation_config.get('top_k', 40)
        
        payload = {
            'model': self.model_name,
            'messages': messages,
            'stream': stream,
            'options': {
                'temperature': temperature,
                'top_p': top_p,
                'top_k': top_k,
                'num_predict': max_tokens,
            }
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                stream=stream,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'message' in data and 'content' in data['message']:
                                yield data['message']['content']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                result = response.json()
                if 'message' in result and 'content' in result['message']:
                    yield result['message']['content']
                else:
                    yield "Ошибка: неожиданный формат ответа от Ollama"
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Ошибка запроса к Ollama: {e}[/red]")
            yield f"Ошибка: {e}"
    
    def _call_lmstudio(self, messages: List[Dict], stream: bool = False) -> Generator[str, None, None]:
        """Вызов LM Studio API (OpenAI-совместимый)"""
        url = f"{self.lmstudio_url}/v1/chat/completions"
        
        generation_config = self.config.get('model', {}).get('generation', {})
        
        # Используем адаптер для форматирования сообщений
        if self.use_adapter and self.model_adapter:
            formatted_messages = self.model_adapter.format_messages_for_model(messages)
            max_tokens = generation_config.get('max_tokens', self.model_adapter.capabilities.max_tokens)
            temperature = generation_config.get('temperature', self.model_adapter.capabilities.optimal_temperature)
            top_p = generation_config.get('top_p', self.model_adapter.capabilities.optimal_top_p)
        else:
            # Fallback на старый метод
            formatted_messages = []
            for msg in messages:
                if msg['role'] == 'system':
                    formatted_messages.append({
                        'role': 'user',
                        'content': f"System: {msg['content']}"
                    })
                else:
                    formatted_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            max_tokens = min(generation_config.get('max_tokens', 4096), 2000)
            temperature = generation_config.get('temperature', 0.7)
            top_p = generation_config.get('top_p', 0.95)
        
        # Определяем правильное имя модели для LM Studio
        actual_model_name = self.model_name
        if hasattr(self, 'lmstudio_model_map') and self.lmstudio_model_map:
            # Пробуем найти точное имя модели в маппинге
            model_name_lower = self.model_name.lower()
            if model_name_lower in self.lmstudio_model_map:
                actual_model_name = self.lmstudio_model_map[model_name_lower]
            elif hasattr(self, 'available_models') and self.available_models:
                # Если модель не найдена в маппинге, пробуем найти похожую
                for available_model in self.available_models:
                    if (model_name_lower in available_model.lower() or 
                        available_model.lower() in model_name_lower):
                        actual_model_name = available_model
                        break
                else:
                    # Используем первую доступную модель
                    actual_model_name = self.available_models[0]
                    console.print(f"[yellow]Модель '{self.model_name}' не найдена, используем '{actual_model_name}'[/yellow]")
        
        # Упрощенный payload для лучшей совместимости
        payload = {
            'model': actual_model_name,
            'messages': formatted_messages,
            'stream': stream,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        
        # Добавляем дополнительные параметры
        if top_p:
            payload['top_p'] = top_p
        
        try:
            # Увеличиваем таймаут для больших моделей
            timeout = max(self.timeout, 180)  # Минимум 3 минуты
            
            # Пробуем несколько раз с задержками и увеличивающимися таймаутами
            max_retries = 5
            response = None
            
            for attempt in range(max_retries):
                try:
                    # Увеличиваем таймаут с каждой попыткой
                    current_timeout = timeout + (attempt * 30)  # 180, 210, 240, 270, 300
                    
                    response = requests.post(
                        url,
                        json=payload,
                        stream=stream,
                        timeout=current_timeout,
                        headers={
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        }
                    )
                    
                    # Если получили 200 - отлично
                    if response.status_code == 200:
                        break
                    
                    # Если 502 и не последняя попытка - ждем и пробуем снова
                    if response.status_code == 502 and attempt < max_retries - 1:
                        import time
                        wait_time = (attempt + 1) * 10  # 10, 20, 30, 40 секунд
                        console.print(f"[yellow]Ожидание готовности модели (попытка {attempt + 1}/{max_retries}, ждем {wait_time}с)...[/yellow]")
                        time.sleep(wait_time)
                        continue
                    
                    # Для других ошибок - пробуем еще раз
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(5)
                        continue
                    
                    # Последняя попытка - выходим
                    response.raise_for_status()
                    break
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 502 and attempt < max_retries - 1:
                        import time
                        wait_time = (attempt + 1) * 10
                        console.print(f"[yellow]Повторная попытка через {wait_time}с (попытка {attempt + 1}/{max_retries})...[/yellow]")
                        time.sleep(wait_time)
                        continue
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(5)
                        continue
                    raise
                except requests.exceptions.Timeout:
                    if attempt < max_retries - 1:
                        import time
                        wait_time = (attempt + 1) * 5
                        console.print(f"[yellow]Таймаут, повтор через {wait_time}с...[/yellow]")
                        time.sleep(wait_time)
                        continue
                    raise
            
            if not response:
                raise requests.exceptions.RequestException("Не удалось получить ответ после всех попыток")
            
            response.raise_for_status()
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = line.decode('utf-8')
                            # LM Studio может использовать разные форматы
                            if line_text.startswith('data: '):
                                data_str = line_text[6:]
                                if data_str.strip() == '[DONE]':
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                            elif line_text.strip() and not line_text.startswith(':'):
                                # Пробуем распарсить как JSON напрямую
                                try:
                                    data = json.loads(line_text)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    # Если не JSON, возможно это просто текст
                                    if line_text.strip() and not line_text.startswith(':'):
                                        yield line_text
                        except UnicodeDecodeError:
                            continue
            else:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    yield result['choices'][0]['message']['content']
                else:
                    yield "Ошибка: неожиданный формат ответа"
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 502:
                error_msg = (
                    "Ошибка 502: Сервер LM Studio не может обработать запрос.\n\n"
                    "Возможные причины:\n"
                    "1. Модель еще загружается - подождите 30-60 секунд\n"
                    "2. Сервер перегружен - попробуйте позже\n"
                    "3. Модель слишком большая для системы\n\n"
                    "Решение:\n"
                    "- В LM Studio убедитесь, что статус 'READY'\n"
                    "- Перезапустите Local Server в настройках LM Studio\n"
                    "- Попробуйте использовать меньшую модель"
                )
                console.print(f"[red]{error_msg}[/red]")
                yield error_msg
            else:
                console.print(f"[red]Ошибка HTTP {e.response.status_code}: {e}[/red]")
                yield f"Ошибка HTTP {e.response.status_code}: {e}"
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Ошибка запроса к LM Studio: {e}[/red]")
            yield f"Ошибка подключения: {e}\n\nУбедитесь, что:\n1. LM Studio запущен\n2. Local Server включен\n3. Модель загружена"
    
    def _call_openai_compatible(self, messages: List[Dict], stream: bool = False) -> Generator[str, None, None]:
        """Вызов OpenAI-совместимого API (OpenAI, Anthropic, кастомные провайдеры)"""
        url = f"{self.openai_url}/chat/completions"
        
        generation_config = self.config.get('model', {}).get('generation', {})
        
        # Используем адаптер для форматирования сообщений
        if self.use_adapter and self.model_adapter:
            formatted_messages = self.model_adapter.format_messages_for_model(messages)
            max_tokens = generation_config.get('max_tokens', self.model_adapter.capabilities.max_tokens)
            temperature = generation_config.get('temperature', self.model_adapter.capabilities.optimal_temperature)
            top_p = generation_config.get('top_p', self.model_adapter.capabilities.optimal_top_p)
        else:
            formatted_messages = messages
            max_tokens = generation_config.get('max_tokens', 4096)
            temperature = generation_config.get('temperature', 0.7)
            top_p = generation_config.get('top_p', 0.95)
        
        # Формируем заголовки
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            if self.provider == "anthropic":
                headers['x-api-key'] = self.api_key
                headers['anthropic-version'] = '2023-06-01'
            else:
                headers['Authorization'] = f'Bearer {self.api_key}'
        
        # Формируем payload
        payload = {
            'model': self.model_name,
            'messages': formatted_messages,
            'stream': stream,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        
        if top_p:
            payload['top_p'] = top_p
        
        # Для Anthropic нужен другой формат
        if self.provider == "anthropic":
            # Anthropic использует немного другой формат
            payload['max_tokens'] = min(max_tokens, 4096)  # Anthropic ограничивает max_tokens
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                stream=stream,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            if stream:
                for line in response.iter_lines():
                    if line:
                        try:
                            line_text = line.decode('utf-8')
                            if line_text.startswith('data: '):
                                data_str = line_text[6:]
                                if data_str.strip() == '[DONE]':
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if 'choices' in data and len(data['choices']) > 0:
                                        delta = data['choices'][0].get('delta', {})
                                        content = delta.get('content', '')
                                        if content:
                                            yield content
                                except json.JSONDecodeError:
                                    continue
                        except UnicodeDecodeError:
                            continue
            else:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    yield result['choices'][0]['message']['content']
                else:
                    yield "Ошибка: неожиданный формат ответа"
                
        except requests.exceptions.HTTPError as e:
            console.print(f"[red]Ошибка HTTP {e.response.status_code}: {e}[/red]")
            error_msg = f"Ошибка HTTP {e.response.status_code}"
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    error_msg += f": {error_data['error'].get('message', 'Неизвестная ошибка')}"
            except:
                pass
            yield error_msg
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Ошибка запроса к {self.provider}: {e}[/red]")
            yield f"Ошибка подключения: {e}\n\nУбедитесь, что:\n1. API ключ указан правильно\n2. Базовый URL корректен\n3. Модель доступна"
    
    def _call_transformers(self, messages: List[Dict], stream: bool = False) -> Generator[str, None, None]:
        """Вызов модели через transformers"""
        import torch
        
        # Форматируем сообщения в промпт
        prompt = self._format_messages(messages)
        
        # Токенизация
        inputs = self.tokenizer(prompt, return_tensors="pt")
        if self.config['model'].get('device') == 'cuda':
            inputs = {k: v.cuda() for k, v in inputs.items()}
        
        # Генерация
        generation_config = self.config.get('model', {}).get('generation', {})
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=generation_config.get('max_tokens', 4096),
                temperature=generation_config.get('temperature', 0.2),
                top_p=generation_config.get('top_p', 0.95),
                top_k=generation_config.get('top_k', 40),
                repetition_penalty=generation_config.get('repetition_penalty', 1.1),
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Декодирование
        generated_text = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        if stream:
            # Симулируем стриминг
            words = generated_text.split()
            for word in words:
                yield word + " "
        else:
            yield generated_text
    
    def _format_messages(self, messages: List[Dict]) -> str:
        """Форматирование сообщений в промпт"""
        formatted = []
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                formatted.append(f"System: {content}\n")
            elif role == 'user':
                formatted.append(f"User: {content}\n")
            elif role == 'assistant':
                formatted.append(f"Assistant: {content}\n")
        
        formatted.append("Assistant: ")
        return "\n".join(formatted)
    
    def _parse_tool_calls(self, text: str) -> List[Dict]:
        """Парсинг вызовов инструментов из текста"""
        tool_calls = []
        # Ищем паттерн TOOL_CALL: tool_name {json_params}
        pattern = r'TOOL_CALL:\s*(\w+)\s*(\{.*?\})'
        matches = re.finditer(pattern, text, re.DOTALL)
        
        for match in matches:
            tool_name = match.group(1)
            params_str = match.group(2)
            try:
                params = json.loads(params_str)
                tool_calls.append({
                    'tool': tool_name,
                    'params': params
                })
            except json.JSONDecodeError:
                console.print(f"[yellow]Не удалось распарсить параметры для {tool_name}[/yellow]")
        
        return tool_calls
    
    def _execute_tool_calls(self, tool_calls: List[Dict]) -> str:
        """Выполнение вызовов инструментов"""
        results = []
        
        for call in tool_calls:
            tool_name = call['tool']
            params = call['params']
            
            if not self.use_mcp or not self.mcp_tools:
                results.append(f"Инструмент {tool_name} недоступен (MCP отключен)")
                continue
            
            console.print(f"[cyan]Выполняю инструмент: {tool_name}[/cyan]")
            result = self.mcp_tools.execute_tool(tool_name, **params)
            
            if result.get('error'):
                results.append(f"Ошибка {tool_name}: {result['error']}")
            else:
                # Форматируем результат для модели
                result_str = json.dumps(result, ensure_ascii=False, indent=2)
                results.append(f"Результат {tool_name}:\n{result_str}")
        
        return "\n\n".join(results)
    
    def ask(self, prompt: str, stream: bool = True, max_iterations: int = 5) -> Generator[str, None, None]:
        """Задать вопрос агенту с поддержкой MCP инструментов"""
        messages = self._build_messages(prompt)
        
        # Сохраняем запрос пользователя
        self.history.append({
            'role': 'user',
            'content': prompt,
            'timestamp': datetime.now().isoformat()
        })
        
        iteration = 0
        full_response = ""
        
        while iteration < max_iterations:
            iteration += 1
            
            # Получаем ответ
            current_response = ""
            if self.provider == "ollama":
                generator = self._call_ollama(messages, stream=stream)
            elif self.provider == "lmstudio":
                generator = self._call_lmstudio(messages, stream=stream)
            elif self.provider == "local_transformers":
                generator = self._call_transformers(messages, stream=stream)
            elif self.provider in ["openai", "openai_compatible", "anthropic", "custom"] or hasattr(self, 'openai_url'):
                generator = self._call_openai_compatible(messages, stream=stream)
            else:
                # Пробуем как OpenAI-совместимый API
                console.print(f"[yellow]Провайдер '{self.provider}' не распознан, пробуем как OpenAI-совместимый API[/yellow]")
                if hasattr(self, 'openai_url'):
                    generator = self._call_openai_compatible(messages, stream=stream)
                else:
                    raise ValueError(f"Неподдерживаемый провайдер: {self.provider}. Укажите base_url в конфигурации для использования как OpenAI-совместимого API.")
            
            for chunk in generator:
                current_response += chunk
                if stream:
                    yield chunk
            
            full_response += current_response
            
            # Проверяем наличие вызовов инструментов
            if self.use_mcp and self.mcp_tools:
                tool_calls = self._parse_tool_calls(current_response)
                
                if tool_calls:
                    # Выполняем инструменты
                    tool_results = self._execute_tool_calls(tool_calls)
                    
                    # Добавляем результаты в контекст и запрашиваем продолжение
                    messages.append({
                        'role': 'assistant',
                        'content': current_response
                    })
                    messages.append({
                        'role': 'user',
                        'content': f"Результаты выполнения инструментов:\n{tool_results}\n\nПродолжи ответ, используя эти результаты."
                    })
                    
                    # Продолжаем цикл для получения финального ответа
                    continue
            
            # Нет вызовов инструментов или они уже обработаны - завершаем
            break
        
        # Сохраняем ответ
        self.history.append({
            'role': 'assistant',
            'content': full_response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Сохраняем историю
        if self.config.get('agent', {}).get('save_history', True):
            self.save_history()
    
    def save_history(self):
        """Сохранение истории диалога"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = self.history_path / f"history_{timestamp}.json"
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def _save_history(self):
        """Приватный метод для обратной совместимости (deprecated)"""
        return self.save_history()
    
    def clear_history(self):
        """Очистка истории диалога"""
        self.history = []
        console.print("[green]История очищена[/green]")
    
    def load_history(self, file_path: str):
        """Загрузка истории из файла"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.history = json.load(f)
        console.print(f"[green]История загружена из {file_path}[/green]")


def main():
    """Основная функция для CLI"""
    agent = CodeAgent()
    
    console.print("\n[bold cyan]🤖 AI Code Agent готов к работе![/bold cyan]")
    console.print("[dim]Введите ваш запрос (или 'exit' для выхода, 'clear' для очистки истории)[/dim]\n")
    
    while True:
        try:
            user_input = input("> ")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]До свидания![/yellow]")
                break
            
            if user_input.lower() == 'clear':
                agent.clear_history()
                continue
            
            if not user_input.strip():
                continue
            
            console.print("\n[cyan]Агент думает...[/cyan]\n")
            
            # Собираем ответ по частям
            response = ""
            for chunk in agent.ask(user_input, stream=True):
                response += chunk
                print(chunk, end='', flush=True)
            
            print("\n")  # Новая строка после ответа
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Прервано пользователем[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")


if __name__ == "__main__":
    main()

