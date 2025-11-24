"""Проверка статуса API с детальными инструкциями"""
import requests
import time

print("=" * 70)
print("ПРОВЕРКА СТАТУСА LM STUDIO API")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"

# Проверка
print("[ПРОВЕРКА] Тестирую API...")
print()

try:
    r = requests.get(f"{base_url}/v1/models", timeout=5)
    
    if r.status_code == 200:
        print("=" * 70)
        print("[✅ УСПЕХ] API РАБОТАЕТ!")
        print("=" * 70)
        print()
        models = r.json().get('data', [])
        print(f"Найдено моделей: {len(models)}")
        for m in models:
            print(f"  - {m.get('id', m.get('model', 'unknown'))}")
        print()
        print("Теперь можно использовать агента!")
        print("Запустите: python test_agent_direct.py")
        
    elif r.status_code == 502:
        print("=" * 70)
        print("[❌ ПРОБЛЕМА] API возвращает 502")
        print("=" * 70)
        print()
        print("ЧТО ЭТО ЗНАЧИТ:")
        print("  - Сервер запущен (порт отвечает)")
        print("  - Но не может обработать запросы")
        print()
        print("=" * 70)
        print("РЕШЕНИЕ:")
        print("=" * 70)
        print()
        print("1. Откройте LM Studio")
        print("2. Перейдите в: Settings → Local Server API")
        print("   (или просто Settings → Local Server)")
        print()
        print("3. ПРОВЕРЬТЕ что:")
        print("   ✅ 'Enable Local Server API' ВКЛЮЧЕН")
        print("   ✅ Или кнопка 'Start Server' нажата")
        print("   ✅ Должно быть написано 'Server running'")
        print("   ✅ Порт указан (1234)")
        print()
        print("4. ЕСЛИ ВЫКЛЮЧЕНО:")
        print("   - Включите 'Enable Local Server API'")
        print("   - Или нажмите 'Start Server'")
        print("   - Дождитесь статуса 'READY'")
        print()
        print("5. ПЕРЕЗАПУСТИТЕ:")
        print("   - Нажмите 'Stop Server'")
        print("   - Подождите 5 секунд")
        print("   - Нажмите 'Start Server'")
        print("   - Дождитесь загрузки модели")
        print()
        print("6. ПРОВЕРЬТЕ СТАТУС МОДЕЛИ:")
        print("   - В разделе Local Server модель должна быть 'READY'")
        print("   - Не 'Loading' и не 'Error'")
        print()
        print("7. ПОСЛЕ НАСТРОЙКИ:")
        print("   - Запустите этот скрипт снова: python check_api_status.py")
        print("   - Или: python FINAL_CONNECTION_TEST.py")
        print()
        
    else:
        print(f"[ERROR] Неожиданный статус: {r.status_code}")
        print(f"Ответ: {r.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("=" * 70)
    print("[❌ ОШИБКА] Не удалось подключиться к серверу")
    print("=" * 70)
    print()
    print("РЕШЕНИЕ:")
    print("1. Убедитесь что LM Studio запущен")
    print("2. Включите Local Server API в настройках")
    print("3. Перезапустите LM Studio")
    print()
    
except Exception as e:
    print(f"[ERROR] {e}")

print("=" * 70)

