"""
Ожидание и тест с длительными таймаутами
"""

import requests
import time
from agent import CodeAgent

print("=" * 70)
print("ТЕСТ С ДЛИТЕЛЬНЫМ ОЖИДАНИЕМ")
print("=" * 70)
print()

# Шаг 1: Ждем и проверяем API
print("[1] Ожидание готовности API (60 секунд)...")
base_url = "http://127.0.0.1:1234"
api_ready = False

for i in range(12):  # 12 попыток по 5 секунд = 60 секунд
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        if response.status_code == 200:
            print(f"    [OK] API готов! (попытка {i+1})")
            api_ready = True
            break
        elif response.status_code == 502:
            print(f"    [502] Ожидание... ({i+1}/12)")
    except:
        print(f"    [WAIT] Ожидание... ({i+1}/12)")
    
    if i < 11:
        time.sleep(5)

print()

# Шаг 2: Инициализация агента
print("[2] Инициализация агента...")
try:
    agent = CodeAgent()
    print(f"    [OK] Агент готов")
    print(f"    Модель: {agent.model_name}")
except Exception as e:
    print(f"    [ERROR] {e}")
    exit(1)

print()

# Шаг 3: Тест запроса с очень длинным ожиданием
print("[3] Отправка запроса про воздушные шарики...")
print("    (Ожидание может занять до 5 минут для большой модели)")
print()

prompt = "Расскажи интересные факты про воздушные шарики. Ответь на русском языке."

print("=" * 70)
print("ЗАПРОС:")
print("=" * 70)
print(prompt)
print()
print("=" * 70)
print("ОТВЕТ:")
print("=" * 70)
print()

response_text = ""
start_time = time.time()
max_wait = 300  # 5 минут

try:
    for chunk in agent.ask(prompt, stream=True):
        # Пропускаем только первые сообщения об ошибках
        if len(response_text) < 10 and ("Ошибка" in chunk or "502" in chunk):
            print(f"[INFO] {chunk}")
            # Продолжаем ждать
            continue
        
        response_text += chunk
        print(chunk, end='', flush=True)
        
        # Ограничение для теста
        if len(response_text) > 2000:
            print("\n... (ответ обрезан)")
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
        print(f"Длина: {len(response_text)} символов")
        print(f"Время: {elapsed:.1f} секунд")
        print("=" * 70)
        print()
        print("СИСТЕМА РАБОТАЕТ!")
    else:
        print("[ERROR] Ответ не получен")
        print("Все попытки вернули ошибку")
        print("=" * 70)
        print()
        print("РЕКОМЕНДАЦИИ:")
        print("1. В LM Studio отправьте сообщение в Chat")
        print("2. Дождитесь ответа")
        print("3. Попробуйте снова")
        
except KeyboardInterrupt:
    print("\n\n[INTERRUPTED] Прервано")
except Exception as e:
    print(f"\n\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

