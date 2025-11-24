"""
Прямой запрос с максимальными таймаутами и детальной диагностикой
"""

import requests
import json
import time

print("=" * 70)
print("ПРЯМОЙ ЗАПРОС С МАКСИМАЛЬНЫМИ ТАЙМАУТАМИ")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"
model_name = "qwen3-30b-a3b-instruct-2507"

# Сначала ждем пока API станет доступен
print("[1] Ожидание готовности API...")
for i in range(20):
    try:
        resp = requests.get(f"{base_url}/v1/models", timeout=5)
        if resp.status_code == 200:
            print(f"    [OK] API готов! (попытка {i+1})")
            break
        elif resp.status_code == 502:
            if i < 19:
                print(f"    [{i+1}/20] Ожидание...")
                time.sleep(10)
            else:
                print("    [WARNING] API все еще возвращает 502")
                print("    Продолжаем с запросом - возможно модель готова")
    except:
        if i < 19:
            time.sleep(10)

print()

# Отправляем запрос с очень длинным таймаутом
print("[2] Отправка запроса про воздушные шарики...")
print("    (Таймаут: 10 минут для большой модели)")
print()

prompt = "Расскажи интересные факты про воздушные шарики. Ответь на русском языке."

payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": prompt}
    ],
    "max_tokens": 500,
    "temperature": 0.7,
    "stream": False
}

print(f"Модель: {model_name}")
print(f"Запрос: {prompt}")
print()
print("Ожидание ответа (это может занять несколько минут для модели 30B)...")
print()

start_time = time.time()

try:
    response = requests.post(
        f"{base_url}/v1/chat/completions",
        json=payload,
        timeout=600,  # 10 минут
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    
    elapsed = time.time() - start_time
    
    print(f"Статус код: {response.status_code}")
    print(f"Время ожидания: {elapsed:.1f} секунд")
    print()
    
    if response.status_code == 200:
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            
            print("=" * 70)
            print("ОТВЕТ МОДЕЛИ ПРО ВОЗДУШНЫЕ ШАРИКИ:")
            print("=" * 70)
            print()
            print(content)
            print()
            print("=" * 70)
            print("[SUCCESS] ВСЕ РАБОТАЕТ!")
            print(f"Время ответа: {elapsed:.1f} секунд")
            print("=" * 70)
        else:
            print(f"[ERROR] Неожиданный формат ответа")
            print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    elif response.status_code == 502:
        print("[502] Bad Gateway")
        print()
        print("Модель все еще не готова обрабатывать запросы.")
        print()
        print("ПОМОЩЬ НУЖНА:")
        print("1. В LM Studio проверьте Developer Logs")
        print("2. Убедитесь, что 'warming up' завершился")
        print("3. Проверьте, что статус модели 'READY'")
        print("4. Попробуйте отправить сообщение в Chat в LM Studio")
        print("   (это загрузит модель в память для API)")
    else:
        print(f"[ERROR] Код {response.status_code}")
        print(f"Ответ: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("[TIMEOUT] Превышен таймаут 10 минут")
    print("Модель слишком медленная или не отвечает")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

