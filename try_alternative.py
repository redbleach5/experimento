"""
Попытка альтернативных способов подключения
"""

import requests
import json
import time

print("=" * 70)
print("ПОПЫТКА АЛЬТЕРНАТИВНЫХ СПОСОБОВ")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Вариант 1: Использовать /v1/responses вместо /v1/chat/completions
print("[1] Попытка через /v1/responses...")
try:
    payload = {
        "model": model_name,
        "prompt": "Расскажи про воздушные шарики на русском",
        "max_tokens": 200
    }
    response = requests.post(
        f"{base_url}/v1/responses",
        json=payload,
        timeout=120
    )
    print(f"    Статус: {response.status_code}")
    if response.status_code == 200:
        print("    [SUCCESS] Работает через /v1/responses!")
        result = response.json()
        print(f"    Ответ: {result}")
    else:
        print(f"    Ответ: {response.text[:200]}")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Вариант 2: Упрощенный запрос без stream
print("[2] Упрощенный запрос без stream...")
try:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Привет"}],
        "max_tokens": 10,
        "stream": False
    }
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=180
    )
    print(f"    Статус: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"    [SUCCESS] Работает! Ответ: {content}")
    else:
        print(f"    [ERROR] {response.status_code}: {response.text[:200]}")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Вариант 3: Проверка, может быть модель нужно "разбудить"
print("[3] Попытка 'разбудить' модель простым запросом...")
try:
    # Сначала очень простой запрос
    simple_payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5
    }
    
    for i in range(3):
        print(f"    Попытка {i+1}/3...")
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=simple_payload,
            timeout=60
        )
        print(f"      Статус: {response.status_code}")
        
        if response.status_code == 200:
            print("    [SUCCESS] Модель ответила!")
            result = response.json()
            print(f"      Ответ: {result['choices'][0]['message']['content']}")
            
            # Теперь основной запрос
            print()
            print("    Отправка основного запроса про воздушные шарики...")
            main_payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Расскажи интересные факты про воздушные шарики на русском языке"}],
                "max_tokens": 300,
                "stream": False
            }
            
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                json=main_payload,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print()
                print("=" * 70)
                print("ОТВЕТ МОДЕЛИ ПРО ВОЗДУШНЫЕ ШАРИКИ:")
                print("=" * 70)
                print(content)
                print("=" * 70)
                print("[SUCCESS] ВСЕ РАБОТАЕТ!")
                break
            else:
                print(f"      [ERROR] {response.status_code}")
        elif response.status_code == 502:
            print(f"      [502] Модель еще не готова, ждем 10 секунд...")
            time.sleep(10)
        else:
            print(f"      [ERROR] {response.status_code}")
            
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)

