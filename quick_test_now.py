"""Быстрый тест агента"""
import sys
from agent import CodeAgent

print("=" * 70)
print("БЫСТРЫЙ ТЕСТ АГЕНТА")
print("=" * 70)
print()

print("Инициализация агента...")
try:
    agent = CodeAgent()
    print(f"[OK] Агент инициализирован")
    print(f"Провайдер: {agent.provider}")
    print(f"Модель: {agent.model_name}")
    print()
except Exception as e:
    print(f"[ERROR] Ошибка инициализации: {e}")
    sys.exit(1)

print("Отправка тестового запроса: 'Сколько будет 2+2? Ответь только числом.'")
print("-" * 70)
print()

try:
    response_text = ""
    chunk_count = 0
    
    for chunk in agent.ask("Сколько будет 2+2? Ответь только числом."):
        response_text += chunk
        sys.stdout.write(chunk)
        sys.stdout.flush()
        chunk_count += 1
        
        # Ограничиваем вывод для теста
        if chunk_count > 100:
            break
    
    print()
    print()
    print("=" * 70)
    
    if response_text.strip():
        print("[SUCCESS] Агент ответил!")
        print(f"Ответ: {response_text[:200]}")
    else:
        print("[WARNING] Пустой ответ")
        print("Возможно, API не настроен в LM Studio")
        print("Проверьте: Settings -> Local Server API -> Enable")
        
except Exception as e:
    print()
    print("=" * 70)
    print(f"[ERROR] Ошибка: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)

