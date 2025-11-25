"""
Ожидание завершения разогрева и общение с моделью
"""

import requests
import time
from agent import CodeAgent

print("=" * 70)
print("ОЖИДАНИЕ ЗАВЕРШЕНИЯ РАЗОГРЕВА И ОБЩЕНИЕ")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"

print("[*] Модель разогревается (warming up)...")
print("    Согласно логам, модель загружена и разогревается.")
print("    Ожидаем завершения разогрева...")
print()

# Ждем пока API начнет отвечать (разогрев может занять время)
print("[*] Проверка готовности API...")
api_ready = False

for i in range(30):  # До 5 минут (30 * 10 секунд)
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        
        if response.status_code == 200:
            print(f"    [OK] API готов! (попытка {i+1})")
            data = response.json()
            models = data.get('data', [])
            if models:
                model_id = models[0].get('id') or models[0].get('model') or models[0].get('name')
                print(f"    Модель: {model_id}")
            api_ready = True
            break
        elif response.status_code == 502:
            elapsed = (i + 1) * 10
            print(f"    [{i+1}/30] Ожидание... (прошло {elapsed}с)")
    except:
        elapsed = (i + 1) * 10
        print(f"    [{i+1}/30] Ожидание... (прошло {elapsed}с)")
    
    if i < 29:
        time.sleep(10)

print()

if not api_ready:
    print("[WARNING] API все еще не готов после ожидания")
    print("Попробуем отправить запрос напрямую - возможно модель готова")
    print()

# Инициализация агента
print("[*] Инициализация агента...")
try:
    agent = CodeAgent()
    print(f"[OK] Агент готов")
    print(f"Модель: {agent.model_name}")
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print()

# Запрос про воздушные шарики
print("=" * 70)
print("ОТПРАВКА ЗАПРОСА ПРО ВОЗДУШНЫЕ ШАРИКИ")
print("=" * 70)
print()

prompt = "Расскажи интересные факты про воздушные шарики. Ответь на русском языке развернуто и интересно."

print(f"Запрос: {prompt}")
print()
print("Ответ модели:")
print("=" * 70)
print()

response_text = ""
chunk_count = 0
start_time = time.time()
max_wait = 600  # 10 минут для большой модели

try:
    for chunk in agent.ask(prompt, stream=True):
        # Пропускаем только первые сообщения об ошибках
        if chunk_count == 0 and ("Ошибка" in chunk or "502" in chunk):
            print(f"[INFO] {chunk}")
            print("[INFO] Продолжаем ожидание...")
            continue
        
        response_text += chunk
        print(chunk, end='', flush=True)
        chunk_count += 1
        
        # Ограничение для теста
        if len(response_text) > 3000:
            print("\n... (ответ обрезан для теста)")
            break
        
        # Таймаут
        if time.time() - start_time > max_wait:
            print("\n... (таймаут)")
            break
    
    elapsed = time.time() - start_time
    
    print()
    print()
    print("=" * 70)
    
    if len(response_text) > 20:
        print("[SUCCESS] ОТВЕТ ПОЛУЧЕН!")
        print(f"Длина ответа: {len(response_text)} символов")
        print(f"Время ответа: {elapsed:.1f} секунд")
        print(f"Получено чанков: {chunk_count}")
        print("=" * 70)
        print()
        print("СИСТЕМА РАБОТАЕТ!")
    else:
        print("[ERROR] Ответ не получен")
        print("Все попытки вернули ошибку")
        print("=" * 70)
        
except KeyboardInterrupt:
    print("\n\n[INTERRUPTED] Прервано")
except Exception as e:
    print(f"\n\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

