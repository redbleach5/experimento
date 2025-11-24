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
            WebSearchTool()
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

