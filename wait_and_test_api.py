"""Ожидание готовности LM Studio API и тест подключения"""
import requests
import time
import sys

print("=" * 70)
print("ОЖИДАНИЕ ГОТОВНОСТИ LM STUDIO API")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Ждем пока API станет доступным
print("Ожидание готовности API...")
print("(Пока вы проверяете настройки в LM Studio)")
print()

max_wait = 300  # 5 минут
check_interval = 5  # проверяем каждые 5 секунд
start_time = time.time()

while time.time() - start_time < max_wait:
    try:
        # Проверяем /v1/models
        r = requests.get(f"{base_url}/v1/models", timeout=3)
        
        if r.status_code == 200:
            print("[OK] API готов!")
            try:
                models = r.json().get('data', [])
                print(f"Найдено моделей: {len(models)}")
                if models:
                    print(f"Модели: {[m.get('id', m.get('model', 'unknown')) for m in models[:3]]}")
            except:
                pass
            break
        elif r.status_code == 502:
            elapsed = int(time.time() - start_time)
            print(f"[{elapsed}с] Ожидание... (502 - модель еще не готова)")
        else:
            print(f"[{int(time.time() - start_time)}с] Статус: {r.status_code}")
            
    except requests.exceptions.ConnectionError:
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}с] Сервер не отвечает...")
    except Exception as e:
        print(f"Ошибка: {e}")
    
    time.sleep(check_interval)

# Если API готов - тестируем запрос
print()
print("=" * 70)
print("ТЕСТ ЗАПРОСА: 2+2")
print("=" * 70)
print()

try:
    r = requests.get(f"{base_url}/v1/models", timeout=5)
    if r.status_code != 200:
        print(f"[ERROR] API все еще не готов (статус {r.status_code})")
        print()
        print("ПРОВЕРЬТЕ В LM STUDIO:")
        print("1. Settings -> Local Server -> Start Server")
        print("2. Отключите 'Load model on demand'")
        print("3. Отключите 'Automatic unloading'")
        print("4. Перезапустите Local Server")
        sys.exit(1)
    
    print("Отправка запроса...")
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Сколько будет 2+2? Ответь только числом."}],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=120
    )
    
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result:
            answer = result['choices'][0]['message']['content']
            print()
            print("=" * 70)
            print("УСПЕХ! ОТВЕТ МОДЕЛИ:")
            print("=" * 70)
            print(answer)
            print("=" * 70)
        else:
            print(f"Неожиданный формат: {result}")
    else:
        print(f"[ERROR] Статус {response.status_code}")
        print(f"Ответ: {response.text[:200]}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

