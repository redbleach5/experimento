"""
Комплексная проверка LM Studio со всеми вариантами
"""

import requests
import json
import time

print("=" * 70)
print("КОМПЛЕКСНАЯ ПРОВЕРКА LM STUDIO")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Вариант 1: Проверка с очень большим таймаутом
print("[VARIANT 1] Проверка с таймаутом 60 секунд...")
try:
    response = requests.get(f"{base_url}/v1/models", timeout=60)
    print(f"    Статус: {response.status_code}")
    if response.status_code == 200:
        print("    [SUCCESS] API работает!")
        data = response.json()
        models = data.get('data', [])
        print(f"    Моделей: {len(models)}")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Вариант 2: Проверка разных endpoints
print("[VARIANT 2] Проверка разных endpoints...")
endpoints = [
    "/v1/models",
    "/",
    "/health",
    "/api/v1/models"
]

for endpoint in endpoints:
    try:
        resp = requests.get(f"{base_url}{endpoint}", timeout=10)
        if resp.status_code == 200:
            print(f"    [FOUND] {endpoint}: {resp.status_code}")
        elif resp.status_code != 502:
            print(f"    {endpoint}: {resp.status_code}")
    except:
        pass

print()

# Вариант 3: Прямой запрос с минимальными параметрами
print("[VARIANT 3] Минимальный запрос к модели...")
minimal_payload = {
    "model": model_name,
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 5
}

try:
    print(f"    Отправка запроса к {model_name}...")
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=minimal_payload,
        timeout=180,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"    Статус: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            content = result['choices'][0]['message']['content']
            print(f"    [SUCCESS] Ответ получен: {content}")
            print()
            print("=" * 70)
            print("[SUCCESS] ВЗАИМОДЕЙСТВИЕ РАБОТАЕТ!")
            print("=" * 70)
            print()
            print("Теперь попробуем запрос про воздушные шарики...")
            print()
            
            # Основной запрос
            main_payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": "Расскажи интересные факты про воздушные шарики на русском языке"}],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            print("Отправка основного запроса...")
            response2 = requests.post(
                f"{base_url}/v1/chat/completions",
                json=main_payload,
                timeout=300,
                headers={'Content-Type': 'application/json'}
            )
            
            if response2.status_code == 200:
                result2 = response2.json()
                content2 = result2['choices'][0]['message']['content']
                print()
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
        else:
            print(f"    [ERROR] Неожиданный формат: {result}")
    elif response.status_code == 502:
        print("    [502] Bad Gateway")
        print()
        print("    ДИАГНОСТИКА:")
        print("    Сервер отвечает, но не может обработать запрос.")
        print()
        print("    ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("    1. Модель не загружена для API (только для Chat)")
        print("    2. Включена 'Загрузка модели по требованию'")
        print("    3. Модель разгружена из памяти")
        print("    4. Модель еще инициализируется")
        print()
        print("    РЕШЕНИЕ:")
        print("    1. В LM Studio откройте Chat")
        print("    2. Отправьте любое сообщение модели")
        print("    3. Дождитесь ответа (это загрузит модель)")
        print("    4. После этого API должен работать")
        print()
        print("    ИЛИ:")
        print("    1. Settings → Local Server")
        print("    2. Отключите 'Загрузка модели по требованию'")
        print("    3. Перезапустите Local Server")
    else:
        print(f"    [ERROR] Код {response.status_code}")
        print(f"    Ответ: {response.text[:300]}")
        
except requests.exceptions.Timeout:
    print("    [TIMEOUT] Превышен таймаут")
except Exception as e:
    print(f"    [ERROR] {e}")

print()
print("=" * 70)

