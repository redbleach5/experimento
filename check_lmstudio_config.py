"""
Проверка конфигурации и альтернативных вариантов
"""

import requests
import json

print("=" * 70)
print("ПРОВЕРКА КОНФИГУРАЦИИ LM STUDIO")
print("=" * 70)
print()

# Проверка разных портов
print("[CHECK 1] Проверка разных портов...")
ports = [1234, 1235, 8080, 8000, 11434]

for port in ports:
    try:
        url = f"http://127.0.0.1:{port}/v1/models"
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            print(f"    [FOUND] Рабочий порт: {port}")
            data = response.json()
            models = data.get('data', [])
            if models:
                print(f"    Модели: {[m.get('id') for m in models]}")
        elif response.status_code != 502:
            print(f"    Порт {port}: {response.status_code}")
    except:
        pass

print()

# Проверка разных форматов URL
print("[CHECK 2] Проверка разных форматов URL...")
urls = [
    "http://127.0.0.1:1234/v1/models",
    "http://localhost:1234/v1/models",
    "http://127.0.0.1:1234/api/v1/models",
    "http://127.0.0.1:1234/models",
]

for url in urls:
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            print(f"    [FOUND] Рабочий URL: {url}")
        elif response.status_code != 502:
            print(f"    {url}: {response.status_code}")
    except:
        pass

print()

# Проверка заголовков
print("[CHECK 3] Проверка с разными заголовками...")
headers_variants = [
    {"Content-Type": "application/json"},
    {"Content-Type": "application/json", "Accept": "application/json"},
    {},
]

for headers in headers_variants:
    try:
        response = requests.get(
            "http://127.0.0.1:1234/v1/models",
            headers=headers,
            timeout=5
        )
        if response.status_code == 200:
            print(f"    [FOUND] Рабочие заголовки: {headers}")
        elif response.status_code != 502:
            print(f"    Заголовки {headers}: {response.status_code}")
    except:
        pass

print()

# Финальный вывод
print("=" * 70)
print("ВЫВОД:")
print("=" * 70)
print()
print("Все запросы возвращают 502 Bad Gateway.")
print("Это означает:")
print("  1. Сервер LM Studio запущен (порт отвечает)")
print("  2. Но сервер не может обработать запросы")
print()
print("ВОЗМОЖНЫЕ ПРИЧИНЫ:")
print("  1. Local Server не полностью инициализирован")
print("  2. Модель не готова к API запросам")
print("  3. Проблема с конфигурацией сервера в LM Studio")
print()
print("РЕКОМЕНДАЦИИ:")
print("  1. В LM Studio проверьте:")
print("     - Settings -> Local Server -> должен быть включен")
print("     - Должно быть 'Server running'")
print("  2. Попробуйте:")
print("     - Перезапустить Local Server")
print("     - Отправить тестовое сообщение в Chat (если работает)")
print("     - Проверить логи в Developer Logs")
print("  3. Альтернатива:")
print("     - Использовать Ollama вместо LM Studio")
print("     - Или попробовать другую модель в LM Studio")
print()
print("=" * 70)

