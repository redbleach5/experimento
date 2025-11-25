"""
Быстрый тест агента с LM Studio
"""

from agent import CodeAgent

print("=" * 60)
print("Быстрый тест AI Code Agent с LM Studio")
print("=" * 60)
print()

try:
    print("[*] Инициализация агента...")
    agent = CodeAgent()
    print("[OK] Агент инициализирован!")
    print()
    
    # Простой тест
    test_prompt = "Напиши функцию на Python для вычисления факториала"
    print(f"[*] Тестовый запрос: {test_prompt}")
    print()
    print("[*] Генерация ответа...")
    print("-" * 60)
    
    response = ""
    chunk_count = 0
    for chunk in agent.ask(test_prompt, stream=True):
        response += chunk
        print(chunk, end='', flush=True)
        chunk_count += 1
        if chunk_count > 100:  # Ограничение для теста
            break
    
    print()
    print("-" * 60)
    print()
    print(f"[OK] Получено {len(response)} символов ответа")
    print()
    print("=" * 60)
    print("[SUCCESS] Тест пройден успешно!")
    print("=" * 60)
    print()
    print("Теперь можно использовать GUI: python gui.py")
    
except Exception as e:
    print(f"[ERROR] Ошибка: {e}")
    import traceback
    traceback.print_exc()
    print()
    print("Возможные причины:")
    print("1. LM Studio не запущен")
    print("2. Local Server не включен")
    print("3. Модель не загружена")
    print("4. Неправильное имя модели в config.yaml")

print()
input("Нажмите Enter для выхода...")

