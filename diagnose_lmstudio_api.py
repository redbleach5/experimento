"""Диагностика LM Studio API - детальная проверка"""
import requests
import json
import sys

print("=" * 70)
print("ДИАГНОСТИКА LM STUDIO API")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"

# 1. Проверка базового подключения
print("[1] Проверка базового подключения...")
try:
    r = requests.get(f"{base_url}/", timeout=5)
    print(f"    Статус: {r.status_code}")
    print(f"    Заголовки: {dict(r.headers)}")
except Exception as e:
    print(f"    Ошибка: {e}")

# 2. Проверка /v1/models
print()
print("[2] Проверка /v1/models...")
try:
    r = requests.get(f"{base_url}/v1/models", timeout=10)
    print(f"    Статус: {r.status_code}")
    print(f"    Content-Type: {r.headers.get('Content-Type', 'N/A')}")
    print(f"    Content-Length: {r.headers.get('Content-Length', 'N/A')}")
    if r.text:
        print(f"    Тело ответа (первые 200 символов): {r.text[:200]}")
    else:
        print(f"    Тело ответа: ПУСТО")
except Exception as e:
    print(f"    Ошибка: {e}")

# 3. Проверка /health (если есть)
print()
print("[3] Проверка /health...")
for endpoint in ["/health", "/status", "/api/health"]:
    try:
        r = requests.get(f"{base_url}{endpoint}", timeout=5)
        print(f"    {endpoint}: {r.status_code}")
        if r.text:
            print(f"    Ответ: {r.text[:100]}")
    except:
        pass

# 4. Проверка с разными заголовками
print()
print("[4] Проверка с разными заголовками...")
headers_variants = [
    {"Content-Type": "application/json"},
    {"Content-Type": "application/json", "Accept": "application/json"},
    {"Content-Type": "application/json", "User-Agent": "LM-Studio"},
]

for i, headers in enumerate(headers_variants, 1):
    try:
        r = requests.get(f"{base_url}/v1/models", headers=headers, timeout=5)
        print(f"    Вариант {i}: {r.status_code}")
    except Exception as e:
        print(f"    Вариант {i}: {type(e).__name__}")

print()
print("=" * 70)
print("ЧТО ПРОВЕРИТЬ В LM STUDIO:")
print("=" * 70)
print()
print("1. Settings -> Local Server:")
print("   - Убедитесь что 'Start Server' нажат")
print("   - Проверьте порт (должен быть 1234)")
print("   - Отключите 'Load model on demand'")
print("   - Отключите 'Automatic unloading of unused models'")
print()
print("2. Проверьте статус модели:")
print("   - В Chat модель должна быть загружена")
print("   - В Local Server должна быть видна как 'READY'")
print()
print("3. Попробуйте перезапустить Local Server:")
print("   - Stop Server -> подождите 5 сек -> Start Server")
print()
print("4. Проверьте логи LM Studio:")
print("   - View -> Developer Logs")
print("   - Ищите ошибки или предупреждения")
print()

