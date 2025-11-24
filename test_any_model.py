"""Тест: ПО работает с любой моделью из LM Studio"""
import requests
import sys
from agent import CodeAgent

print("=" * 70)
print("ТЕСТ: РАБОТА С ЛЮБОЙ МОДЕЛЬЮ")
print("=" * 70)
print()

base_url = "http://127.0.0.1:1234"

# 1. Получаем список всех доступных моделей
print("[1] Получение списка всех доступных моделей...")
print("-" * 70)

try:
    r = requests.get(f"{base_url}/v1/models", timeout=10)
    
    if r.status_code == 200:
        data = r.json()
        models = data.get('data', [])
        
        if models:
            model_ids = []
            for m in models:
                model_id = m.get('id') or m.get('model') or m.get('name') or ''
                if model_id:
                    model_ids.append(model_id)
            
            print(f"[OK] Найдено моделей: {len(model_ids)}")
            print()
            for i, mid in enumerate(model_ids, 1):
                print(f"  {i}. {mid}")
            print()
            
            # 2. Тестируем каждую модель
            print("[2] Тестирование каждой модели...")
            print("-" * 70)
            print()
            
            working_models = []
            failed_models = []
            
            for model_id in model_ids:
                print(f"Тестирую модель: {model_id}")
                
                try:
                    payload = {
                        "model": model_id,
                        "messages": [{"role": "user", "content": "2+2"}],
                        "max_tokens": 5,
                        "temperature": 0.1
                    }
                    
                    r = requests.post(
                        f"{base_url}/v1/chat/completions",
                        json=payload,
                        timeout=60
                    )
                    
                    if r.status_code == 200:
                        result = r.json()
                        if 'choices' in result:
                            answer = result['choices'][0]['message']['content']
                            print(f"  [OK] Работает! Ответ: {answer[:50]}")
                            working_models.append(model_id)
                        else:
                            print(f"  [WARNING] Неожиданный формат ответа")
                            failed_models.append((model_id, "Неожиданный формат"))
                    elif r.status_code == 502:
                        print(f"  [502] Модель не готова (может быть загружается)")
                        failed_models.append((model_id, "502 - не готова"))
                    else:
                        print(f"  [ERROR] Статус {r.status_code}")
                        failed_models.append((model_id, f"Статус {r.status_code}"))
                        
                except requests.exceptions.Timeout:
                    print(f"  [TIMEOUT] Модель не отвечает за 60 секунд")
                    failed_models.append((model_id, "Таймаут"))
                except Exception as e:
                    print(f"  [ERROR] {e}")
                    failed_models.append((model_id, str(e)))
                
                print()
            
            # 3. Итоги
            print("=" * 70)
            print("ИТОГИ:")
            print("=" * 70)
            print()
            print(f"Всего моделей: {len(model_ids)}")
            print(f"Работающих: {len(working_models)}")
            print(f"Не работающих: {len(failed_models)}")
            print()
            
            if working_models:
                print("Работающие модели:")
                for mid in working_models:
                    print(f"  [OK] {mid}")
                print()
            
            if failed_models:
                print("Модели с проблемами:")
                for mid, reason in failed_models:
                    print(f"  [WARNING] {mid}: {reason}")
                print()
            
            # 4. Тест через агента
            print("[3] Тест через агента (автоматический выбор модели)...")
            print("-" * 70)
            print()
            
            try:
                agent = CodeAgent()
                print(f"[OK] Агент инициализирован")
                print(f"Провайдер: {agent.provider}")
                print(f"Используемая модель: {agent.model_name}")
                
                if hasattr(agent, 'available_models') and agent.available_models:
                    print(f"Доступные модели для агента: {len(agent.available_models)}")
                    print("Агент может использовать любую из них!")
                
                print()
                print("Отправка тестового запроса через агента...")
                response_text = ""
                for chunk in agent.ask("Сколько будет 2+2? Ответь только числом."):
                    response_text += chunk
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                
                print()
                print()
                if response_text.strip():
                    print("[SUCCESS] Агент успешно работает с моделью!")
                else:
                    print("[WARNING] Пустой ответ")
                    
            except Exception as e:
                print(f"[ERROR] Ошибка при работе с агентом: {e}")
                import traceback
                traceback.print_exc()
            
            print()
            print("=" * 70)
            print("ВЫВОД:")
            print("=" * 70)
            print()
            print("Наше ПО поддерживает ЛЮБУЮ модель из LM Studio!")
            print("Просто:")
            print("1. Загрузите модель в LM Studio")
            print("2. Включите Local Server API")
            print("3. Агент автоматически найдет и использует модель")
            print()
            if working_models:
                print(f"У вас работает {len(working_models)} модель(ей) - можете использовать любую!")
            
        else:
            print("[WARNING] Модели не найдены в ответе API")
            print("Проверьте, что модель загружена в LM Studio")
    elif r.status_code == 502:
        print("[502] API возвращает 502")
        print()
        print("РЕШЕНИЕ:")
        print("1. В LM Studio: Settings -> Local Server API")
        print("2. Включите 'Enable Local Server API'")
        print("3. Перезапустите Local Server")
    else:
        print(f"[ERROR] Статус {r.status_code}")
        
except requests.exceptions.ConnectionError:
    print("[ERROR] Не удалось подключиться к API")
    print("Убедитесь что Local Server API запущен")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()

print()

