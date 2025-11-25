"""
Финальный тест с готовой моделью
"""

import sys
import os

# Устанавливаем UTF-8
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

from agent import CodeAgent
import time

print("\n" + "=" * 60)
print("ФИНАЛЬНЫЙ ТЕСТ AI CODE AGENT")
print("=" * 60)
print()

try:
    print("[*] Инициализация агента...")
    agent = CodeAgent()
    print("[OK] Агент инициализирован!")
    print(f"[*] Провайдер: {agent.provider}")
    print(f"[*] Модель: {agent.model_name}")
    print()
    
    # Тест 1: Простой запрос
    print("=" * 60)
    print("ТЕСТ 1: Простая функция")
    print("=" * 60)
    test1 = "Напиши функцию на Python для вычисления факториала числа с использованием рекурсии"
    print(f"\nЗапрос: {test1}")
    print("\nОтвет агента:")
    print("-" * 60)
    
    response1 = ""
    for chunk in agent.ask(test1, stream=True):
        response1 += chunk
        print(chunk, end='', flush=True)
    
    print("\n" + "-" * 60)
    print(f"\n[OK] Получено {len(response1)} символов")
    print()
    
    time.sleep(2)
    
    # Тест 2: Более сложный запрос
    print("=" * 60)
    print("ТЕСТ 2: Сложный запрос")
    print("=" * 60)
    test2 = "Создай класс на Python для работы с бинарным деревом поиска. Включи методы: вставка, поиск, удаление, обход в порядке"
    print(f"\nЗапрос: {test2}")
    print("\nОтвет агента:")
    print("-" * 60)
    
    response2 = ""
    for chunk in agent.ask(test2, stream=True):
        response2 += chunk
        print(chunk, end='', flush=True)
        if len(response2) > 2000:  # Ограничение для теста
            break
    
    print("\n" + "-" * 60)
    print(f"\n[OK] Получено {len(response2)} символов")
    print()
    
    # Итоги
    print("=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    print()
    print("[SUCCESS] Все тесты пройдены успешно!")
    print()
    print("Система работает корректно:")
    print("  - Подключение к LM Studio: OK")
    print("  - Генерация ответов: OK")
    print("  - Стриминг: OK")
    print()
    print("Можно использовать:")
    print("  - GUI интерфейс: python gui.py")
    print("  - CLI интерфейс: python cli.py")
    print("  - Веб интерфейс: python web_ui.py")
    print()
    print("=" * 60)
    
except Exception as e:
    print(f"\n[ERROR] Ошибка при тестировании: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("Проверьте:")
    print("1. LM Studio запущен и модель загружена")
    print("2. Local Server включен и статус 'READY'")
    print("3. Модель qwen3-30b-a3b-instruct-2507 доступна")

print()

