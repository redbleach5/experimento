"""
Глубокое тестирование LM Studio API
"""

import requests
import json
import time

print("=" * 60)
print("ГЛУБОКОЕ ТЕСТИРОВАНИЕ LM STUDIO")
print("=" * 60)
print()

base_url = "http://127.0.0.1:1234"

# Тест разных endpoints
endpoints = [
    ("GET", "/v1/models", None),
    ("GET", "/", None),
    ("GET", "/health", None),
]

print("[TEST] Проверка различных endpoints...")
for method, endpoint, data in endpoints:
    try:
        url = f"{base_url}{endpoint}"
        print(f"\n  {method} {endpoint}...")
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json=data, timeout=5)
        
        print(f"    Статус: {response.status_code}")
        print(f"    Заголовки: {dict(list(response.headers.items())[:3])}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"    [OK] Ответ получен")
                if endpoint == "/v1/models" and 'data' in result:
                    models = result['data']
                    print(f"    Найдено моделей: {len(models)}")
                    if models:
                        print(f"    Первая модель: {models[0].get('id', 'Unknown')}")
            except:
                print(f"    Текст ответа: {response.text[:100]}")
        elif response.status_code == 502:
            print(f"    [502] Bad Gateway - сервер не может обработать запрос")
        else:
            print(f"    Текст: {response.text[:100]}")
            
    except requests.exceptions.ConnectionError:
        print(f"    [ERROR] Не удалось подключиться")
    except Exception as e:
        print(f"    [ERROR] {e}")

print()
print("=" * 60)
print("РЕКОМЕНДАЦИИ:")
print("=" * 60)
print()
print("Если все endpoints возвращают 502:")
print("1. В LM Studio проверьте статус модели - должна быть 'READY'")
print("2. Попробуйте перезапустить Local Server")
print("3. Убедитесь, что модель полностью загружена в память")
print("4. Проверьте, что порт 1234 не занят другим процессом")
print()
print("Если /v1/models работает, но /v1/chat/completions не работает:")
print("1. Модель может быть слишком большой для вашей системы")
print("2. Попробуйте использовать меньшую модель")
print("3. Увеличьте таймаут в запросах")
print()

