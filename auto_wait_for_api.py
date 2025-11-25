"""Автоматическое ожидание готовности API и тест"""
import requests
import time
import sys

print("=" * 70)
print("АВТОМАТИЧЕСКОЕ ОЖИДАНИЕ ГОТОВНОСТИ LM STUDIO API")
print("=" * 70)
print()
print("Этот скрипт будет ждать, пока API станет доступным.")
print("Пока он работает, настройте LM Studio:")
print()
print("1. Settings -> Local Server -> Start Server")
print("2. Отключите 'Load model on demand'")
print("3. Отключите 'Automatic unloading'")
print("4. Перезапустите Local Server")
print()
print("Скрипт будет проверять каждые 5 секунд...")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"
max_wait_minutes = 10
check_interval = 5

start_time = time.time()
max_wait_seconds = max_wait_minutes * 60
attempt = 0

while time.time() - start_time < max_wait_seconds:
    attempt += 1
    elapsed = int(time.time() - start_time)
    
    try:
        r = requests.get(f"{base_url}/v1/models", timeout=5)
        
        if r.status_code == 200:
            print()
            print("=" * 70)
            print("[OK] API ГОТОВ!")
            print("=" * 70)
            print()
            
            models = r.json().get('data', [])
            print(f"Найдено моделей: {len(models)}")
            if models:
                for m in models[:3]:
                    print(f"  - {m.get('id', m.get('model', 'unknown'))}")
            print()
            
            # Тестируем запрос
            print("Тестируем запрос: 'Сколько будет 2+2? Ответь только числом.'")
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
                    print("[OK] Все работает! Агент может использовать модель.")
                    sys.exit(0)
                else:
                    print(f"Неожиданный формат: {result}")
            else:
                print(f"[ERROR] Запрос вернул {response.status_code}")
                print(f"Ответ: {response.text[:200]}")
            
            break
            
        elif r.status_code == 502:
            if attempt % 6 == 0:  # Каждые 30 секунд
                print(f"[{elapsed}с] Все еще ожидание... (502 - проверьте настройки в LM Studio)")
        else:
            print(f"[{elapsed}с] Статус: {r.status_code}")
            
    except requests.exceptions.ConnectionError:
        if attempt % 6 == 0:
            print(f"[{elapsed}с] Сервер не отвечает... (проверьте что Local Server запущен)")
    except Exception as e:
        if attempt % 6 == 0:
            print(f"[{elapsed}с] Ошибка: {e}")
    
    time.sleep(check_interval)

print()
print("=" * 70)
print("ВРЕМЯ ОЖИДАНИЯ ИСТЕКЛО")
print("=" * 70)
print()
print("API не стал доступным за {max_wait_minutes} минут.")
print()
print("ПРОВЕРЬТЕ:")
print("1. Local Server запущен в LM Studio?")
print("2. Настройки отключены ('Load model on demand', 'Automatic unloading')?")
print("3. Модель имеет статус 'READY' в Local Server?")
print()
print("Запустите скрипт снова после настройки.")
print()

