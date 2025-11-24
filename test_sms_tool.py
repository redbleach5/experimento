"""Тест инструмента отправки SMS"""
from mcp_tools import MCPToolManager

print("=" * 70)
print("ТЕСТ ИНСТРУМЕНТА ОТПРАВКИ SMS")
print("=" * 70)
print()

tm = MCPToolManager()

# Тест send_sms
print("[1] Тест send_sms...")
print("Номер: +797734030123")
print("Сообщение: Привет! Это тест от AI агента.")

result = tm.execute_tool(
    "send_sms",
    phone="+797734030123",
    message="Привет! Это тест от AI агента."
)

print()
if "error" in result:
    print(f"[INFO] {result.get('error', 'Unknown error')}")
    if "note" in result:
        print(f"Примечание: {result['note']}")
    if "options" in result:
        print("Варианты настройки:")
        for opt in result["options"]:
            print(f"  {opt}")
else:
    print(f"[SUCCESS] SMS отправлено!")
    print(f"Сервис: {result.get('service', 'Unknown')}")
    print(f"Статус: {result.get('status', 'Unknown')}")

print()
print("=" * 70)

# Тест send_notification
print("[2] Тест send_notification...")
result = tm.execute_tool(
    "send_notification",
    title="AI Agent",
    message="Тестовое уведомление от агента",
    method="desktop"
)

if "error" not in result:
    print("[OK] Уведомление отправлено")
else:
    print(f"[INFO] {result.get('error')}")

print()
print("=" * 70)

