"""
Автоматическое тестирование системы
"""

import requests
import json
import time
import yaml

print("=" * 60)
print("АВТОМАТИЧЕСКОЕ ТЕСТИРОВАНИЕ")
print("=" * 60)
print()

# Тест 1: Проверка сервера
print("[TEST 1] Проверка LM Studio сервера...")
base_url = "http://127.0.0.1:1234"

try:
    # Пробуем несколько раз с задержкой
    for attempt in range(3):
        try:
            response = requests.get(f"{base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                print(f"    [OK] Сервер доступен (попытка {attempt + 1})")
                models = response.json().get('data', [])
                if models:
                    print(f"    [OK] Найдено моделей: {len(models)}")
                    for i, model in enumerate(models[:3], 1):
                        model_id = model.get('id', 'Unknown')
                        print(f"        {i}. {model_id}")
                    test_model = models[0].get('id', '')
                    break
                else:
                    print("    [!] Модели не найдены")
                    test_model = None
                    break
            else:
                print(f"    [RETRY] Код {response.status_code}, попытка {attempt + 1}/3")
                if attempt < 2:
                    time.sleep(2)
        except requests.exceptions.ConnectionError:
            print(f"    [RETRY] Ошибка подключения, попытка {attempt + 1}/3")
            if attempt < 2:
                time.sleep(2)
    else:
        print("    [ERROR] Не удалось подключиться после 3 попыток")
        test_model = None
except Exception as e:
    print(f"    [ERROR] {e}")
    test_model = None

print()

# Тест 2: Проверка API
if test_model:
    print(f"[TEST 2] Тест API с моделью: {test_model}")
    print("    Отправка тестового запроса...")
    
    payload = {
        "model": test_model,
        "messages": [
            {"role": "user", "content": "Напиши функцию на Python для вычисления факториала. Ответь только кодом."}
        ],
        "max_tokens": 200,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"    Статус код: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"    [OK] Ответ получен ({len(content)} символов):")
                print("    " + "-" * 50)
                print("    " + content[:200].replace('\n', '\n    '))
                if len(content) > 200:
                    print("    ...")
                print("    " + "-" * 50)
                print()
                print("=" * 60)
                print("[SUCCESS] ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
                print("=" * 60)
                print()
                print("Система работает корректно!")
                print("Можно использовать GUI или CLI интерфейс.")
            else:
                print(f"    [ERROR] Неожиданный формат: {result}")
        else:
            print(f"    [ERROR] Ошибка сервера: {response.text[:200]}")
            print()
            print("Возможные причины:")
            print("1. Модель еще загружается - подождите 30-60 секунд")
            print("2. Сервер перегружен - попробуйте позже")
            print("3. Проблема с моделью - попробуйте другую модель")
            
    except requests.exceptions.Timeout:
        print("    [ERROR] Таймаут запроса (модель может быть слишком медленной)")
    except Exception as e:
        print(f"    [ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
else:
    print("[TEST 2] Пропущен - нет доступных моделей")

print()

# Тест 3: Проверка конфигурации
print("[TEST 3] Проверка конфигурации...")
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    provider = config.get('model', {}).get('provider', '')
    model_name = config.get('model', {}).get('model_name', '')
    
    print(f"    Провайдер: {provider}")
    print(f"    Модель в конфиге: {model_name}")
    
    if test_model and model_name != test_model:
        print(f"    [!] Рекомендуется обновить model_name на: {test_model}")
        print("    Обновляю конфигурацию...")
        config['model']['model_name'] = test_model
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        print("    [OK] Конфигурация обновлена")
    else:
        print("    [OK] Конфигурация корректна")
        
except Exception as e:
    print(f"    [ERROR] Ошибка: {e}")

print()
print("=" * 60)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 60)

