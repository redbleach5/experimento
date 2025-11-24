"""
Тест подключения и общения с моделью
"""

import requests
import json
import sys

print("=" * 70)
print("ТЕСТ ПОДКЛЮЧЕНИЯ К LM STUDIO")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Шаг 1: Проверка доступности моделей
print("[1] Проверка доступности моделей...")
try:
    response = requests.get(f"{base_url}/v1/models", timeout=10)
    print(f"    Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        models = data.get('data', [])
        print(f"    [OK] Найдено моделей: {len(models)}")
        if models:
            for m in models:
                print(f"      - {m.get('id', 'Unknown')}")
            # Используем первую доступную модель
            if models[0].get('id'):
                model_name = models[0].get('id')
                print(f"    [*] Используем модель: {model_name}")
    else:
        print(f"    [ERROR] Код {response.status_code}")
        print(f"    Ответ: {response.text[:200]}")
except Exception as e:
    print(f"    [ERROR] {e}")
    sys.exit(1)

print()

# Шаг 2: Отправка запроса про воздушные шарики
print("[2] Отправка запроса про воздушные шарики...")
print()

prompt = "Расскажи мне интересные факты про воздушные шарики. Ответь на русском языке."

payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 500,
    "temperature": 0.7,
    "stream": False
}

try:
    print(f"    Запрос: {prompt}")
    print()
    print("    Ожидание ответа...")
    
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=120,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"    Статус код: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            print("=" * 70)
            print("ОТВЕТ МОДЕЛИ:")
            print("=" * 70)
            print()
            print(content)
            print()
            print("=" * 70)
            print("[SUCCESS] ПОДКЛЮЧЕНИЕ РАБОТАЕТ!")
            print("=" * 70)
        else:
            print(f"    [ERROR] Неожиданный формат: {result}")
    elif response.status_code == 502:
        print("    [ERROR] 502 Bad Gateway")
        print("    Сервер не может обработать запрос")
        print("    Возможно, модель еще инициализируется")
    else:
        print(f"    [ERROR] Код {response.status_code}")
        print(f"    Ответ: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("    [ERROR] Таймаут запроса")
    print("    Модель слишком медленная или не отвечает")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

