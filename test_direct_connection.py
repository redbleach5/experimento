"""Прямое подключение к LM Studio с разными вариантами"""
import requests
import json
import time

print("=" * 70)
print("ПРЯМОЕ ПОДКЛЮЧЕНИЕ К LM STUDIO")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Вариант 1: Простой запрос с минимальными параметрами
print("[1] Тест 1: Минимальный запрос")
print("-" * 70)
payload1 = {
    "model": model_name,
    "messages": [{"role": "user", "content": "2+2"}],
    "max_tokens": 10
}

try:
    r = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload1,
        timeout=60
    )
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        print("УСПЕХ!")
        print(r.json())
    else:
        print(f"Ответ: {r.text[:200]}")
except Exception as e:
    print(f"Ошибка: {e}")
print()

# Вариант 2: Без stream
print("[2] Тест 2: С явным stream=False")
print("-" * 70)
payload2 = {
    "model": model_name,
    "messages": [{"role": "user", "content": "Сколько будет 2+2? Ответь только числом."}],
    "max_tokens": 20,
    "stream": False,
    "temperature": 0.1
}

try:
    r = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload2,
        timeout=120,
        headers={"Content-Type": "application/json"}
    )
    print(f"Статус: {r.status_code}")
    if r.status_code == 200:
        result = r.json()
        if 'choices' in result:
            answer = result['choices'][0]['message']['content']
            print(f"ОТВЕТ: {answer}")
        else:
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    else:
        print(f"Ответ: {r.text[:200]}")
except Exception as e:
    print(f"Ошибка: {e}")
print()

# Вариант 3: Проверка health endpoint
print("[3] Тест 3: Health check")
print("-" * 70)
for endpoint in ["/health", "/", "/v1/models", "/v1/chat/completions"]:
    try:
        r = requests.get(f"{base_url}{endpoint}", timeout=5)
        print(f"{endpoint}: {r.status_code}")
    except Exception as e:
        print(f"{endpoint}: {type(e).__name__}")
print()

print("=" * 70)
print("ЕСЛИ ВСЕ ВОЗВРАЩАЕТ 502:")
print("=" * 70)
print("1. В LM Studio: Settings -> Local Server")
print("2. Убедитесь что 'Start Server' активен")
print("3. Проверьте что модель загружена для API (не только для Chat)")
print("4. Попробуйте перезапустить Local Server")
print()

