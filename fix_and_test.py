"""
Исправление и тест - пробуем все возможные варианты
"""

import requests
import json
import time
from agent import CodeAgent

print("=" * 70)
print("ИСПРАВЛЕНИЕ И ТЕСТ")
print("=" * 70)
print()

# Шаг 1: Проверяем точное имя модели из API
print("[1] Получение точного имени модели...")
base_url = "http://127.0.0.1:1234"
exact_model_name = None

# Пробуем много раз с ожиданием
for attempt in range(10):
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=15)
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            if models:
                exact_model_name = models[0].get('id') or models[0].get('model') or models[0].get('name')
                print(f"    [OK] Найдена модель: {exact_model_name}")
                break
        elif response.status_code == 502:
            print(f"    [WAIT] Попытка {attempt + 1}/10, ждем 5 секунд...")
            time.sleep(5)
    except:
        time.sleep(5)

if not exact_model_name:
    exact_model_name = "qwen3-30b-a3b-instruct-2507"
    print(f"    [INFO] Используем модель из конфига: {exact_model_name}")

print()

# Шаг 2: Пробуем разные варианты имени модели
print("[2] Тест с разными вариантами имени модели...")
model_variants = [
    exact_model_name,
    "qwen3-30b-a3b-instruct-2507",
    "qwen3-30b-a3b-instruct",
    "qwen3-30b",
    "qwen3"
]

for model_var in model_variants:
    print(f"    Пробуем: {model_var}")
    try:
        payload = {
            "model": model_var,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5,
            "stream": False
        }
        
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            timeout=60,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"    [SUCCESS] Работает с моделью: {model_var}")
            print(f"    Ответ: {content}")
            print()
            
            # Обновляем конфиг с правильным именем
            import yaml
            with open('config.yaml', 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            config['model']['model_name'] = model_var
            with open('config.yaml', 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
            print(f"    [OK] Конфиг обновлен с моделью: {model_var}")
            print()
            
            # Теперь основной запрос
            print("=" * 70)
            print("ОТПРАВКА ЗАПРОСА ПРО ВОЗДУШНЫЕ ШАРИКИ")
            print("=" * 70)
            print()
            
            main_payload = {
                "model": model_var,
                "messages": [{"role": "user", "content": "Расскажи интересные факты про воздушные шарики. Ответь на русском языке."}],
                "max_tokens": 500,
                "temperature": 0.7,
                "stream": False
            }
            
            print("Ожидание ответа (может занять время для большой модели)...")
            response2 = requests.post(
                f"{base_url}/v1/chat/completions",
                json=main_payload,
                timeout=300,
                headers={'Content-Type': 'application/json'}
            )
            
            if response2.status_code == 200:
                result2 = response2.json()
                content2 = result2['choices'][0]['message']['content']
                
                print()
                print("=" * 70)
                print("ОТВЕТ МОДЕЛИ:")
                print("=" * 70)
                print()
                print(content2)
                print()
                print("=" * 70)
                print("[SUCCESS] ВСЕ РАБОТАЕТ!")
                print("=" * 70)
            else:
                print(f"    [ERROR] Код {response2.status_code}")
            
            break
        elif response.status_code != 502:
            print(f"    [ERROR] Код {response.status_code}")
            break
    except Exception as e:
        if "502" not in str(e):
            print(f"    [ERROR] {e}")
    
    if response.status_code == 502:
        print(f"    [502] Пробуем следующий вариант...")
        continue

print()

# Шаг 3: Если ничего не сработало, пробуем через агента
if response.status_code == 502:
    print("[3] Пробуем через агента с обновленным именем модели...")
    try:
        agent = CodeAgent()
        print(f"    Модель: {agent.model_name}")
        
        prompt = "Расскажи про воздушные шарики на русском."
        print(f"    Запрос: {prompt}")
        print()
        print("    Ответ:")
        
        response_text = ""
        for chunk in agent.ask(prompt, stream=True):
            if len(response_text) < 10 and ("Ошибка" in chunk or "502" in chunk):
                print(f"    [WARNING] {chunk}")
                continue
            response_text += chunk
            print(chunk, end='', flush=True)
            if len(response_text) > 500:
                break
        
        print()
        if len(response_text) > 20:
            print()
            print("[SUCCESS] Работает через агента!")
        else:
            print()
            print("[ERROR] Не работает")
    except Exception as e:
        print(f"    [ERROR] {e}")

print()
print("=" * 70)

