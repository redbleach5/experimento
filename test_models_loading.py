"""
Тест загрузки всех моделей из LM Studio
"""

import requests
import json

print("=" * 70)
print("ТЕСТ ЗАГРУЗКИ ВСЕХ МОДЕЛЕЙ ИЗ LM STUDIO")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"

# Пробуем несколько раз
for attempt in range(3):
    try:
        timeout = 5 + (attempt * 5)
        print(f"[Попытка {attempt + 1}/3] Запрос с таймаутом {timeout}с...")
        
        response = requests.get(f"{base_url}/v1/models", timeout=timeout)
        print(f"    Статус код: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"    [OK] Ответ получен!")
            print()
            
            # Показываем полный ответ для отладки
            print("Полный ответ API:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print()
            
            models = data.get('data', [])
            print(f"Найдено моделей в 'data': {len(models)}")
            print()
            
            if models:
                print("=" * 70)
                print("ВСЕ НАЙДЕННЫЕ МОДЕЛИ:")
                print("=" * 70)
                
                all_model_ids = []
                for i, model in enumerate(models, 1):
                    # Пробуем все возможные поля
                    model_id = model.get('id') or model.get('model') or model.get('name') or 'Unknown'
                    all_model_ids.append(model_id)
                    
                    print(f"\n{i}. Модель:")
                    print(f"   ID: {model.get('id', 'N/A')}")
                    print(f"   Model: {model.get('model', 'N/A')}")
                    print(f"   Name: {model.get('name', 'N/A')}")
                    print(f"   Полный объект: {json.dumps(model, indent=4, ensure_ascii=False)}")
                
                print()
                print("=" * 70)
                print("ИСПОЛЬЗУЕМЫЕ ID МОДЕЛЕЙ:")
                print("=" * 70)
                for mid in all_model_ids:
                    print(f"  - {mid}")
                
                print()
                print("[SUCCESS] Все модели найдены!")
                break
            else:
                print("[WARNING] Модели не найдены в ответе")
                print("Проверьте структуру ответа выше")
                
        elif response.status_code == 502:
            print(f"    [502] Bad Gateway")
            if attempt < 2:
                import time
                wait = (attempt + 1) * 3
                print(f"    Ждем {wait} секунд и пробуем снова...")
                time.sleep(wait)
                continue
            else:
                print("    [ERROR] Все попытки вернули 502")
                print("    Возможные причины:")
                print("    1. Модель еще загружается")
                print("    2. Сервер не готов обрабатывать запросы")
                print("    3. Проблема с конфигурацией сервера")
        else:
            print(f"    [ERROR] Код {response.status_code}")
            print(f"    Ответ: {response.text[:500]}")
            
    except requests.exceptions.Timeout:
        print(f"    [TIMEOUT] Превышен таймаут {timeout}с")
        if attempt < 2:
            continue
    except requests.exceptions.ConnectionError:
        print(f"    [ERROR] Не удалось подключиться")
        if attempt < 2:
            import time
            time.sleep(2)
            continue
    except Exception as e:
        print(f"    [ERROR] {e}")
        import traceback
        traceback.print_exc()

print()
print("=" * 70)

