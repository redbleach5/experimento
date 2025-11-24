"""
Прямой тест общения с моделью
"""

import requests
import json
import time

print("=" * 70)
print("ПРЯМОЕ ОБЩЕНИЕ С МОДЕЛЬЮ")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Сначала пробуем получить список моделей с большим таймаутом
print("[1] Получение списка моделей (таймаут 30с)...")
models_list = []

try:
    response = requests.get(f"{base_url}/v1/models", timeout=30)
    print(f"    Статус: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        models = data.get('data', [])
        for m in models:
            model_id = m.get('id') or m.get('model') or m.get('name') or ''
            if model_id:
                models_list.append(model_id)
        
        if models_list:
            print(f"    [OK] Найдено моделей: {len(models_list)}")
            model_name = models_list[0]
            print(f"    Используем: {model_name}")
        else:
            print(f"    [WARNING] Модели не найдены, используем из конфига: {model_name}")
    else:
        print(f"    [WARNING] Код {response.status_code}, используем модель из конфига")
except Exception as e:
    print(f"    [WARNING] {e}, используем модель из конфига")

print()

# Теперь пробуем отправить запрос
print("[2] Отправка запроса про воздушные шарики...")
prompt = "Расскажи интересные факты про воздушные шарики. Ответь на русском языке."

payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 500,
    "temperature": 0.7,
    "stream": False
}

print(f"    Модель: {model_name}")
print(f"    Запрос: {prompt}")
print()
print("    Ожидание ответа (может занять время)...")

try:
    # Увеличенный таймаут для большой модели
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=300,  # 5 минут
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    
    print(f"    Статус код: {response.status_code}")
    print()
    
    if response.status_code == 200:
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            
            print("=" * 70)
            print("ОТВЕТ МОДЕЛИ ПРО ВОЗДУШНЫЕ ШАРИКИ:")
            print("=" * 70)
            print()
            print(content)
            print()
            print("=" * 70)
            print("[SUCCESS] ВЗАИМОДЕЙСТВИЕ РАБОТАЕТ!")
            print("=" * 70)
        else:
            print(f"    [ERROR] Неожиданный формат ответа")
            print(f"    Ответ: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    elif response.status_code == 502:
        print("    [502] Bad Gateway")
        print()
        print("    Проблема: Сервер не может обработать запрос")
        print()
        print("    Возможные причины:")
        print("    1. Модель еще загружается или разогревается")
        print("    2. Включена 'Загрузка модели по требованию'")
        print("    3. Модель разгружена из памяти")
        print()
        print("    Решение:")
        print("    1. В LM Studio отправьте сообщение в Chat (это загрузит модель)")
        print("    2. Или отключите 'Загрузка модели по требованию' в настройках")
        print("    3. Подождите 1-2 минуты после загрузки модели")
    else:
        print(f"    [ERROR] Код {response.status_code}")
        print(f"    Ответ: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("    [TIMEOUT] Превышен таймаут 5 минут")
    print("    Модель слишком медленная или не отвечает")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

