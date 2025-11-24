"""
Тестирование подключения к LM Studio и работы агента
"""

import requests
import json
from agent import CodeAgent

def test_connection():
    """Тест подключения к LM Studio"""
    print("=" * 60)
    print("Тестирование подключения к LM Studio")
    print("=" * 60)
    print()
    
    try:
        print("[*] Проверка доступности сервера...")
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        
        if response.status_code == 200:
            print("[OK] Сервер доступен!")
            print()
            
            models = response.json().get('data', [])
            if models:
                print(f"[OK] Найдено моделей: {len(models)}")
                print()
                print("Доступные модели:")
                for i, model in enumerate(models, 1):
                    model_id = model.get('id', 'Unknown')
                    print(f"  {i}. {model_id}")
                
                # Используем первую модель
                first_model = models[0].get('id', '')
                print()
                print(f"[*] Используем модель: {first_model}")
                return first_model
            else:
                print("[!] Модели не найдены")
                return None
        else:
            print(f"[ERROR] Сервер недоступен (статус: {response.status_code})")
            return None
            
    except Exception as e:
        print(f"[ERROR] Ошибка подключения: {e}")
        return None

def test_agent(model_name):
    """Тест работы агента"""
    print()
    print("=" * 60)
    print("Тестирование AI Code Agent")
    print("=" * 60)
    print()
    
    try:
        print(f"[*] Инициализация агента с моделью: {model_name}")
        
        # Обновляем конфигурацию
        import yaml
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        config['model']['model_name'] = model_name
        
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
        
        agent = CodeAgent()
        print("[OK] Агент инициализирован!")
        print()
        
        # Тестовый запрос
        test_prompt = "Напиши функцию на Python для вычисления факториала числа с использованием рекурсии"
        print(f"[*] Тестовый запрос: {test_prompt}")
        print()
        print("[*] Генерация ответа...")
        print("-" * 60)
        
        response = ""
        for chunk in agent.ask(test_prompt, stream=True):
            response += chunk
            print(chunk, end='', flush=True)
        
        print()
        print("-" * 60)
        print()
        print("[OK] Тест успешно завершен!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка при тестировании агента: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Тест подключения
    model_name = test_connection()
    
    if model_name:
        # Тест агента
        success = test_agent(model_name)
        
        if success:
            print()
            print("=" * 60)
            print("[SUCCESS] Все тесты пройдены успешно!")
            print("=" * 60)
            print()
            print("Теперь можно использовать GUI: python gui.py")
        else:
            print()
            print("=" * 60)
            print("[ERROR] Тест не пройден")
            print("=" * 60)
    else:
        print()
        print("[ERROR] Не удалось подключиться к LM Studio")
        print("Убедитесь, что:")
        print("1. LM Studio запущен")
        print("2. Local Server включен")
        print("3. Модель загружена")
    
    print()
    input("Нажмите Enter для выхода...")

