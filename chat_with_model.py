"""
Общение с моделью через агента
"""

import time
import sys
from agent import CodeAgent

print("=" * 70)
print("ОБЩЕНИЕ С МОДЕЛЬЮ ПРО ВОЗДУШНЫЕ ШАРИКИ")
print("=" * 70)
print()

try:
    print("[*] Инициализация агента...")
    agent = CodeAgent()
    print(f"[OK] Агент готов!")
    print(f"    Провайдер: {agent.provider}")
    print(f"    Модель: {agent.model_name}")
    print()
    
    # Даем время модели на разогрев
    print("[*] Ожидание готовности модели (10 секунд)...")
    for i in range(10, 0, -1):
        print(f"    {i}...", end=' ', flush=True)
        time.sleep(1)
    print()
    print()
    
    # Запрос про воздушные шарики
    prompt = "Расскажи мне интересные факты про воздушные шарики. Ответь на русском языке развернуто и интересно."
    
    print("=" * 70)
    print("ЗАПРОС К МОДЕЛИ:")
    print("=" * 70)
    print(prompt)
    print()
    print("=" * 70)
    print("ОТВЕТ МОДЕЛИ:")
    print("=" * 70)
    print()
    
    response_text = ""
    chunk_count = 0
    error_occurred = False
    
    try:
        for chunk in agent.ask(prompt, stream=True):
            if "Ошибка" in chunk or "502" in chunk or "Error" in chunk:
                if chunk_count == 0:  # Только если это первый чанк
                    error_occurred = True
                    print(chunk)
                    break
            else:
                response_text += chunk
                print(chunk, end='', flush=True)
                chunk_count += 1
        
        print()
        print()
        print("=" * 70)
        
        if not error_occurred and len(response_text) > 10:
            print("[SUCCESS] ОТВЕТ ПОЛУЧЕН!")
            print(f"Длина ответа: {len(response_text)} символов")
            print("=" * 70)
        elif error_occurred:
            print("[ERROR] Произошла ошибка при получении ответа")
            print()
            print("Возможные причины:")
            print("1. Модель еще разогревается (warming up)")
            print("2. Сервер перегружен")
            print("3. Недостаточно ресурсов")
            print()
            print("Попробуйте:")
            print("- Подождать еще 30-60 секунд")
            print("- Проверить статус в LM Studio")
            print("- Перезапустить Local Server")
            print("=" * 70)
        else:
            print("[WARNING] Ответ слишком короткий или пустой")
            print("=" * 70)
            
    except KeyboardInterrupt:
        print("\n\n[!] Прервано пользователем")
    except Exception as e:
        print(f"\n\n[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"[ERROR] Ошибка инициализации: {e}")
    import traceback
    traceback.print_exc()

print()

