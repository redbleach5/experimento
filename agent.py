"""
AI Agent для помощи в написании кода
Поддерживает локальные модели через Ollama и прямую работу с transformers
"""

import os
import json
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Generator
import requests
from rich.console import Console
from rich.markdown import Markdown
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Импорт MCP инструментов
try:
    from mcp_tools import MCPToolManager, format_tools_for_prompt
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    console = Console()
    console.print("[yellow]MCP tools not available[/yellow]")

if not MCP_AVAILABLE:
    console = Console()
else:
    console = Console()


class CodeAgent:
    """AI агент для помощи в написании кода"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Инициализация агента"""
        self.config = self._load_config(config_path)
        self.provider = self.config['model']['provider']
        self.model_name = self.config['model']['model_name']
        self.history: List[Dict] = []
        self.history_path = Path(self.config['agent']['history_path'])
        self.history_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализация MCP инструментов
        self.use_mcp = self.config.get('mcp', {}).get('enabled', True) and MCP_AVAILABLE
        if self.use_mcp:
            self.mcp_tools = MCPToolManager()
            console.print(f"[green]MCP инструменты загружены: {len(self.mcp_tools.list_tools())} доступно[/green]")
        else:
            self.mcp_tools = None
        
        # Инициализация провайдера
        if self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "lmstudio":
            self._init_lmstudio()
        elif self.provider == "local_transformers":
            self._init_transformers()
        else:
            raise ValueError(f"Неподдерживаемый провайдер: {self.provider}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Загрузка конфигурации"""
        if not os.path.exists(config_path):
            console.print(f"[yellow]Конфигурация не найдена, используем значения по умолчанию[/yellow]")
            return self._default_config()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> Dict:
        """Конфигурация по умолчанию"""
        return {
            'model': {
                'provider': 'ollama',
                'model_name': 'deepseek-coder:6.7b'
            },
            'agent': {
                'system_prompt': 'Ты опытный AI-ассистент для программирования.',
                'history_path': './history'
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
                                    # Ищем модель с похожим именем
                                    for mid in model_ids:
                                        if self.model_name.lower() in mid.lower() or mid.lower() in self.model_name.lower():
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
    
    def _build_messages(self, user_prompt: str) -> List[Dict]:
        """Построение списка сообщений для модели"""
        messages = []
        
        # Системный промпт
        system_prompt = self.config['agent'].get('system_prompt', '')
        
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
        
        # История диалога
        for msg in self.history[-10:]:  # Последние 10 сообщений
            messages.append(msg)
        
        # Текущий запрос
        messages.append({
            'role': 'user',
            'content': user_prompt
        })
        
        return messages
    
    def _call_ollama(self, messages: List[Dict], stream: bool = False) -> Generator[str, None, None]:
        """Вызов Ollama API"""
        url = f"{self.ollama_url}/api/chat"
        
        generation_config = self.config['model']['generation']
        
        payload = {
            'model': self.model_name,
            'messages': messages,
            'stream': stream,
            'options': {
                'temperature': generation_config.get('temperature', 0.2),
                'top_p': generation_config.get('top_p', 0.95),
                'top_k': generation_config.get('top_k', 40),
                'num_predict': generation_config.get('max_tokens', 4096),
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
                        data = json.loads(line)
                        if 'message' in data and 'content' in data['message']:
                            yield data['message']['content']
                        if data.get('done', False):
                            break
            else:
                result = response.json()
                yield result['message']['content']
                
        except requests.exceptions.RequestException as e:
            console.print(f"[red]Ошибка запроса к Ollama: {e}[/red]")
            yield f"Ошибка: {e}"
    
    def _call_lmstudio(self, messages: List[Dict], stream: bool = False) -> Generator[str, None, None]:
        """Вызов LM Studio API (OpenAI-совместимый)"""
        url = f"{self.lmstudio_url}/v1/chat/completions"
        
        generation_config = self.config['model']['generation']
        
        # Преобразуем системный промпт в сообщения
        formatted_messages = []
        for msg in messages:
            if msg['role'] == 'system':
                # LM Studio может не поддерживать system role напрямую, добавляем как user
                formatted_messages.append({
                    'role': 'user',
                    'content': f"System: {msg['content']}"
                })
            else:
                formatted_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # Упрощенный payload для лучшей совместимости
        payload = {
            'model': self.model_name,
            'messages': formatted_messages,
            'stream': stream,
            'temperature': generation_config.get('temperature', 0.7),
            'max_tokens': min(generation_config.get('max_tokens', 4096), 2000),  # Ограничиваем для теста
        }
        
        # Добавляем дополнительные параметры только если нужны
        if generation_config.get('top_p'):
            payload['top_p'] = generation_config.get('top_p')
        
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
        generation_config = self.config['model']['generation']
        
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
            
            if 'error' in result:
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
            else:
                raise ValueError(f"Неподдерживаемый провайдер: {self.provider}")
            
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
        if self.config['agent'].get('save_history', True):
            self._save_history()
    
    def _save_history(self):
        """Сохранение истории диалога"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        history_file = self.history_path / f"history_{timestamp}.json"
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
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

