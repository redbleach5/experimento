"""
MCP (Model Context Protocol) инструменты для агента
Позволяет агенту использовать внешние инструменты и получать контекст
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import requests
import logging

logger = logging.getLogger(__name__)


class MCPTool:
    """Базовый класс для MCP инструментов"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнение инструмента"""
        raise NotImplementedError


class FileReadTool(MCPTool):
    """Чтение файлов с безопасной обработкой кодировок"""
    
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Читает содержимое файла. Параметры: file_path (str) - путь к файлу"
        )
    
    def execute(self, file_path: str) -> Dict[str, Any]:
        try:
            from utils.file_utils import read_file_safe
            
            path = Path(file_path)
            if not path.exists():
                return {"error": f"Файл не найден: {file_path}"}
            
            if not path.is_file():
                return {"error": f"Путь не является файлом: {file_path}"}
            
            content = read_file_safe(path, max_size=10*1024*1024)  # 10MB максимум
            
            if content is None:
                return {"error": f"Не удалось прочитать файл: {file_path}"}
            
            return {
                "success": True,
                "content": content,
                "file_path": str(path),
                "size": len(content)
            }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка чтения файла {file_path}: {e}", exc_info=True)
            return {"error": f"Ошибка чтения файла: {str(e)}"}


class FileWriteTool(MCPTool):
    """Запись в файлы с безопасной обработкой"""
    
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Записывает содержимое в файл. Параметры: file_path (str), content (str)"
        )
    
    def execute(self, file_path: str, content: str) -> Dict[str, Any]:
        try:
            from utils.file_utils import write_file_safe
            
            path = Path(file_path)
            
            # Определяем разрешенную корневую директорию (текущая рабочая директория)
            allowed_root = Path.cwd().resolve()
            
            # Нормализуем путь
            if not path.is_absolute():
                path = allowed_root / path
            else:
                # Если абсолютный путь, проверяем что он в allowed_root
                if not str(path.resolve()).startswith(str(allowed_root)):
                    return {"error": f"Путь вне разрешенной директории: {file_path}"}
            
            resolved_path = path.resolve()
            
            # Строгая проверка на path traversal
            try:
                relative = resolved_path.relative_to(allowed_root)
                # Проверяем, что в относительном пути нет ..
                if '..' in str(relative) or str(relative).startswith('..'):
                    return {"error": "Path traversal detected: путь содержит '..'"}
            except ValueError:
                # Путь не находится внутри allowed_root
                return {"error": f"Путь вне разрешенной директории: {file_path}"}
            
            # Дополнительная проверка - исходный путь не должен содержать опасные символы
            if '..' in str(file_path) or file_path.startswith('/') or (os.name == 'nt' and ':' in file_path and not file_path.startswith(allowed_root.drive)):
                # Разрешаем только если это безопасный относительный путь
                if not (file_path.replace('\\', '/').startswith('./') or not file_path.startswith('/')):
                    return {"error": "Небезопасный путь: используйте относительные пути"}
            
            success = write_file_safe(resolved_path, content, encoding='utf-8', create_dirs=True)
            
            if not success:
                return {"error": f"Не удалось записать файл: {file_path}"}
            
            return {
                "success": True,
                "file_path": str(resolved_path),
                "bytes_written": len(content.encode('utf-8'))
            }
        except (OSError, IOError, PermissionError) as e:
            logger.error(f"Ошибка записи файла {file_path}: {e}", exc_info=True)
            return {"error": f"Ошибка записи файла: {str(e)}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при записи файла {file_path}: {e}", exc_info=True)
            return {"error": f"Ошибка записи файла: {str(e)}"}


