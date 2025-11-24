"""Прямой тест агента с максимальными таймаутами"""
import sys
import time
from agent import CodeAgent

print("=" * 70)
print("ПРЯМОЙ ТЕСТ АГЕНТА - РЕШЕНИЕ 2+2")
print("=" * 70)
print()

print("Инициализация агента...")
try:
    agent = CodeAgent()
    print("[OK] Агент инициализирован")
    print(f"Провайдер: {agent.provider}")
    print(f"Модель: {agent.model_name}")
    print()
except Exception as e:
    print(f"[ERROR] Ошибка инициализации: {e}")
    sys.exit(1)

print("Отправка запроса: 'Реши 2+2 используя калькулятор. Ответь только числом.'")
print("Ожидание ответа (это может занять время для модели 30B)...")
print("-" * 70)
print()

start_time = time.time()

try:
    response_text = ""
    for chunk in agent.ask("Реши 2+2 используя калькулятор. Ответь только числом."):
        response_text += chunk
        sys.stdout.write(chunk)
        sys.stdout.flush()
    
    elapsed = time.time() - start_time
    
    print()
    print()
    print("=" * 70)
    print(f"ВРЕМЯ ОТВЕТА: {elapsed:.1f} секунд")
    print("=" * 70)
    
    if response_text.strip():
        print("[SUCCESS] Агент ответил!")
    else:
        print("[WARNING] Пустой ответ")
        
except Exception as e:
    elapsed = time.time() - start_time
    print()
    print()
    print("=" * 70)
    print(f"[ERROR] Ошибка после {elapsed:.1f} секунд: {e}")
    print("=" * 70)
    import traceback
    traceback.print_exc()

print()

