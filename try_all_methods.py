"""Пробуем все возможные способы подключения к LM Studio"""
import requests
import json
import time

print("=" * 70)
print("ПОПЫТКА ВСЕХ МЕТОДОВ ПОДКЛЮЧЕНИЯ")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Метод 1: Простейший запрос без лишних параметров
print("[1] Метод 1: Минимальный запрос")
print("-" * 70)
try:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "2+2"}]
    }
    r = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=180)
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        print("УСПЕХ!")
        print(r.json())
    else:
        print(f"Ответ: {r.text[:200]}")
except Exception as e:
    print(f"Ошибка: {e}")
print()

# Метод 2: С явным указанием stream=False
print("[2] Метод 2: С stream=False")
print("-" * 70)
try:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Сколько будет 2+2? Ответь только числом."}],
        "stream": False,
        "max_tokens": 10
    }
    r = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=180)
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        if 'choices' in result:
            print(f"ОТВЕТ: {result['choices'][0]['message']['content']}")
        else:
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"Ответ: {r.text[:200]}")
except Exception as e:
    print(f"Ошибка: {e}")
print()

# Метод 3: Streaming запрос
print("[3] Метод 3: Streaming запрос")
print("-" * 70)
try:
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "2+2"}],
        "stream": True
    }
    r = requests.post(f"{base_url}/v1/chat/completions", json=payload, stream=True, timeout=180)
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        print("Получение ответа...")
        full_response = ""
        for line in r.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data_str = line_str[6:]
                    if data_str == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            content = delta.get('content', '')
                            if content:
                                full_response += content
                                print(content, end='', flush=True)
                    except:
                        pass
        print()
        print(f"\nПолный ответ: {full_response}")
    else:
        print(f"Ответ: {r.text[:200]}")
except Exception as e:
    print(f"Ошибка: {e}")
print()

# Метод 4: Проверка доступных моделей через API
print("[4] Метод 4: Проверка списка моделей")
print("-" * 70)
try:
    r = requests.get(f"{base_url}/v1/models", timeout=30)
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        models = r.json().get('data', [])
        print(f"Найдено моделей: {len(models)}")
        for m in models:
            print(f"  - {m.get('id', m.get('model', 'unknown'))}")
    else:
        print(f"Ответ: {r.text[:200]}")
except Exception as e:
    print(f"Ошибка: {e}")
print()

# Метод 5: Попробуем без указания модели (пусть API сам выберет)
print("[5] Метод 5: Без указания модели")
print("-" * 70)
try:
    payload = {
        "messages": [{"role": "user", "content": "2+2"}]
    }
    r = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=180)
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        print("УСПЕХ!")
        print(r.json())
    else:
        print(f"Ответ: {r.text[:200]}")
except Exception as e:
    print(f"Ошибка: {e}")
print()

print("=" * 70)
print("РЕЗУЛЬТАТ:")
print("=" * 70)
print("Если все методы возвращают 502, значит:")
print("1. Local Server не настроен правильно")
print("2. Модель не загружена для API (только для Chat)")
print("3. Нужно проверить настройки в LM Studio")
print()

