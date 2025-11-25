"""
Финальный тест взаимодействия с улучшенными повторами
"""

import time
from agent import CodeAgent

print("=" * 70)
print("ФИНАЛЬНЫЙ ТЕСТ ВЗАИМОДЕЙСТВИЯ С МОДЕЛЬЮ")
print("=" * 70)
print()

try:
    print("[*] Инициализация агента...")
    agent = CodeAgent()
    print(f"[OK] Агент готов (модель: {agent.model_name})")
    print()
    
    # Даем время на инициализацию
    print("[*] Ожидание 5 секунд для стабилизации...")
    time.sleep(5)
    print()
    
    # Запрос про воздушные шарики
    prompt = "Расскажи интересные факты про воздушные шарики. Ответь на русском языке развернуто и интересно."
    
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
    start_time = time.time()
    error_in_response = False
    
    try:
        for chunk in agent.ask(prompt, stream=True):
            # Игнорируем сообщения об ошибках, если уже есть ответ
            if len(response_text) == 0 and ("Ошибка" in chunk or "502" in chunk):
                print(f"[WARNING] {chunk}")
                error_in_response = True
                # Продолжаем, может быть ответ все равно придет
                continue
            
            response_text += chunk
            print(chunk, end='', flush=True)
            chunk_count += 1
            
            # Ограничение для теста
            if len(response_text) > 3000:
                print("\n... (ответ обрезан для теста)")
                break
            
            # Таймаут
            if time.time() - start_time > 300:
                print("\n... (таймаут теста)")
                break
        
        elapsed = time.time() - start_time
        
        print()
        print()
        print("=" * 70)
        
        if len(response_text) > 20 and not error_in_response:
            print("[SUCCESS] ОТВЕТ ПОЛУЧЕН!")
            print(f"Длина ответа: {len(response_text)} символов")
            print(f"Время: {elapsed:.1f} секунд")
            print(f"Чанков: {chunk_count}")
            print("=" * 70)
            print()
            print("СИСТЕМА РАБОТАЕТ КОРРЕКТНО!")
        elif len(response_text) > 20:
            print("[PARTIAL] Частичный ответ получен")
            print(f"Длина: {len(response_text)} символов")
            print("Возможно, были ошибки, но ответ частично получен")
        else:
            print("[ERROR] Ответ не получен")
            print("Все попытки вернули ошибку 502")
            print()
            print("РЕКОМЕНДАЦИИ:")
            print("1. В LM Studio отправьте сообщение в Chat")
            print("2. Дождитесь ответа (это загрузит модель)")
            print("3. Попробуйте снова")
            
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Прервано")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f"[ERROR] Ошибка инициализации: {e}")
    import traceback
    traceback.print_exc()

print()

