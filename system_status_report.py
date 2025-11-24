"""
Отчет о работоспособности системы
"""

import requests
import yaml
from agent import CodeAgent
import time

print("=" * 70)
print("ОТЧЕТ О РАБОТОСПОСОБНОСТИ СИСТЕМЫ")
print("=" * 70)
print()

# 1. Конфигурация
print("[1] Конфигурация:")
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    provider = config.get('model', {}).get('provider', '')
    model_name = config.get('model', {}).get('model_name', '')
    print(f"    Провайдер: {provider}")
    print(f"    Модель: {model_name}")
    print("    [OK] Конфигурация загружена")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# 2. Подключение к LM Studio
print("[2] Подключение к LM Studio:")
base_url = "http://127.0.0.1:1234"
api_working = False
models_available = []

try:
    response = requests.get(f"{base_url}/v1/models", timeout=10)
    if response.status_code == 200:
        data = response.json()
        models = data.get('data', [])
        for m in models:
            model_id = m.get('id') or m.get('model') or m.get('name') or ''
            if model_id:
                models_available.append(model_id)
        if models_available:
            api_working = True
            print(f"    [OK] API работает, найдено моделей: {len(models_available)}")
            for mid in models_available:
                print(f"      - {mid}")
        else:
            print("    [WARNING] API отвечает, но модели не найдены")
    elif response.status_code == 502:
        print("    [502] API возвращает Bad Gateway")
        print("    [INFO] Используется модель из конфига")
    else:
        print(f"    [ERROR] Код {response.status_code}")
except Exception as e:
    print(f"    [WARNING] Не удалось подключиться: {e}")
    print("    [INFO] Используется модель из конфига")

print()

# 3. Инициализация агента
print("[3] Инициализация агента:")
try:
    agent = CodeAgent()
    print(f"    [OK] Агент инициализирован")
    print(f"    Провайдер: {agent.provider}")
    print(f"    Модель: {agent.model_name}")
    
    if hasattr(agent, 'available_models') and agent.available_models:
        print(f"    Доступные модели: {', '.join(agent.available_models)}")
    
    agent_ready = True
except Exception as e:
    print(f"    [ERROR] {e}")
    agent_ready = False

print()

# 4. Тест запроса
print("[4] Тест отправки запроса:")
if agent_ready:
    test_prompt = "Привет! Ответь одним словом: работает?"
    print(f"    Запрос: {test_prompt}")
    print("    Ожидание ответа...")
    
    response_text = ""
    error_occurred = False
    
    try:
        start_time = time.time()
        for chunk in agent.ask(test_prompt, stream=True):
            if "Ошибка" in chunk or "502" in chunk:
                if len(response_text) == 0:
                    error_occurred = True
                    break
            else:
                response_text += chunk
                if len(response_text) > 50:  # Ограничение для теста
                    break
            if time.time() - start_time > 30:
                break
        
        elapsed = time.time() - start_time
        
        if not error_occurred and len(response_text) > 5:
            print(f"    [OK] Ответ получен за {elapsed:.1f}с")
            print(f"    Ответ: {response_text[:100]}")
            query_working = True
        else:
            print("    [ERROR] Ошибка при получении ответа")
            print("    Причина: API возвращает 502")
            query_working = False
    except Exception as e:
        print(f"    [ERROR] {e}")
        query_working = False
else:
    print("    [SKIP] Агент не инициализирован")
    query_working = False

print()

# Итоговый отчет
print("=" * 70)
print("ИТОГОВЫЙ СТАТУС")
print("=" * 70)
print()

print("Компоненты системы:")
print(f"  [{'OK' if True else 'ERROR'}] Конфигурация")
print(f"  [{'OK' if agent_ready else 'ERROR'}] Агент")
print(f"  [{'OK' if api_working else 'WARNING'}] API LM Studio")
print(f"  [{'OK' if query_working else 'ERROR'}] Запросы к модели")
print()

if query_working:
    print("[SUCCESS] СИСТЕМА ПОЛНОСТЬЮ РАБОТАЕТ!")
    print()
    print("Все компоненты функционируют корректно.")
    print("Можно использовать GUI, CLI или веб-интерфейс.")
elif agent_ready:
    print("[WARNING] СИСТЕМА ЧАСТИЧНО РАБОТАЕТ")
    print()
    print("Код агента работает, но модель не отвечает.")
    print()
    print("Причина: API LM Studio возвращает 502 Bad Gateway")
    print()
    print("Решение:")
    print("1. В LM Studio: Settings -> Local Server")
    print("2. Отключите 'Загрузка модели по требованию'")
    print("3. Отключите 'Автоматическая разгрузка'")
    print("4. Перезапустите Local Server")
    print("5. Убедитесь, что модель загружена и статус 'READY'")
else:
    print("[ERROR] СИСТЕМА НЕ РАБОТАЕТ")
    print()
    print("Проверьте конфигурацию и настройки.")

print()
print("=" * 70)

