"""Проверка модели и API в LM Studio - универсальный скрипт"""
import requests
import json
import sys

print("=" * 70)
print("ПРОВЕРКА МОДЕЛИ И API В LM STUDIO")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"

# 1. Проверка health endpoint
print("[1] Проверка health endpoint...")
print("-" * 70)
try:
    r = requests.get(f"{base_url}/health", timeout=5)
    if r.status_code == 200:
        print("[OK] Health endpoint работает!")
        try:
            data = r.json()
            print(f"    Ответ: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"    Ответ: {r.text[:200]}")
    else:
        print(f"[{r.status_code}] Health endpoint не отвечает")
except requests.exceptions.ConnectionError:
    print("[ERROR] Не удалось подключиться к серверу")
    print("        -> Local Server API может быть не запущен")
except Exception as e:
    print(f"[ERROR] {e}")
print()

# 2. Проверка списка моделей
print("[2] Проверка доступных моделей...")
print("-" * 70)
try:
    r = requests.get(f"{base_url}/v1/models", timeout=10)
    
    if r.status_code == 200:
        print("[OK] API работает! Модели доступны")
        print()
        data = r.json()
        models = data.get('data', [])
        
        if models:
            print(f"Найдено моделей: {len(models)}")
            print()
            for i, model in enumerate(models, 1):
                model_id = model.get('id') or model.get('model') or model.get('name', 'unknown')
                print(f"  {i}. {model_id}")
                
                # Проверяем на Flux
                if 'flux' in model_id.lower():
                    print(f"      [FLUX] Найдена модель Flux!")
        else:
            print("[WARNING] Модели не найдены в ответе")
            print(f"Полный ответ: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
    elif r.status_code == 502:
        print("[502] API возвращает 502 Bad Gateway")
        print()
        print("ПРОБЛЕМА: Local Server API не настроен правильно")
        print()
        print("РЕШЕНИЕ:")
        print("1. В LM Studio: Settings -> Local Server API")
        print("2. Включите 'Enable Local Server API'")
        print("3. Или нажмите 'Start Server'")
        print("4. Убедитесь что модель выбрана")
        print("5. Перезапустите Local Server")
    else:
        print(f"[ERROR] Статус {r.status_code}")
        print(f"Ответ: {r.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("[ERROR] Не удалось подключиться")
    print("        -> Убедитесь что Local Server API запущен")
except Exception as e:
    print(f"[ERROR] {e}")
print()

# 3. Тест запроса к модели
print("[3] Тест запроса к модели...")
print("-" * 70)

# Пробуем получить модель из конфига или использовать первую доступную
model_name = None

try:
    r = requests.get(f"{base_url}/v1/models", timeout=5)
    if r.status_code == 200:
        models = r.json().get('data', [])
        if models:
            model_name = models[0].get('id') or models[0].get('model')
            print(f"Используем модель: {model_name}")
        else:
            print("[WARNING] Модели не найдены, используем из конфига")
            # Пробуем из конфига
            try:
                import yaml
                with open('config.yaml', 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    model_name = config.get('model', {}).get('model_name')
                    print(f"Используем модель из конфига: {model_name}")
            except:
                pass
except:
    # Пробуем из конфига
    try:
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            model_name = config.get('model', {}).get('model_name')
            print(f"Используем модель из конфига: {model_name}")
    except:
        pass

if not model_name:
    print("[SKIP] Не удалось определить модель для теста")
    print()
else:
    print(f"Отправка тестового запроса к модели '{model_name}'...")
    print()
    
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Сколько будет 2+2? Ответь только числом."}],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        r = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            timeout=120
        )
        
        if r.status_code == 200:
            result = r.json()
            if 'choices' in result:
                answer = result['choices'][0]['message']['content']
                print("=" * 70)
                print("[SUCCESS] МОДЕЛЬ ОТВЕТИЛА!")
                print("=" * 70)
                print(f"Ответ: {answer}")
                print("=" * 70)
                print()
                print("[OK] API полностью работает! Можно использовать агента.")
            else:
                print(f"[WARNING] Неожиданный формат ответа")
                print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
        elif r.status_code == 502:
            print("[502] Модель не может обработать запрос")
            print()
            print("ВОЗМОЖНЫЕ ПРИЧИНЫ:")
            print("1. Модель еще загружается")
            print("2. Модель слишком большая (попробуйте Q4_K_M или Q5_K_S)")
            print("3. Не хватает памяти")
            print("4. Модель не поддерживает текстовую генерацию")
        else:
            print(f"[ERROR] Статус {r.status_code}")
            print(f"Ответ: {r.text[:200]}")
    except requests.exceptions.Timeout:
        print("[TIMEOUT] Модель не отвечает за 2 минуты")
        print("          Возможно модель слишком большая или медленная")
    except Exception as e:
        print(f"[ERROR] {e}")

print()
print("=" * 70)
print("ИТОГОВАЯ ДИАГНОСТИКА:")
print("=" * 70)
print()

# Финальная проверка
try:
    r = requests.get(f"{base_url}/v1/models", timeout=5)
    if r.status_code == 200:
        print("[OK] API работает корректно")
        print("[OK] Модели доступны")
        print()
        print("ВСЕ ГОТОВО! Можно использовать агента:")
        print("  python test_agent_direct.py")
    elif r.status_code == 502:
        print("[ERROR] API возвращает 502")
        print()
        print("НУЖНО СДЕЛАТЬ:")
        print("1. LM Studio -> Settings -> Local Server API")
        print("2. Включите 'Enable Local Server API'")
        print("3. Нажмите 'Start Server'")
        print("4. Убедитесь что модель выбрана и имеет статус 'READY'")
        print("5. Перезапустите Local Server")
    else:
        print(f"[ERROR] API не работает (статус {r.status_code})")
except:
    print("[ERROR] Не удалось подключиться к API")
    print()
    print("Убедитесь что:")
    print("1. LM Studio запущен")
    print("2. Local Server API включен")
    print("3. Порт 1234 свободен")

print()