class ListFilesTool(MCPTool):
    """Список файлов в директории"""
    
    def __init__(self):
        super().__init__(
            name="list_files",
            description="Получает список файлов в директории. Параметры: directory (str, optional) - путь к директории"
        )
    
    def execute(self, directory: str = ".") -> Dict[str, Any]:
        try:
            path = Path(directory)
            if not path.exists():
                return {"error": f"Директория не найдена: {directory}"}
            
            if not path.is_dir():
                return {"error": f"Путь не является директорией: {directory}"}
            
            files = []
            dirs = []
            
            for item in path.iterdir():
                if item.is_file():
                    files.append({
                        "name": item.name,
                        "path": str(item),
                        "size": item.stat().st_size
                    })
                elif item.is_dir():
                    dirs.append({
                        "name": item.name,
                        "path": str(item)
                    })
            
            return {
                "success": True,
                "directory": str(path),
                "files": files,
                "directories": dirs,
                "total_files": len(files),
                "total_dirs": len(dirs)
            }
        except (OSError, IOError, PermissionError) as e:
            logger.error(f"Ошибка чтения директории {directory}: {e}")
            return {"error": f"Ошибка чтения директории: {str(e)}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при чтении директории {directory}: {e}", exc_info=True)
            return {"error": f"Ошибка чтения директории: {str(e)}"}


class ExecuteCommandTool(MCPTool):
    """Выполнение команд с валидацией безопасности"""
    
    # Whitelist разрешенных команд
    ALLOWED_COMMANDS = [
        'git', 'python', 'pip', 'npm', 'node', 'yarn', 'pwd', 'ls', 'dir',
        'cd', 'echo', 'cat', 'type', 'head', 'tail', 'grep', 'find'
    ]
    
    # Blacklist опасных паттернов
    DANGEROUS_PATTERNS = [
        'rm ', 'del ', 'format ', 'sudo', 'su ', 'chmod 777', 'chown',
        'dd if=', 'mkfs', 'fdisk', '> /dev/', '| nc ', '| bash', '| sh',
        'curl |', 'wget |', 'python -c', 'eval', 'exec', '__import__'
    ]
    
    # Максимальная длина команды
    MAX_COMMAND_LENGTH = 1000
    
    def __init__(self):
        super().__init__(
            name="execute_command",
            description="Выполняет команду в shell с проверкой безопасности. Параметры: command (str) - команда для выполнения"
        )
    
    def _validate_command(self, command: str) -> Tuple[bool, Optional[str]]:
        """
        Валидация команды на безопасность
        
        Returns:
            (is_valid, error_message)
        """
        if not command or not command.strip():
            return False, "Команда пуста"
        
        # Проверка длины
        if len(command) > self.MAX_COMMAND_LENGTH:
            return False, f"Команда слишком длинная (максимум {self.MAX_COMMAND_LENGTH} символов)"
        
        command_lower = command.lower().strip()
        
        # Запрещаем все опасные символы и конструкции
        dangerous_chars = ['|', '&&', ';', '`', '$', '(', ')', '<', '>', '\n', '\r']
        for char in dangerous_chars:
            if char in command:
                return False, f"Команда содержит опасные символы: '{char}'"
        
        # Проверка на опасные паттерны
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in command_lower:
                return False, f"Команда содержит опасный паттерн: {pattern}"
        
        # Разрешаем только простые команды из whitelist
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return False, "Команда пуста после разбора"
        
        first_cmd = cmd_parts[0].lower()
        
        # Проверяем whitelist
        if first_cmd not in self.ALLOWED_COMMANDS:
            # Разрешаем только относительные пути к скриптам в текущей директории
            if first_cmd.startswith('./') or first_cmd.startswith('.\\'):
                # Дополнительная проверка - путь должен быть простым
                if '..' in first_cmd or '/' in first_cmd[2:] or '\\' in first_cmd[2:]:
                    return False, "Небезопасный путь к скрипту"
            else:
                return False, f"Команда '{first_cmd}' не разрешена. Разрешенные: {', '.join(self.ALLOWED_COMMANDS)}"
        
        return True, None
    
    def execute(self, command: str) -> Dict[str, Any]:
        # Валидация команды
        is_valid, error_msg = self._validate_command(command)
        if not is_valid:
            return {"error": error_msg or "Команда не прошла валидацию"}
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8',
                errors='replace'
            )
            
            return {
                "success": True,
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"error": "Команда превысила таймаут 30 секунд"}
        except Exception as e:
            return {"error": f"Ошибка выполнения команды: {str(e)}"}


