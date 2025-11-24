"""
Полная проверка работоспособности системы
"""

import requests
import json
import time
import sys
import yaml
from agent import CodeAgent

print("=" * 70)
print("ПОЛНАЯ ПРОВЕРКА РАБОТОСПОСОБНОСТИ СИСТЕМЫ")
print("=" * 70)
print()

# Тест 1: Проверка конфигурации
print("[TEST 1] Проверка конфигурации...")
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    provider = config.get('model', {}).get('provider', '')
    model_name = config.get('model', {}).get('model_name', '')
    
    print(f"    Провайдер: {provider}")
    print(f"    Модель: {model_name}")
    
    if provider == 'lmstudio' and model_name:
        print("    [OK] Конфигурация корректна")
    else:
        print("    [ERROR] Неправильная конфигурация")
        sys.exit(1)
except Exception as e:
    print(f"    [ERROR] Ошибка чтения конфига: {e}")
    sys.exit(1)

print()

# Тест 2: Проверка подключения к LM Studio
print("[TEST 2] Проверка подключения к LM Studio...")
base_url = "http://127.0.0.1:1234"
models_found = []

for attempt in range(3):
    try:
        timeout = 5 + (attempt * 5)
        print(f"    Попытка {attempt + 1}/3 (таймаут {timeout}с)...")
        
        response = requests.get(f"{base_url}/v1/models", timeout=timeout)
        print(f"    Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            
            for m in models:
                model_id = m.get('id') or m.get('model') or m.get('name') or ''
                if model_id and model_id not in models_found:
                    models_found.append(model_id)
            
            if models_found:
                print(f"    [OK] Найдено моделей: {len(models_found)}")
                for i, mid in enumerate(models_found, 1):
                    print(f"      {i}. {mid}")
                break
            else:
                print("    [WARNING] Модели не найдены в ответе")
        elif response.status_code == 502:
            print(f"    [502] Bad Gateway")
            if attempt < 2:
                wait = (attempt + 1) * 3
                print(f"    Ждем {wait}с и пробуем снова...")
                time.sleep(wait)
                continue
        else:
            print(f"    [ERROR] Код {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"    [TIMEOUT] Превышен таймаут")
        if attempt < 2:
            continue
    except Exception as e:
        print(f"    [ERROR] {e}")
        if attempt < 2:
            time.sleep(2)
            continue

if not models_found:
    print("    [WARNING] Не удалось загрузить модели через API")
    print(f"    [INFO] Будет использована модель из конфига: {model_name}")

print()

# Тест 3: Инициализация агента
print("[TEST 3] Инициализация агента...")
try:
    agent = CodeAgent()
    print(f"    [OK] Агент инициализирован")
    print(f"    Провайдер: {agent.provider}")
    print(f"    Модель: {agent.model_name}")
    
    # Проверяем доступные модели
    if hasattr(agent, 'available_models') and agent.available_models:
        print(f"    Доступные модели: {', '.join(agent.available_models)}")
    
except Exception as e:
    print(f"    [ERROR] Ошибка инициализации: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Тест 4: Отправка тестового запроса
print("[TEST 4] Отправка тестового запроса...")
test_prompt = "Расскажи интересные факты про воздушные шарики. Ответь кратко на русском языке."

print(f"    Запрос: {test_prompt}")
print()
print("    Ответ модели:")
print("    " + "-" * 66)

response_text = ""
chunk_count = 0
error_occurred = False
start_time = time.time()

try:
    for chunk in agent.ask(test_prompt, stream=True):
        if "Ошибка" in chunk or "502" in chunk or "Error" in chunk:
            if chunk_count == 0:
                error_occurred = True
                print(f"    {chunk}")
                break
        else:
            response_text += chunk
            print(chunk, end='', flush=True)
            chunk_count += 1
            
            # Ограничение для теста
            if len(response_text) > 1000:
                print("\n    ... (ответ обрезан для теста)")
                break
            
            # Таймаут для теста
            if time.time() - start_time > 120:
                print("\n    ... (таймаут теста)")
                break
    
    elapsed_time = time.time() - start_time
    
    print()
    print("    " + "-" * 66)
    print()
    
    if not error_occurred and len(response_text) > 10:
        print(f"    [SUCCESS] Ответ получен!")
        print(f"    Длина ответа: {len(response_text)} символов")
        print(f"    Время ответа: {elapsed_time:.1f} секунд")
        print(f"    Получено чанков: {chunk_count}")
    elif error_occurred:
        print(f"    [ERROR] Произошла ошибка при получении ответа")
        print(f"    Возможные причины:")
        print(f"    1. Модель еще не готова (502)")
        print(f"    2. Сервер перегружен")
        print(f"    3. Проблема с конфигурацией LM Studio")
    else:
        print(f"    [WARNING] Ответ слишком короткий или пустой")
        
except KeyboardInterrupt:
    print("\n    [INTERRUPTED] Тест прерван пользователем")
except Exception as e:
    print(f"\n    [ERROR] Ошибка: {e}")
    import traceback
    traceback.print_exc()

print()

# Итоговый результат
print("=" * 70)
print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
print("=" * 70)
print()

if not error_occurred and len(response_text) > 10:
    print("[SUCCESS] СИСТЕМА РАБОТАЕТ!")
    print()
    print("Все компоненты функционируют:")
    print("  ✅ Конфигурация загружена")
    print("  ✅ Агент инициализирован")
    print("  ✅ Модель отвечает на запросы")
    print()
    print("Система готова к использованию!")
else:
    print("[WARNING] ЕСТЬ ПРОБЛЕМЫ")
    print()
    print("Статус компонентов:")
    print("  ✅ Конфигурация загружена")
    print("  ✅ Агент инициализирован")
    if error_occurred:
        print("  ❌ Модель не отвечает (ошибка 502)")
        print()
        print("Рекомендации:")
        print("  1. Проверьте настройки LM Studio:")
        print("     - Settings → Local Server → отключите 'Загрузка модели по требованию'")
        print("     - Перезапустите Local Server")
        print("  2. Убедитесь, что модель загружена в LM Studio")
        print("  3. Попробуйте отправить сообщение в Chat в LM Studio")
    else:
        print("  ⚠️  Модель отвечает, но ответ неполный")

print()
print("=" * 70)

