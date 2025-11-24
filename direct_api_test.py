"""
Прямой тест API LM Studio
"""

import requests
import json
import time

print("=" * 60)
print("ПРЯМОЙ ТЕСТ API LM STUDIO")
print("=" * 60)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Тест 1: Проверка моделей
print("[TEST 1] Проверка доступности моделей...")
try:
    response = requests.get(f"{base_url}/v1/models", timeout=10)
    print(f"    Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        models = data.get('data', [])
        print(f"    [OK] Найдено моделей: {len(models)}")
        if models:
            print(f"    Первая модель: {models[0].get('id', 'Unknown')}")
            model_name = models[0].get('id', model_name)
    else:
        print(f"    [ERROR] Ответ: {response.text[:200]}")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Тест 2: Простой запрос без стриминга
print("[TEST 2] Тест простого запроса (без стриминга)...")
payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": "Привет! Ответь одним словом: работает?"}
    ],
    "max_tokens": 10,
    "temperature": 0.7,
    "stream": False
}

try:
    print(f"    Отправка запроса к модели: {model_name}")
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=120,  # Увеличенный таймаут для большой модели
        headers={"Content-Type": "application/json"}
    )
    
    print(f"    Статус код: {response.status_code}")
    print(f"    Заголовки ответа: {dict(list(response.headers.items())[:3])}")
    
    if response.status_code == 200:
        result = response.json()
        print("    [OK] Запрос успешен!")
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            print(f"    Ответ модели: {content}")
            print()
            print("=" * 60)
            print("[SUCCESS] API РАБОТАЕТ!")
            print("=" * 60)
        else:
            print(f"    [WARNING] Неожиданный формат: {result}")
    elif response.status_code == 502:
        print("    [ERROR] 502 Bad Gateway")
        print("    Возможные причины:")
        print("    1. Модель еще инициализируется")
        print("    2. Недостаточно памяти")
        print("    3. Сервер перегружен")
        print()
        print("    Попробуйте:")
        print("    1. Проверить статус в LM Studio - должно быть 'READY'")
        print("    2. Отправить тестовое сообщение прямо в LM Studio Chat")
        print("    3. Перезапустить Local Server")
    else:
        print(f"    [ERROR] Код {response.status_code}")
        print(f"    Ответ: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("    [ERROR] Таймаут запроса (модель слишком медленная или не отвечает)")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

# Тест 3: Проверка через другой endpoint
print("[TEST 3] Проверка альтернативных endpoints...")
endpoints = ["/", "/health", "/v1/health"]

for endpoint in endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", timeout=5)
        print(f"    {endpoint}: {resp.status_code}")
    except:
        print(f"    {endpoint}: недоступен")

print()
print("=" * 60)
print("РЕКОМЕНДАЦИИ:")
print("=" * 60)
print()
print("Если все еще 502:")
print("1. В LM Studio отправьте тестовое сообщение в Chat")
print("2. Если работает в Chat, но не через API - проблема в сервере")
print("3. Попробуйте перезапустить Local Server")
print("4. Проверьте логи в LM Studio (Developer Logs)")
print()