class WebSearchTool(MCPTool):
    """Поиск в интернете"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Ищет информацию в интернете. Параметры: query (str) - поисковый запрос"
        )
    
    def execute(self, query: str) -> Dict[str, Any]:
        # Простая реализация через DuckDuckGo или другой сервис
        try:
            # Можно использовать duckduckgo-search или другие библиотеки
            return {
                "success": True,
                "query": query,
                "note": "Web search requires additional setup. Use execute_command with curl/wget for now."
            }
        except Exception as e:
            return {"error": f"Ошибка поиска: {str(e)}"}


class SendSMSTool(MCPTool):
    """Отправка SMS через API"""
    
    def __init__(self):
        super().__init__(
            name="send_sms",
            description="Отправляет SMS сообщение. Параметры: phone (str) - номер телефона, message (str) - текст сообщения"
        )
    
    def execute(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Отправка SMS через различные сервисы
        Требует настройки API ключей в переменных окружения
        """
        import os
        
        # Проверяем доступные сервисы
        twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_from = os.getenv('TWILIO_PHONE_NUMBER')
        
        # Twilio
        if twilio_sid and twilio_token and twilio_from:
            try:
                from twilio.rest import Client
                client = Client(twilio_sid, twilio_token)
                message_obj = client.messages.create(
                    body=message,
                    from_=twilio_from,
                    to=phone
                )
                return {
                    "success": True,
                    "service": "Twilio",
                    "message_sid": message_obj.sid,
                    "status": message_obj.status,
                    "phone": phone
                }
            except ImportError:
                return {"error": "Twilio library not installed. Run: pip install twilio"}
            except Exception as e:
                return {"error": f"Ошибка отправки через Twilio: {str(e)}"}
        
        # Альтернатива: через email-to-SMS шлюзы
        # Или через другие сервисы
        
        return {
            "error": "SMS service not configured",
            "note": "Для отправки SMS нужно настроить один из сервисов:",
            "options": [
                "1. Twilio: установите переменные TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER",
                "2. Или используйте execute_command с curl для других API"
            ],
            "phone": phone,
            "message": message[:50] + "..." if len(message) > 50 else message
        }


class SendNotificationTool(MCPTool):
    """Отправка уведомлений"""
    
    def __init__(self):
        super().__init__(
            name="send_notification",
            description="Отправляет уведомление. Параметры: title (str), message (str), method (str) - 'desktop', 'email', 'sms'"
        )
    
    def execute(self, title: str, message: str, method: str = "desktop") -> Dict[str, Any]:
        try:
            if method == "desktop":
                import subprocess
                import platform
                import sys
                
                # Определяем ОС
                system = platform.system()
                
                try:
                    if system == "Windows":
                        # Windows notification через PowerShell
                        # Экранируем специальные символы
                        safe_message = message.replace("'", "''").replace('"', '`"')
                        safe_title = title.replace("'", "''").replace('"', '`"')
                        subprocess.run([
                            "powershell",
                            "-Command",
                            f"[reflection.assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('{safe_message}', '{safe_title}')"
                        ], timeout=5, capture_output=True, check=False)
                        return {"success": True, "method": "desktop", "title": title, "platform": "Windows"}
                    elif system == "Darwin":  # macOS
                        # macOS notification через osascript
                        subprocess.run([
                            "osascript",
                            "-e",
                            f'display notification "{message}" with title "{title}"'
                        ], timeout=5, capture_output=True, check=False)
                        return {"success": True, "method": "desktop", "title": title, "platform": "macOS"}
                    elif system == "Linux":
                        # Linux notification через notify-send
                        subprocess.run([
                            "notify-send",
                            title,
                            message
                        ], timeout=5, capture_output=True, check=False)
                        return {"success": True, "method": "desktop", "title": title, "platform": "Linux"}
                    else:
                        return {"success": False, "error": f"Unsupported platform: {system}"}
                except FileNotFoundError:
                    return {"success": False, "error": f"Notification tool not found for {system}"}
                except Exception as e:
                    return {"success": False, "error": f"Failed to send notification: {str(e)}"}
            
            elif method == "email":
                # Email через SMTP
                import smtplib
                from email.mime.text import MIMEText
                import os
                
                smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
                smtp_port = int(os.getenv('SMTP_PORT', '587'))
                email_from = os.getenv('EMAIL_FROM')
                email_to = os.getenv('EMAIL_TO')
                email_password = os.getenv('EMAIL_PASSWORD')
                
                if not all([email_from, email_to, email_password]):
                    return {"error": "Email not configured. Set EMAIL_FROM, EMAIL_TO, EMAIL_PASSWORD"}
                
                msg = MIMEText(message)
                msg['Subject'] = title
                msg['From'] = email_from
                msg['To'] = email_to
                
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(email_from, email_password)
                    server.send_message(msg)
                
                return {"success": True, "method": "email", "to": email_to}
            
            else:
                return {"error": f"Unknown method: {method}"}
                
        except Exception as e:
            return {"error": f"Ошибка отправки уведомления: {str(e)}"}


