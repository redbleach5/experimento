"""Тест агента с MCP инструментами"""
import sys
from agent import CodeAgent

print("=" * 70)
print("ТЕСТ АГЕНТА С MCP ИНСТРУМЕНТАМИ")
print("=" * 70)
print()

print("Инициализация агента...")
try:
    agent = CodeAgent()
    print(f"[OK] Агент инициализирован")
    print(f"Провайдер: {agent.provider}")
    print(f"Модель: {agent.model_name}")
    print(f"MCP включен: {agent.use_mcp}")
    
    if agent.use_mcp and agent.mcp_tools:
        tools = agent.mcp_tools.list_tools()
        print(f"MCP инструментов: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}")
    print()
except Exception as e:
    print(f"[ERROR] Ошибка инициализации: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("Тестовый запрос: 'Прочитай файл config.yaml и скажи какая модель используется'")
print("-" * 70)
print()

try:
    response_text = ""
    chunk_count = 0
    
    for chunk in agent.ask("Прочитай файл config.yaml и скажи какая модель используется"):
        response_text += chunk
        sys.stdout.write(chunk)
        sys.stdout.flush()
        chunk_count += 1
        
        # Ограничиваем для теста
        if chunk_count > 200:
            break
    
    print()
    print()
    print("=" * 70)
    
    if response_text.strip():
        print("[SUCCESS] Агент ответил!")
        if "TOOL_CALL" in response_text or "read_file" in response_text.lower():
            print("[INFO] Агент пытался использовать инструменты!")
    else:
        print("[WARNING] Пустой ответ")
        
except Exception as e:
    print()
    print("=" * 70)
    print(f"[ERROR] Ошибка: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)

