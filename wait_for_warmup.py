"""
Ожидание завершения разогрева модели
"""

import requests
import time

print("=" * 70)
print("ОЖИДАНИЕ ЗАВЕРШЕНИЯ РАЗОГРЕВА МОДЕЛИ")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"

print("Модель разогревается (warming up)...")
print("Ожидаем завершения разогрева...")
print()

# Ждем пока API начнет отвечать
max_wait = 300  # 5 минут
check_interval = 10  # Проверяем каждые 10 секунд
attempts = max_wait // check_interval

for i in range(attempts):
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        
        if response.status_code == 200:
            print(f"[SUCCESS] API готов! (попытка {i+1}/{attempts})")
            data = response.json()
            models = data.get('data', [])
            if models:
                print(f"Найдено моделей: {len(models)}")
                for m in models:
                    print(f"  - {m.get('id', 'Unknown')}")
            print()
            print("=" * 70)
            print("МОДЕЛЬ ГОТОВА! Теперь можно отправлять запросы.")
            print("=" * 70)
            break
        elif response.status_code == 502:
            elapsed = (i + 1) * check_interval
            remaining = max_wait - elapsed
            print(f"[{i+1}/{attempts}] Ожидание... (прошло {elapsed}с, осталось ~{remaining}с)")
    except:
        elapsed = (i + 1) * check_interval
        print(f"[{i+1}/{attempts}] Ожидание... (прошло {elapsed}с)")
    
    if i < attempts - 1:
        time.sleep(check_interval)

print()

# После ожидания пробуем запрос
if response.status_code == 200:
    print("Отправка тестового запроса...")
    from agent import CodeAgent
    
    try:
        agent = CodeAgent()
        prompt = "Расскажи про воздушные шарики на русском."
        
        print(f"Запрос: {prompt}")
        print()
        print("Ответ:")
        print("-" * 70)
        
        response_text = ""
        for chunk in agent.ask(prompt, stream=True):
            response_text += chunk
            print(chunk, end='', flush=True)
            if len(response_text) > 1000:
                break
        
        print()
        print("-" * 70)
        
        if len(response_text) > 20:
            print()
            print("[SUCCESS] ВСЕ РАБОТАЕТ!")
        else:
            print()
            print("[WARNING] Ответ неполный")
    except Exception as e:
        print(f"[ERROR] {e}")
else:
    print("[WARNING] API все еще не готов после ожидания")
    print()
    print("ПОМОЩЬ НУЖНА:")
    print("1. В LM Studio проверьте Developer Logs")
    print("2. Убедитесь, что 'warming up' завершился")
    print("3. Проверьте статус модели - должно быть 'READY'")
    print("4. Попробуйте отправить сообщение в Chat")

print()

