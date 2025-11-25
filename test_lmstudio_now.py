"""
Проверка взаимодействия с LM Studio прямо сейчас
"""

import requests
import json
import time
from agent import CodeAgent

print("=" * 70)
print("ПРОВЕРКА ВЗАИМОДЕЙСТВИЯ С LM STUDIO")
print("=" * 70)
print()

# Шаг 1: Проверка API
print("[1] Проверка доступности API...")
base_url = "http://127.0.0.1:1234"

try:
    response = requests.get(f"{base_url}/v1/models", timeout=10)
    print(f"    Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        models = data.get('data', [])
        print(f"    [OK] API работает!")
        print(f"    Найдено моделей: {len(models)}")
        
        if models:
            print("    Доступные модели:")
            for i, m in enumerate(models, 1):
                model_id = m.get('id') or m.get('model') or m.get('name') or 'Unknown'
                print(f"      {i}. {model_id}")
    elif response.status_code == 502:
        print("    [502] Bad Gateway - сервер не может обработать запрос")
    else:
        print(f"    [ERROR] Код {response.status_code}")
        print(f"    Ответ: {response.text[:200]}")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Шаг 2: Инициализация агента
print("[2] Инициализация агента...")
try:
    agent = CodeAgent()
    print(f"    [OK] Агент готов")
    print(f"    Модель: {agent.model_name}")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print()

# Шаг 3: Отправка запроса про воздушные шарики
print("[3] Отправка запроса про воздушные шарики...")
prompt = "Расскажи интересные факты про воздушные шарики. Ответь на русском языке развернуто."

print(f"    Запрос: {prompt}")
print()
print("    Ответ модели:")
print("    " + "=" * 66)

response_text = ""
chunk_count = 0
start_time = time.time()

try:
    for chunk in agent.ask(prompt, stream=True):
        # Пропускаем сообщения об ошибках только в начале
        if chunk_count == 0 and ("Ошибка" in chunk or "502" in chunk or "Error" in chunk):
            print(f"    {chunk}")
            print()
            print("    [WARNING] Обнаружена ошибка, но продолжаем...")
            continue
        
        response_text += chunk
        print(chunk, end='', flush=True)
        chunk_count += 1
        
        # Ограничение для теста
        if len(response_text) > 2000:
            print("\n    ... (ответ обрезан)")
            break
        
        # Таймаут
        if time.time() - start_time > 180:
            print("\n    ... (таймаут)")
            break
    
    elapsed = time.time() - start_time
    
    print()
    print("    " + "=" * 66)
    print()
    
    if len(response_text) > 20:
        print(f"    [SUCCESS] Ответ получен!")
        print(f"    Длина: {len(response_text)} символов")
        print(f"    Время: {elapsed:.1f} секунд")
        print(f"    Чанков: {chunk_count}")
        print()
        print("=" * 70)
        print("[SUCCESS] ВЗАИМОДЕЙСТВИЕ РАБОТАЕТ!")
        print("=" * 70)
    else:
        print("    [WARNING] Ответ слишком короткий")
        print("    Возможно, модель еще загружается")
        
except KeyboardInterrupt:
    print("\n    [INTERRUPTED] Прервано")
except Exception as e:
    print(f"\n    [ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

