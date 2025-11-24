"""Тест MCP инструментов"""
from mcp_tools import MCPToolManager

print("=" * 70)
print("ТЕСТ MCP ИНСТРУМЕНТОВ")
print("=" * 70)
print()

tm = MCPToolManager()

print(f"Доступно инструментов: {len(tm.list_tools())}")
print()

# Тест 1: Список файлов
print("[1] Тест list_files...")
result = tm.execute_tool("list_files", directory=".")
if "error" not in result:
    print(f"  [OK] Найдено файлов: {result.get('total_files', 0)}")
    print(f"  Найдено директорий: {result.get('total_dirs', 0)}")
else:
    print(f"  [ERROR] {result['error']}")
print()

# Тест 2: Чтение файла
print("[2] Тест read_file...")
result = tm.execute_tool("read_file", file_path="config.yaml")
if "error" not in result:
    print(f"  [OK] Файл прочитан, размер: {result.get('size', 0)} байт")
    print(f"  Первые 100 символов: {result.get('content', '')[:100]}...")
else:
    print(f"  [ERROR] {result['error']}")
print()

# Тест 3: Выполнение команды
print("[3] Тест execute_command...")
result = tm.execute_tool("execute_command", command="echo Hello from MCP")
if "error" not in result:
    print(f"  [OK] Команда выполнена")
    print(f"  Вывод: {result.get('stdout', '').strip()}")
else:
    print(f"  [ERROR] {result['error']}")
print()

print("=" * 70)
print("ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
print("=" * 70)