class GetProjectStructureTool(MCPTool):
    """Получение структуры проекта"""
    
    def __init__(self):
        super().__init__(
            name="get_project_structure",
            description="Получает структуру проекта. Параметры: max_depth (int, optional) - максимальная глубина вложенности (по умолчанию 3)"
        )
    
    def execute(self, max_depth: int = 3) -> Dict[str, Any]:
        try:
            from project_context import ProjectContext
            context = ProjectContext()
            structure = context.get_project_structure(max_depth=max_depth, include_files=True)
            return {
                "success": True,
                "structure": structure,
                "project_root": str(context.project_root)
            }
        except ImportError:
            return {"error": "ProjectContext не доступен. Установите project_context.py"}
        except Exception as e:
            return {"error": f"Ошибка получения структуры проекта: {str(e)}"}


class GetProjectContextTool(MCPTool):
    """Получение контекста проекта"""
    
    def __init__(self):
        super().__init__(
            name="get_project_context",
            description="Получает полный контекст проекта (структура, README, конфиги, основные файлы)"
        )
    
    def execute(self) -> Dict[str, Any]:
        try:
            from project_context import ProjectContext
            context = ProjectContext()
            summary = context.get_project_summary()
            return {
                "success": True,
                "context": summary,
                "project_root": str(context.project_root)
            }
        except ImportError:
            return {"error": "ProjectContext не доступен. Установите project_context.py"}
        except Exception as e:
            return {"error": f"Ошибка получения контекста проекта: {str(e)}"}


class MCPToolManager:
    """Менеджер MCP инструментов"""
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Регистрация стандартных инструментов"""
        default_tools = [
            FileReadTool(),
            FileWriteTool(),
            ListFilesTool(),
            ExecuteCommandTool(),
            WebSearchTool(),
            SendSMSTool(),
            SendNotificationTool()
        ]
        
        # Добавляем инструменты для работы с контекстом проекта, если доступны
        try:
            from project_context import ProjectContext
            default_tools.extend([
                GetProjectStructureTool(),
                GetProjectContextTool()
            ])
        except ImportError:
            pass  # ProjectContext не доступен, пропускаем эти инструменты
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: MCPTool):
        """Регистрация нового инструмента"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Получение инструмента по имени"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """Список всех доступных инструментов"""
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools.values()
        ]
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """Выполнение инструмента"""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Инструмент не найден: {name}"}
        
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return {"error": f"Ошибка выполнения инструмента: {str(e)}"}


def format_tools_for_prompt(tool_manager: MCPToolManager) -> str:
    """Форматирование списка инструментов для промпта"""
    tools = tool_manager.list_tools()
    
    if not tools:
        return ""
    
    lines = ["\nДоступные инструменты (MCP):"]
    lines.append("-" * 50)
    
    for tool in tools:
        lines.append(f"- {tool['name']}: {tool['description']}")
    
    lines.append("\nДля использования инструмента в ответе укажите:")
    lines.append("TOOL_CALL: <tool_name> <json_parameters>")
    lines.append("Пример: TOOL_CALL: read_file {\"file_path\": \"config.yaml\"}")
    
    return "\n".join(lines)

