"""
Финальный тест общения с моделью
"""

import time
from agent import CodeAgent

print("\n" + "=" * 70)
print("ОБЩЕНИЕ С МОДЕЛЬЮ ПРО ВОЗДУШНЫЕ ШАРИКИ")
print("=" * 70)
print()

try:
    print("[*] Инициализация агента...")
    agent = CodeAgent()
    print("[OK] Агент готов!")
    print()
    
    # Даем больше времени на разогрев
    print("[*] Ожидание готовности модели...")
    print("    (Модель может разогреваться)")
    time.sleep(5)
    print("[OK] Продолжаем...")
    print()
    
    # Запрос про воздушные шарики
    prompt = "Расскажи мне интересные факты про воздушные шарики. Ответь на русском языке."
    
    print("=" * 70)
    print("МОЙ ЗАПРОС:")
    print("=" * 70)
    print(prompt)
    print()
    print("=" * 70)
    print("ОТВЕТ МОДЕЛИ:")
    print("=" * 70)
    print()
    
    response_text = ""
    error_found = False
    
    try:
        for chunk in agent.ask(prompt, stream=True):
            # Проверяем на ошибки только в начале
            if len(response_text) < 50:
                if "502" in chunk or "Ошибка" in chunk or "Error" in chunk:
                    if not error_found:
                        error_found = True
                        print(f"\n[WARNING] Обнаружена ошибка: {chunk[:100]}")
                        print("\nПопробую еще раз через несколько секунд...\n")
                        time.sleep(5)
                        # Пробуем еще раз
                        response_text = ""
                        for retry_chunk in agent.ask(prompt, stream=True):
                            if "502" not in retry_chunk and "Ошибка" not in retry_chunk:
                                response_text += retry_chunk
                                print(retry_chunk, end='', flush=True)
                            if len(response_text) > 100:
                                break
                        break
            
            if not error_found or len(response_text) > 0:
                response_text += chunk
                print(chunk, end='', flush=True)
        
        print()
        print()
        print("=" * 70)
        
        if len(response_text) > 20:
            print("[SUCCESS] ОТВЕТ ПОЛУЧЕН!")
            print(f"Длина: {len(response_text)} символов")
            print("=" * 70)
            print()
            print("Отлично! Модель работает!")
        else:
            print("[WARNING] Ответ слишком короткий")
            print("Возможно, модель еще разогревается")
            print("=" * 70)
            
    except Exception as e:
        print(f"\n[ERROR] Ошибка: {e}")
        
except Exception as e:
    print(f"[ERROR] Ошибка инициализации: {e}")

print()

