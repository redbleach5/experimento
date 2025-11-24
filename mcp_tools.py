"""
MCP (Model Context Protocol) инструменты для агента
Позволяет агенту использовать внешние инструменты и получать контекст
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests


class MCPTool:
    """Базовый класс для MCP инструментов"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Выполнение инструмента"""
        raise NotImplementedError


class FileReadTool(MCPTool):
    """Чтение файлов"""
    
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Читает содержимое файла. Параметры: file_path (str) - путь к файлу"
        )
    
    def execute(self, file_path: str) -> Dict[str, Any]:
        try:
            path = Path(file_path)
            if not path.exists():
                return {"error": f"Файл не найден: {file_path}"}
            
            if not path.is_file():
                return {"error": f"Путь не является файлом: {file_path}"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "file_path": str(path),
                "size": len(content)
            }
        except Exception as e:
            return {"error": f"Ошибка чтения файла: {str(e)}"}


class FileWriteTool(MCPTool):
    """Запись в файлы"""
    
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Записывает содержимое в файл. Параметры: file_path (str), content (str)"
        )
    
    def execute(self, file_path: str, content: str) -> Dict[str, Any]:
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": str(path),
                "bytes_written": len(content.encode('utf-8'))
            }
        except Exception as e:
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
        except Exception as e:
            return {"error": f"Ошибка чтения директории: {str(e)}"}


class ExecuteCommandTool(MCPTool):
    """Выполнение команд"""
    
    def __init__(self):
        super().__init__(
            name="execute_command",
            description="Выполняет команду в shell. Параметры: command (str) - команда для выполнения"
        )
    
    def execute(self, command: str) -> Dict[str, Any]:
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
                # Windows notification
                import subprocess
                try:
                    subprocess.run([
                        "powershell",
                        "-Command",
                        f"[reflection.assembly]::LoadWithPartialName('System.Windows.Forms'); [System.Windows.Forms.MessageBox]::Show('{message}', '{title}')"
                    ], timeout=5, capture_output=True)
                    return {"success": True, "method": "desktop", "title": title}
                except:
                    # Fallback для других ОС
                    return {"success": True, "method": "desktop", "note": "Notification sent (if supported)"}
            
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

