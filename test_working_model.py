"""
Тест с готовой моделью - пробуем все варианты
"""

import requests
import json
import time

print("=" * 70)
print("ТЕСТ С ГОТОВОЙ МОДЕЛЬЮ")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Вариант 1: Простейший запрос без stream
print("[VARIANT 1] Простейший запрос (без stream)...")
try:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Привет"}],
        "max_tokens": 10,
        "stream": False
    }
    
    print(f"    Отправка к модели: {model_name}")
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=300,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"    Статус: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"    [SUCCESS] Ответ: {content}")
        print()
        print("=" * 70)
        print("[SUCCESS] МОДЕЛЬ РАБОТАЕТ!")
        print("=" * 70)
        print()
        
        # Теперь основной запрос
        print("Отправка запроса про воздушные шарики...")
        print()
        
        main_payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "Расскажи интересные факты про воздушные шарики. Ответь на русском языке развернуто."}],
            "max_tokens": 500,
            "temperature": 0.7,
            "stream": False
        }
        
        response2 = requests.post(
            f"{base_url}/v1/chat/completions",
            json=main_payload,
            timeout=300,
            headers={'Content-Type': 'application/json'}
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            content2 = result2['choices'][0]['message']['content']
            
            print("=" * 70)
            print("ОТВЕТ МОДЕЛИ ПРО ВОЗДУШНЫЕ ШАРИКИ:")
            print("=" * 70)
            print()
            print(content2)
            print()
            print("=" * 70)
            print("[SUCCESS] ВСЕ РАБОТАЕТ!")
            print("=" * 70)
        else:
            print(f"    [ERROR] Код {response2.status_code}")
    elif response.status_code == 502:
        print("    [502] Bad Gateway")
        print("    Модель может быть еще не полностью готова")
        print("    Подождите еще 30-60 секунд после 'warming up'")
    else:
        print(f"    [ERROR] Код {response.status_code}")
        print(f"    Ответ: {response.text[:300]}")
        
except requests.exceptions.Timeout:
    print("    [TIMEOUT] Превышен таймаут")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

