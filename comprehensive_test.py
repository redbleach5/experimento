"""
Комплексное тестирование всех возможных вариантов
"""

import requests
import json
import time
import sys

print("=" * 70)
print("КОМПЛЕКСНОЕ ТЕСТИРОВАНИЕ LM STUDIO")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Тест 1: Базовое подключение с разными таймаутами
print("[TEST 1] Базовое подключение...")
for timeout in [5, 10, 30]:
    try:
        print(f"    Попытка с таймаутом {timeout}с...")
        response = requests.get(f"{base_url}/v1/models", timeout=timeout)
        print(f"    Статус: {response.status_code}")
        if response.status_code == 200:
            print("    [SUCCESS] Подключение работает!")
            data = response.json()
            models = data.get('data', [])
            if models:
                print(f"    Найдено моделей: {len(models)}")
                for m in models:
                    print(f"      - {m.get('id', 'Unknown')}")
            break
        elif response.status_code == 502:
            print(f"    [502] Bad Gateway (таймаут {timeout}с)")
        else:
            print(f"    [ERROR] Код {response.status_code}")
    except requests.exceptions.Timeout:
        print(f"    [TIMEOUT] Превышен таймаут {timeout}с")
    except Exception as e:
        print(f"    [ERROR] {type(e).__name__}: {e}")

print()

# Тест 2: Разные форматы запросов
print("[TEST 2] Тест разных форматов запросов...")

test_payloads = [
    # Минимальный запрос
    {
        "model": model_name,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5
    },
    # С дополнительными параметрами
    {
        "model": model_name,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5,
        "temperature": 0.7,
        "stream": False
    },
    # Без stream явно
    {
        "model": model_name,
        "messages": [{"role": "user", "content": "test"}],
        "max_tokens": 3
    }
]

for i, payload in enumerate(test_payloads, 1):
    try:
        print(f"    Вариант {i}...")
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        print(f"      Статус: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                content = result['choices'][0]['message']['content']
                print(f"      [SUCCESS] Ответ получен: {content[:50]}")
                print()
                print("=" * 70)
                print("[SUCCESS] API РАБОТАЕТ! Найден рабочий формат запроса!")
                print("=" * 70)
                break
        elif response.status_code == 502:
            print(f"      [502] Bad Gateway")
        else:
            print(f"      [ERROR] {response.status_code}: {response.text[:100]}")
    except requests.exceptions.Timeout:
        print(f"      [TIMEOUT] Превышен таймаут")
    except Exception as e:
        print(f"      [ERROR] {e}")

print()

# Тест 3: Проверка через agent
print("[TEST 3] Тест через агента...")
try:
    from agent import CodeAgent
    
    print("    Инициализация агента...")
    agent = CodeAgent()
    print(f"    [OK] Агент инициализирован")
    print(f"    Провайдер: {agent.provider}")
    print(f"    Модель: {agent.model_name}")
    print()
    
    print("    Отправка тестового запроса...")
    test_prompt = "Напиши функцию factorial на Python"
    
    response_text = ""
    chunk_count = 0
    error_occurred = False
    
    try:
        for chunk in agent.ask(test_prompt, stream=True):
            response_text += chunk
            chunk_count += 1
            if chunk_count <= 5:  # Показываем первые 5 чанков
                print(chunk, end='', flush=True)
            if chunk_count == 5:
                print("...")
            
            if "Ошибка" in chunk or "502" in chunk:
                error_occurred = True
                break
            
            if len(response_text) > 500:  # Ограничение для теста
                break
        
        if not error_occurred and len(response_text) > 10:
            print()
            print("    [SUCCESS] Агент работает! Получен ответ.")
            print(f"    Длина ответа: {len(response_text)} символов")
            print()
            print("=" * 70)
            print("[SUCCESS] ВСЕ РАБОТАЕТ!")
            print("=" * 70)
        else:
            print()
            print("    [ERROR] Ошибка при получении ответа")
            
    except Exception as e:
        print(f"    [ERROR] Ошибка: {e}")
        
except ImportError:
    print("    [ERROR] Не удалось импортировать агента")
except Exception as e:
    print(f"    [ERROR] {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
print("=" * 70)

