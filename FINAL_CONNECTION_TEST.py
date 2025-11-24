"""Финальный тест подключения с детальными инструкциями"""
import requests
import time
import sys

print("=" * 70)
print("ФИНАЛЬНЫЙ ТЕСТ ПОДКЛЮЧЕНИЯ К LM STUDIO")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Шаг 1: Проверка базового подключения
print("[ШАГ 1] Проверка подключения к серверу...")
try:
    r = requests.get(f"{base_url}/v1/models", timeout=10)
    print(f"    Статус: {r.status_code}")
    
    if r.status_code == 200:
        print("    [OK] API работает!")
        models = r.json().get('data', [])
        print(f"    Найдено моделей: {len(models)}")
        sys.exit(0)
    elif r.status_code == 502:
        print("    [502] Сервер отвечает, но модель не готова")
    else:
        print(f"    [ERROR] Неожиданный статус: {r.status_code}")
except requests.exceptions.ConnectionError:
    print("    [ERROR] Не удалось подключиться к серверу")
    print()
    print("=" * 70)
    print("РЕШЕНИЕ:")
    print("=" * 70)
    print("1. В LM Studio откройте: Settings -> Local Server")
    print("2. Нажмите 'Start Server'")
    print("3. Дождитесь сообщения 'Server running'")
    print("4. Запустите этот скрипт снова")
    sys.exit(1)
except Exception as e:
    print(f"    [ERROR] {e}")

print()
print("[ШАГ 2] Попытка подключения с ожиданием...")
print("    (Ждем 30 секунд - проверяем каждые 5 секунд)")
print()

# Ждем и пробуем несколько раз
for i in range(6):
    try:
        r = requests.get(f"{base_url}/v1/models", timeout=5)
        if r.status_code == 200:
            print(f"    [OK] API готов! (попытка {i+1})")
            models = r.json().get('data', [])
            print(f"    Найдено моделей: {len(models)}")
            break
        elif r.status_code == 502:
            if i < 5:
                print(f"    [{i+1}/6] Ожидание... (502)")
                time.sleep(5)
            else:
                print(f"    [FAIL] После 30 секунд все еще 502")
        else:
            print(f"    Статус: {r.status_code}")
    except:
        if i < 5:
            time.sleep(5)
        pass

print()
print("[ШАГ 3] Тест запроса к модели...")
print()

try:
    r = requests.get(f"{base_url}/v1/models", timeout=5)
    if r.status_code != 200:
        print("=" * 70)
        print("ПРОБЛЕМА: API все еще возвращает 502")
        print("=" * 70)
        print()
        print("ЧТО НУЖНО СДЕЛАТЬ В LM STUDIO:")
        print()
        print("1. Откройте Settings -> Local Server")
        print("2. Убедитесь что:")
        print("   - Кнопка 'Start Server' нажата")
        print("   - Статус показывает 'Server running'")
        print("   - Порт указан (обычно 1234)")
        print()
        print("3. ОТКЛЮЧИТЕ следующие настройки:")
        print("   - 'Load model on demand' (Загрузка модели по требованию)")
        print("   - 'Automatic unloading of unused models' (Автоматическая разгрузка)")
        print()
        print("4. Перезапустите Local Server:")
        print("   - Нажмите 'Stop Server'")
        print("   - Подождите 5 секунд")
        print("   - Нажмите 'Start Server'")
        print("   - Дождитесь статуса 'READY' для модели")
        print()
        print("5. Проверьте статус модели:")
        print("   - В разделе Local Server модель должна быть 'READY'")
        print("   - В Chat модель должна отвечать (это уже работает)")
        print()
        print("6. После настройки запустите этот скрипт снова:")
        print("   python FINAL_CONNECTION_TEST.py")
        print()
        sys.exit(1)
    
    # Если API работает - тестируем запрос
    print("Отправка запроса: 'Сколько будет 2+2? Ответь только числом.'")
    print("Ожидание ответа...")
    print()
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Сколько будет 2+2? Ответь только числом."}],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=180
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            answer = result['choices'][0]['message']['content']
            print()
            print("=" * 70)
            print("УСПЕХ! МОДЕЛЬ ОТВЕТИЛА:")
            print("=" * 70)
            print(answer)
            print("=" * 70)
            print()
            print("[OK] Подключение работает! Агент может использовать модель.")
        else:
            print(f"Неожиданный формат ответа: {result}")
    else:
        print(f"[ERROR] Статус {response.status_code}")
        print(f"Ответ: {response.text[:200]}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

