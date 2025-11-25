"""
Продвинутая диагностика с детальной проверкой
"""

import requests
import json
import socket
import time

print("=" * 70)
print("ПРОДВИНУТАЯ ДИАГНОСТИКА LM STUDIO")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"

# Проверка 1: Порт и соединение
print("[1] Проверка сетевого соединения...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(('127.0.0.1', 1234))
    sock.close()
    
    if result == 0:
        print("    [OK] Порт 1234 открыт и доступен")
    else:
        print(f"    [ERROR] Порт 1234 недоступен (код: {result})")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Проверка 2: HTTP заголовки
print("[2] Проверка HTTP заголовков...")
try:
    response = requests.get(f"{base_url}/v1/models", timeout=10)
    print(f"    Статус: {response.status_code}")
    print(f"    Заголовки ответа:")
    for key, value in list(response.headers.items())[:5]:
        print(f"      {key}: {value}")
    
    if response.status_code == 502:
        print()
        print("    [DIAGNOSIS] 502 Bad Gateway означает:")
        print("      - Сервер запущен и отвечает")
        print("      - Но не может обработать запрос")
        print("      - Возможно, модель еще не готова или не загружена")
        
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Проверка 3: Разные методы запросов
print("[3] Тест разных методов HTTP...")
methods = ['GET', 'POST', 'OPTIONS']

for method in methods:
    try:
        if method == 'GET':
            resp = requests.get(f"{base_url}/v1/models", timeout=5)
        elif method == 'POST':
            resp = requests.post(f"{base_url}/v1/models", timeout=5)
        elif method == 'OPTIONS':
            resp = requests.options(f"{base_url}/v1/models", timeout=5)
        
        print(f"    {method}: {resp.status_code}")
    except:
        print(f"    {method}: ошибка")

print()

# Проверка 4: Прямой запрос с детальным выводом
print("[4] Детальный тест запроса...")
model_name = "qwen3-30b-a3b-instruct-2507"

payload = {
    "model": model_name,
    "messages": [{"role": "user", "content": "Hi"}],
    "max_tokens": 5,
    "stream": False
}

print(f"    URL: {base_url}/v1/chat/completions")
print(f"    Модель: {model_name}")
print(f"    Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
print()

try:
    print("    Отправка запроса...")
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=120,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AI-Code-Agent/1.0'
        }
    )
    
    print(f"    Статус код: {response.status_code}")
    print(f"    Заголовки ответа:")
    for key, value in list(response.headers.items())[:3]:
        print(f"      {key}: {value}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"    [SUCCESS] Ответ получен!")
        print(f"    Ответ: {result['choices'][0]['message']['content']}")
    elif response.status_code == 502:
        print(f"    [502] Bad Gateway")
        print(f"    Размер ответа: {len(response.content)} байт")
        if response.content:
            print(f"    Содержимое: {response.content[:200]}")
        print()
        print("    ВОЗМОЖНЫЕ ПРИЧИНЫ:")
        print("    1. Модель еще разогревается (warming up)")
        print("    2. Модель не загружена для API")
        print("    3. Проблема с конфигурацией сервера")
        print("    4. Недостаточно памяти/ресурсов")
    else:
        print(f"    [ERROR] Код {response.status_code}")
        print(f"    Ответ: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("    [TIMEOUT] Превышен таймаут")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

# Рекомендации
print("=" * 70)
print("РЕКОМЕНДАЦИИ ДЛЯ ПРОДВИНУТОГО ПОЛЬЗОВАТЕЛЯ:")
print("=" * 70)
print()
print("1. Проверьте в LM Studio:")
print("   - Developer Logs - должно быть 'warming up' завершено")
print("   - Статус модели должен быть 'READY' (не 'Loading')")
print("   - Local Server должен показывать 'Server running'")
print()
print("2. Проверьте настройки сервера:")
print("   - Settings → Local Server")
print("   - 'Загрузка модели по требованию' - должно быть ВЫКЛЮЧЕНО")
print("   - 'Автоматическая разгрузка' - должно быть ВЫКЛЮЧЕНО")
print()
print("3. Проверьте ресурсы:")
print("   - nvidia-smi (если используете GPU)")
print("   - Диспетчер задач (использование RAM)")
print()
print("4. Попробуйте перезапустить:")
print("   - Stop Server → подождите 10 сек → Start Server")
print("   - Подождите 1-2 минуты после запуска")
print()
print("=" * 70)

