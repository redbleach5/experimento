"""
Детальная проверка подключения к LM Studio
"""

import requests
import json

def test_lmstudio():
    """Детальная проверка LM Studio"""
    # Пробуем разные варианты адресов
    base_urls = [
        "http://127.0.0.1:1234",
        "http://localhost:1234"
    ]
    
    base_url = None
    for url in base_urls:
        try:
            print(f"[*] Проверка {url}...")
            response = requests.get(f"{url}/v1/models", timeout=5)
            if response.status_code == 200:
                base_url = url
                print(f"[OK] Рабочий адрес: {url}")
                break
        except:
            continue
    
    if not base_url:
        base_url = "http://127.0.0.1:1234"  # По умолчанию
    
    print("=" * 60)
    print("Детальная проверка LM Studio")
    print("=" * 60)
    print()
    
    # Тест 1: Проверка базового подключения
    print("[TEST 1] Проверка базового подключения...")
    try:
        response = requests.get(f"{base_url}/v1/models", timeout=10)
        print(f"  Статус код: {response.status_code}")
        print(f"  Заголовки: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("  [OK] Подключение успешно!")
            data = response.json()
            models = data.get('data', [])
            print(f"  Найдено моделей: {len(models)}")
            
            if models:
                print("\n  Доступные модели:")
                for model in models:
                    model_id = model.get('id', 'Unknown')
                    print(f"    - {model_id}")
                
                # Тест 2: Проверка chat completions
                print("\n[TEST 2] Тест API chat/completions...")
                test_model = models[0].get('id', '')
                
                payload = {
                    "model": test_model,
                    "messages": [
                        {"role": "user", "content": "Привет! Ответь одним словом: работает?"}
                    ],
                    "max_tokens": 10,
                    "temperature": 0.7
                }
                
                try:
                    chat_response = requests.post(
                        f"{base_url}/v1/chat/completions",
                        json=payload,
                        timeout=30
                    )
                    print(f"  Статус код: {chat_response.status_code}")
                    
                    if chat_response.status_code == 200:
                        result = chat_response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            content = result['choices'][0]['message']['content']
                            print(f"  [OK] Ответ получен: {content}")
                            print("\n" + "=" * 60)
                            print("[SUCCESS] LM Studio полностью готов к работе!")
                            print("=" * 60)
                            return test_model
                        else:
                            print("  [ERROR] Неожиданный формат ответа")
                    else:
                        print(f"  [ERROR] Ошибка: {chat_response.text}")
                except Exception as e:
                    print(f"  [ERROR] Ошибка при тесте API: {e}")
            else:
                print("  [WARNING] Модели не найдены")
        else:
            print(f"  [ERROR] Сервер вернул ошибку: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("  [ERROR] Не удалось подключиться к серверу")
        print("  Убедитесь, что:")
        print("    1. LM Studio запущен")
        print("    2. Local Server включен (Settings -> Local Server)")
        print("    3. Модель загружена")
    except Exception as e:
        print(f"  [ERROR] Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    model_name = test_lmstudio()
    
    if model_name:
        print(f"\n[*] Рекомендуемая модель для config.yaml: {model_name}")
        print("\nТеперь можно запустить:")
        print("  python gui.py")
        print("  или")
        print("  python test_lmstudio.py")
    else:
        print("\n[!] Не удалось подключиться к LM Studio")

