"""
Проверка подключения к LM Studio и тест запроса
"""

import requests
import json
import time
from agent import CodeAgent

print("=" * 70)
print("ПРОВЕРКА ПОДКЛЮЧЕНИЯ И ТЕСТ ЗАПРОСА")
print("=" * 70)
print()

# Проверка API
print("[1] Проверка API LM Studio...")
base_url = "http://127.0.0.1:1234"

try:
    response = requests.get(f"{base_url}/v1/models", timeout=15)
    print(f"    Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        models = data.get('data', [])
        print(f"    [OK] API работает! Найдено моделей: {len(models)}")
        if models:
            for m in models:
                model_id = m.get('id') or m.get('model') or m.get('name') or ''
                print(f"      - {model_id}")
    else:
        print(f"    [WARNING] Код {response.status_code}")
except Exception as e:
    print(f"    [WARNING] {e}")

print()

# Инициализация агента
print("[2] Инициализация агента...")
try:
    agent = CodeAgent()
    print(f"    [OK] Агент готов")
    print(f"    Модель: {agent.model_name}")
except Exception as e:
    print(f"    [ERROR] {e}")
    exit(1)

print()

# Тест запроса
print("[3] Тест запроса про воздушные шарики...")
prompt = "Расскажи интересные факты про воздушные шарики. Ответь кратко на русском."

print(f"    Запрос: {prompt}")
print()
print("    Ответ:")

response_text = ""
start_time = time.time()

try:
    for chunk in agent.ask(prompt, stream=True):
        if len(response_text) == 0 and ("Ошибка" in chunk or "502" in chunk):
            print(f"    [WARNING] {chunk}")
            continue
        
        response_text += chunk
        print(chunk, end='', flush=True)
        
        if len(response_text) > 1000:
            print("\n    ... (обрезано)")
            break
        
        if time.time() - start_time > 180:
            print("\n    ... (таймаут)")
            break
    
    print()
    print()
    
    if len(response_text) > 20:
        print(f"    [SUCCESS] Ответ получен! ({len(response_text)} символов)")
        print()
        print("=" * 70)
        print("[SUCCESS] ВСЕ РАБОТАЕТ!")
        print("=" * 70)
    else:
        print("    [ERROR] Ответ не получен")
        
except Exception as e:
    print(f"\n    [ERROR] {e}")

print()

