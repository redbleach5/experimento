"""Проверка Local Server LM Studio"""
import requests
import sys

print("=" * 70)
print("ПРОВЕРКА LOCAL SERVER LM STUDIO")
print("=" * 70)
print()

# Проверяем разные порты
ports_to_check = [1234, 11434, 8080, 8000, 5000]

for port in ports_to_check:
    url = f"http://127.0.0.1:{port}/v1/models"
    try:
        response = requests.get(url, timeout=3)
        print(f"Порт {port}:")
        print(f"  Статус: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                models = data.get('data', [])
                print(f"  [OK] API работает! Найдено моделей: {len(models)}")
                if models:
                    print(f"  Модели: {[m.get('id', m.get('model', 'unknown')) for m in models[:3]]}")
            except:
                print(f"  [OK] API отвечает, но формат не JSON")
        elif response.status_code == 502:
            print(f"  [502] Сервер отвечает, но модель не готова")
        else:
            print(f"  [ERROR] Код {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Порт {port}: [НЕТ ПОДКЛЮЧЕНИЯ]")
    except Exception as e:
        print(f"Порт {port}: [ОШИБКА] {e}")
    print()

print("=" * 70)
print("РЕКОМЕНДАЦИИ:")
print("=" * 70)
print()
print("1. В LM Studio откройте: Settings -> Local Server")
print("2. Убедитесь, что 'Start Server' нажат (Server running)")
print("3. Проверьте порт - должен быть указан в настройках")
print("4. Если порт другой - обновите config.yaml")
print()

