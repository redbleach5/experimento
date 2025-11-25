"""
Адаптивная система для работы с разными моделями
Автоматически определяет возможности модели и адаптирует параметры
"""

import re
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
import requests
from rich.console import Console

console = Console()


@dataclass
class ModelCapabilities:
    """Возможности модели"""
    max_context: int = 4096
    max_tokens: int = 2048
    supports_streaming: bool = True
    supports_system_prompt: bool = True
    supports_tools: bool = False
    optimal_temperature: float = 0.2
    optimal_top_p: float = 0.95
    optimal_top_k: int = 40
    model_type: str = "unknown"  # "code", "chat", "general"
    estimated_tokens_per_char: float = 0.25  # Примерно 4 символа на токен


class ModelAdapter:
    """Адаптер для работы с разными моделями"""
    
    # База знаний о моделях
    MODEL_DATABASE = {
        # Ollama модели
        "deepseek-coder": {
            "max_context": 16384,
            "max_tokens": 4096,
            "model_type": "code",
            "optimal_temperature": 0.2,
        },
        "deepseek-coder:6.7b": {
            "max_context": 16384,
            "max_tokens": 4096,
            "model_type": "code",
            "optimal_temperature": 0.2,
        },
        "codellama": {
            "max_context": 8192,
            "max_tokens": 2048,
            "model_type": "code",
            "optimal_temperature": 0.2,
        },
        "codellama:13b": {
            "max_context": 8192,
            "max_tokens": 2048,
            "model_type": "code",
            "optimal_temperature": 0.2,
        },
        "qwen2.5-coder": {
            "max_context": 32768,
            "max_tokens": 4096,
            "model_type": "code",
            "optimal_temperature": 0.2,
        },
        "qwen2.5-coder:7b": {
            "max_context": 32768,
            "max_tokens": 4096,
            "model_type": "code",
            "optimal_temperature": 0.2,
        },
        "qwen3-vl-2b-instruct": {
            "max_context": 4096,
            "max_tokens": 2000,
            "model_type": "general",
            "optimal_temperature": 0.3,
        },
        "starcoder2": {
            "max_context": 16384,
            "max_tokens": 4096,
            "model_type": "code",
            "optimal_temperature": 0.2,
        },
        "starcoder2:7b": {
            "max_context": 16384,
            "max_tokens": 4096,
            "model_type": "code",
            "optimal_temperature": 0.2,
        },
        # Общие паттерны
        "llama": {
            "max_context": 4096,
            "max_tokens": 2048,
            "model_type": "general",
        },
        "mistral": {
            "max_context": 8192,
            "max_tokens": 2048,
            "model_type": "general",
        },
        "mixtral": {
            "max_context": 32768,
            "max_tokens": 4096,
            "model_type": "general",
        },
    }
    
    def __init__(self, provider: str, model_name: str, base_url: str = None):
        """
        Инициализация адаптера
        
        Args:
            provider: Провайдер ("ollama", "lmstudio", "openai", "anthropic", "custom")
            model_name: Имя модели
            base_url: Базовый URL API
        """
        self.provider = provider
        self.model_name = model_name
        self.base_url = base_url
        self.capabilities = self._detect_capabilities()
        self._tested = False
    
    def _detect_capabilities(self) -> ModelCapabilities:
        """Автоматическое определение возможностей модели"""
        # Сначала пробуем получить информацию от API (самый точный способ)
        api_capabilities = None
        if self.provider == "ollama" and self.base_url:
            api_capabilities = self._detect_from_ollama_api()
        elif self.provider == "lmstudio" and self.base_url:
            api_capabilities = self._detect_from_lmstudio_api()
        elif self.provider in ["openai", "openai_compatible", "anthropic", "custom"] and self.base_url:
            # Для OpenAI-совместимых API пробуем определить через API
            api_capabilities = self._detect_from_openai_compatible_api()
        
        # Если получили информацию от API, используем её
        if api_capabilities:
            console.print(f"[green]✓ Возможности модели определены через API[/green]")
            return api_capabilities
        
        # Если API не дал информации, пробуем базу данных
        capabilities = self._get_from_database()
        
        # Если не нашли в базе, пробуем определить по имени
        if capabilities.max_context == 4096:  # Значение по умолчанию
            capabilities = self._detect_from_name()
            console.print(f"[yellow]⚠ Возможности модели определены по имени (используются значения по умолчанию)[/yellow]")
        else:
            console.print(f"[green]✓ Возможности модели найдены в базе данных[/green]")
        
        return capabilities
    
    def _get_from_database(self) -> ModelCapabilities:
        """Получение информации из базы данных"""
        # Пробуем точное совпадение
        if self.model_name in self.MODEL_DATABASE:
            info = self.MODEL_DATABASE[self.model_name]
            return ModelCapabilities(
                max_context=info.get("max_context", 4096),
                max_tokens=info.get("max_tokens", 2048),
                model_type=info.get("model_type", "general"),
                optimal_temperature=info.get("optimal_temperature", 0.2),
            )
        
        # Пробуем частичное совпадение
        for db_name, info in self.MODEL_DATABASE.items():
            if db_name in self.model_name or self.model_name in db_name:
                return ModelCapabilities(
                    max_context=info.get("max_context", 4096),
                    max_tokens=info.get("max_tokens", 2048),
                    model_type=info.get("model_type", "general"),
                    optimal_temperature=info.get("optimal_temperature", 0.2),
                )
        
        return ModelCapabilities()
    
    def _detect_from_name(self) -> ModelCapabilities:
        """Определение возможностей по имени модели (универсальный метод)"""
        name_lower = self.model_name.lower()
        
        # Определяем тип модели
        model_type = "general"
        if any(x in name_lower for x in ["coder", "code", "starcoder", "wizardcoder", "phind"]):
            model_type = "code"
        elif any(x in name_lower for x in ["chat", "instruct", "conversational"]):
            model_type = "chat"
        
        # Определяем размер контекста по размеру модели и архитектуре
        max_context = 4096  # Консервативное значение по умолчанию
        
        # Современные модели часто имеют большой контекст
        if any(x in name_lower for x in ["qwen2.5", "qwen2", "qwen-2"]):
            max_context = 32768
        elif "qwen" in name_lower:
            max_context = 8192
        elif any(x in name_lower for x in ["llama3.1", "llama-3.1", "llama3", "llama-3"]):
            max_context = 128000  # Llama 3.1 поддерживает 128K контекст
        elif "llama" in name_lower:
            max_context = 8192
        elif any(x in name_lower for x in ["mistral", "mixtral"]):
            max_context = 32768
        elif "deepseek" in name_lower:
            max_context = 16384
        elif "phi" in name_lower:
            max_context = 4096
        elif "gemma" in name_lower:
            max_context = 8192
        elif "gemini" in name_lower:
            max_context = 32768
        elif "claude" in name_lower:
            max_context = 200000  # Claude 3 поддерживает 200K
        elif "gpt-4" in name_lower:
            max_context = 128000
        elif "gpt-3.5" in name_lower or "gpt3" in name_lower:
            max_context = 16384
        elif "gpt" in name_lower:
            max_context = 4096
        
        # Определяем по размеру параметров (если указан)
        if "7b" in name_lower or "6.7b" in name_lower or "8b" in name_lower:
            if max_context == 4096:  # Если не определили по архитектуре
                max_context = 16384
        elif "13b" in name_lower:
            if max_context == 4096:
                max_context = 8192
        elif any(x in name_lower for x in ["34b", "32b", "30b"]):
            if max_context == 4096:
                max_context = 32768
        elif "70b" in name_lower:
            if max_context == 4096:
                max_context = 8192
        
        # Определяем оптимальную температуру
        optimal_temp = 0.2 if model_type == "code" else 0.3
        
        return ModelCapabilities(
            max_context=max_context,
            max_tokens=min(4096, max_context // 2),
            model_type=model_type,
            optimal_temperature=optimal_temp,
        )
    
    def _detect_from_ollama_api(self) -> Optional[ModelCapabilities]:
        """Определение возможностей через Ollama API"""
        try:
            url = f"{self.base_url}/api/show"
            response = requests.post(
                url,
                json={"name": self.model_name},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Извлекаем информацию о контексте
                context_size = 4096
                
                # Пробуем разные способы получения размера контекста
                if "modelfile" in data:
                    modelfile = data["modelfile"]
                    # Ищем параметр num_ctx или context_size
                    match = re.search(r'num_ctx[:\s]+(\d+)', modelfile, re.IGNORECASE)
                    if match:
                        context_size = int(match.group(1))
                    else:
                        match = re.search(r'context_size[:\s]+(\d+)', modelfile, re.IGNORECASE)
                        if match:
                            context_size = int(match.group(1))
                
                # Также проверяем параметры модели напрямую
                if "parameters" in data:
                    params = data["parameters"]
                    if "num_ctx" in params:
                        context_size = int(params["num_ctx"])
                    elif "context_size" in params:
                        context_size = int(params["context_size"])
                
                # Определяем тип модели по имени и параметрам
                model_type = "general"
                name_lower = self.model_name.lower()
                if any(x in name_lower for x in ["code", "coder", "starcoder"]):
                    model_type = "code"
                elif any(x in name_lower for x in ["chat", "instruct"]):
                    model_type = "chat"
                
                # Определяем оптимальную температуру
                optimal_temp = 0.2 if model_type == "code" else 0.3
                
                return ModelCapabilities(
                    max_context=context_size,
                    max_tokens=min(4096, context_size // 2),
                    model_type=model_type,
                    optimal_temperature=optimal_temp,
                )
        except Exception as e:
            console.print(f"[yellow]Не удалось определить возможности через Ollama API: {e}[/yellow]")
        
        return None
    
    def _detect_from_lmstudio_api(self) -> Optional[ModelCapabilities]:
        """Определение возможностей через LM Studio API (OpenAI-совместимый)"""
        try:
            # Пробуем получить информацию о модели через OpenAI-совместимый API
            url = f"{self.base_url}/v1/models"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                
                # Ищем нашу модель в списке
                model_info = None
                for model in models:
                    model_id = model.get('id') or model.get('model') or model.get('name') or ''
                    # Проверяем точное совпадение или частичное
                    if (model_id == self.model_name or 
                        self.model_name.lower() in model_id.lower() or
                        model_id.lower() in self.model_name.lower()):
                        model_info = model
                        break
                
                if model_info:
                    # Пробуем извлечь информацию о контексте
                    context_size = 4096  # Значение по умолчанию
                    
                    # Проверяем разные поля
                    if 'context_length' in model_info:
                        context_size = int(model_info['context_length'])
                    elif 'max_context' in model_info:
                        context_size = int(model_info['max_context'])
                    elif 'context_size' in model_info:
                        context_size = int(model_info['context_size'])
                    
                    # Определяем тип модели
                    model_type = "general"
                    name_lower = self.model_name.lower()
                    if any(x in name_lower for x in ["code", "coder", "starcoder"]):
                        model_type = "code"
                    elif any(x in name_lower for x in ["chat", "instruct"]):
                        model_type = "chat"
                    
                    optimal_temp = 0.2 if model_type == "code" else 0.3
                    
                    return ModelCapabilities(
                        max_context=context_size,
                        max_tokens=min(4096, context_size // 2),
                        model_type=model_type,
                        optimal_temperature=optimal_temp,
                    )
        except Exception as e:
            console.print(f"[yellow]Не удалось определить возможности через LM Studio API: {e}[/yellow]")
        
        return None
    
    def _detect_from_openai_compatible_api(self) -> Optional[ModelCapabilities]:
        """Определение возможностей через OpenAI-совместимый API"""
        try:
            # Пробуем получить информацию о модели
            url = f"{self.base_url}/models"
            headers = {}
            
            # Если есть API ключ в переменных окружения
            import os
            if self.provider == "openai":
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    headers['Authorization'] = f'Bearer {api_key}'
            elif self.provider == "anthropic":
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if api_key:
                    headers['x-api-key'] = api_key
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                
                # Ищем нашу модель
                for model in models:
                    model_id = model.get('id') or model.get('name') or ''
                    if (model_id == self.model_name or 
                        self.model_name.lower() in model_id.lower()):
                        # Пробуем извлечь информацию о контексте
                        context_size = 4096
                        if 'context_length' in model:
                            context_size = int(model['context_length'])
                        elif 'max_context' in model:
                            context_size = int(model['max_context'])
                        
                        # Определяем тип модели
                        model_type = "general"
                        name_lower = self.model_name.lower()
                        if any(x in name_lower for x in ["code", "coder"]):
                            model_type = "code"
                        
                        optimal_temp = 0.2 if model_type == "code" else 0.3
                        
                        return ModelCapabilities(
                            max_context=context_size,
                            max_tokens=min(4096, context_size // 2),
                            model_type=model_type,
                            optimal_temperature=optimal_temp,
                        )
        except Exception as e:
            console.print(f"[yellow]Не удалось определить возможности через OpenAI-совместимый API: {e}[/yellow]")
        
        return None
    
    def get_optimal_config(self, user_config: Dict) -> Dict:
        """
        Получает оптимальную конфигурацию для модели
        
        Args:
            user_config: Конфигурация пользователя
        
        Returns:
            Оптимизированная конфигурация
        """
        config = user_config.copy()
        
        # Адаптируем max_tokens под возможности модели
        if "generation" not in config:
            config["generation"] = {}
        
        max_tokens = config["generation"].get("max_tokens", 4096)
        if max_tokens > self.capabilities.max_tokens:
            config["generation"]["max_tokens"] = self.capabilities.max_tokens
            console.print(f"[yellow]max_tokens ограничен до {self.capabilities.max_tokens} для модели {self.model_name}[/yellow]")
        
        # Адаптируем температуру для типа модели
        if "temperature" not in config["generation"]:
            config["generation"]["temperature"] = self.capabilities.optimal_temperature
        elif self.capabilities.model_type == "code":
            # Для кодовых моделей рекомендуем низкую температуру
            if config["generation"]["temperature"] > 0.3:
                console.print(f"[yellow]Температура снижена до 0.2 для кодовой модели[/yellow]")
                config["generation"]["temperature"] = 0.2
        
        # Адаптируем top_p и top_k
        if "top_p" not in config["generation"]:
            config["generation"]["top_p"] = self.capabilities.optimal_top_p
        if "top_k" not in config["generation"]:
            config["generation"]["top_k"] = self.capabilities.optimal_top_k
        
        return config
    
    def estimate_tokens(self, text: str) -> int:
        """
        Оценивает количество токенов в тексте
        
        Args:
            text: Текст для оценки
        
        Returns:
            Примерное количество токенов
        """
        # Простая оценка: примерно 4 символа на токен для английского
        # Для русского и кода может быть меньше
        chars = len(text)
        
        # Учитываем тип модели
        if self.capabilities.model_type == "code":
            # Код обычно более компактный
            tokens_per_char = 0.3
        else:
            tokens_per_char = 0.25
        
        return int(chars * tokens_per_char)
    
    def get_max_context_for_project(self) -> int:
        """
        Получает максимальный размер контекста для проекта
        
        Returns:
            Максимальный размер в символах
        """
        # Для маленьких моделей (менее 6K) используем более агрессивные ограничения
        if self.capabilities.max_context < 6000:
            # Только 15% для проекта, остальное для системного промпта, истории и ответа
            project_ratio = 0.15
        elif self.capabilities.max_context < 10000:
            # Для средних моделей (6K-10K) - 20%
            project_ratio = 0.20
        else:
            # Для больших моделей - 30%
            project_ratio = 0.30
        
        max_project_tokens = int(self.capabilities.max_context * project_ratio)
        
        # Конвертируем в символы (примерно 4 символа на токен, но для кода может быть меньше)
        # Используем консервативную оценку - 3 символа на токен
        max_project_chars = max_project_tokens * 3
        
        # Минимальный лимит для очень маленьких моделей
        if self.capabilities.max_context <= 4096:
            max_project_chars = min(max_project_chars, 1000)  # Максимум 1000 символов
        
        return max_project_chars
    
    def get_max_relevant_files_size(self) -> int:
        """
        Получает максимальный размер для релевантных файлов
        
        Returns:
            Максимальный размер в символах
        """
        # Для маленьких моделей - более агрессивные ограничения
        if self.capabilities.max_context < 6000:
            relevant_ratio = 0.10  # Только 10%
        elif self.capabilities.max_context < 10000:
            relevant_ratio = 0.12  # 12%
        else:
            relevant_ratio = 0.15  # 15%
        
        max_relevant_tokens = int(self.capabilities.max_context * relevant_ratio)
        # Консервативная оценка - 3 символа на токен
        max_relevant_chars = max_relevant_tokens * 3
        
        # Для очень маленьких моделей - жесткий лимит
        if self.capabilities.max_context <= 4096:
            max_relevant_chars = min(max_relevant_chars, 500)  # Максимум 500 символов
        
        return max_relevant_chars
    
    def should_include_project_context(self, history_size: int = 0) -> bool:
        """
        Определяет, стоит ли включать контекст проекта
        
        Args:
            history_size: Размер истории в токенах
        
        Returns:
            True если можно включить контекст проекта
        """
        # Для очень маленьких моделей (4K) - не включаем автоматически
        if self.capabilities.max_context <= 4096:
            return False
        
        # Для маленьких моделей (4K-6K) - только если нет истории
        if self.capabilities.max_context < 6000:
            return history_size == 0
        
        # Если история уже занимает много места, не включаем
        history_ratio = history_size / self.capabilities.max_context
        if history_ratio > 0.4:
            return False
        
        return True
    
    def format_messages_for_model(self, messages: List[Dict]) -> List[Dict]:
        """
        Форматирует сообщения под конкретную модель
        
        Args:
            messages: Список сообщений
        
        Returns:
            Отформатированные сообщения
        """
        formatted = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Некоторые модели не поддерживают system role
            if role == "system" and not self.capabilities.supports_system_prompt:
                # Преобразуем system в user с префиксом
                formatted.append({
                    "role": "user",
                    "content": f"System instructions: {content}"
                })
            else:
                formatted.append({
                    "role": role,
                    "content": content
                })
        
        return formatted
    
    def optimize_context(self, context: str, max_size: int = None) -> str:
        """
        Оптимизирует контекст под размер модели
        
        Args:
            context: Контекст для оптимизации
            max_size: Максимальный размер в символах
        
        Returns:
            Оптимизированный контекст
        """
        if max_size is None:
            max_size = self.get_max_context_for_project()
        
        if len(context) <= max_size:
            return context
        
        # Обрезаем контекст, сохраняя важные части
        # Сначала пытаемся обрезать по абзацам
        lines = context.split('\n')
        
        # Сохраняем начало (структура проекта)
        important_start = []
        important_end = []
        middle = []
        
        in_important = True
        for line in lines:
            if len('\n'.join(important_start)) < max_size * 0.4:
                important_start.append(line)
            elif len('\n'.join(important_end)) < max_size * 0.3:
                important_end.insert(0, line)
            else:
                middle.append(line)
        
        # Если всё ещё слишком длинно, обрезаем
        result = '\n'.join(important_start)
        if len(result) < max_size * 0.7:
            result += '\n... [промежуточный контекст обрезан] ...\n'
            result += '\n'.join(important_end[-int(max_size * 0.3):])
        
        # Финальная обрезка
        if len(result) > max_size:
            result = result[:max_size] + "\n... [контекст обрезан]"
        
        return result
    
    def get_info(self) -> Dict:
        """Получает информацию о возможностях модели"""
        return {
            "model_name": self.model_name,
            "provider": self.provider,
            "max_context": self.capabilities.max_context,
            "max_tokens": self.capabilities.max_tokens,
            "model_type": self.capabilities.model_type,
            "optimal_temperature": self.capabilities.optimal_temperature,
            "supports_system_prompt": self.capabilities.supports_system_prompt,
            "supports_streaming": self.capabilities.supports_streaming,
        }
    
    def print_info(self):
        """Выводит информацию о модели"""
        info = self.get_info()
        console.print(f"\n[bold cyan]Информация о модели:[/bold cyan]")
        console.print(f"  Модель: {info['model_name']}")
        console.print(f"  Провайдер: {info['provider']}")
        console.print(f"  Макс. контекст: {info['max_context']} токенов")
        console.print(f"  Макс. генерация: {info['max_tokens']} токенов")
        console.print(f"  Тип: {info['model_type']}")
        console.print(f"  Оптимальная температура: {info['optimal_temperature']}")
        console.print(f"  Поддержка system prompt: {info['supports_system_prompt']}")


def create_model_adapter(provider: str, model_name: str, base_url: str = None) -> ModelAdapter:
    """
    Создаёт адаптер для модели
    
    Args:
        provider: Провайдер ("ollama", "lmstudio")
        model_name: Имя модели
        base_url: Базовый URL API
    
    Returns:
        ModelAdapter
    """
    return ModelAdapter(provider, model_name, base_url)

