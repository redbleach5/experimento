"""
Простой тест для проверки работы агента
"""

import sys
import os

# Устанавливаем UTF-8 для вывода
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

from agent import CodeAgent

print("\n" + "=" * 60)
print("ПРОСТОЙ ТЕСТ AI CODE AGENT")
print("=" * 60)
print()

try:
    print("[*] Инициализация агента...")
    agent = CodeAgent()
    print("[OK] Агент готов!")
    print()
    
    # Простой тест
    test_prompt = "Напиши функцию на Python для вычисления факториала числа"
    print(f"[*] Запрос: {test_prompt}")
    print()
    print("[*] Ответ агента:")
    print("-" * 60)
    
    full_response = ""
    for chunk in agent.ask(test_prompt, stream=True):
        full_response += chunk
        print(chunk, end='', flush=True)
    
    print()
    print("-" * 60)
    print()
    print(f"[OK] Получен ответ длиной {len(full_response)} символов")
    print()
    print("=" * 60)
    print("ТЕСТ ПРОЙДЕН УСПЕШНО!")
    print("=" * 60)
    print()
    print("Теперь можно использовать GUI для полноценной работы.")
    print("GUI должен быть уже открыт.")
    
except Exception as e:
    print(f"\n[ERROR] Ошибка: {e}")
    print()
    print("Возможные решения:")
    print("1. Убедитесь, что LM Studio запущен")
    print("2. Проверьте, что Local Server включен")
    print("3. Убедитесь, что модель загружена и статус 'READY'")
    print("4. Попробуйте перезапустить Local Server в LM Studio")
    import traceback
    traceback.print_exc()

print()
input("Нажмите Enter для выхода...")

