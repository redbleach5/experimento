"""
Скрипт для проверки статуса LM Studio
"""

import requests
import sys
import os

# Устанавливаем UTF-8 для Windows
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')

def check_lmstudio():
    """Проверка доступности LM Studio"""
    print("=" * 60)
    print("  Проверка LM Studio")
    print("=" * 60)
    print()
    
    # Проверка доступности сервера
    try:
        print("[*] Проверка подключения к LM Studio...")
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        
        if response.status_code == 200:
            print("[OK] LM Studio сервер доступен!")
            print()
            
            # Получение списка моделей
            models = response.json().get('data', [])
            if models:
                print(f"[*] Найдено моделей: {len(models)}")
                print()
                print("Доступные модели:")
                for i, model in enumerate(models, 1):
                    model_id = model.get('id', 'Unknown')
                    print(f"  {i}. {model_id}")
                print()
                print("[OK] Все готово! Можно использовать AI Code Agent.")
                return True
            else:
                print("[!] Модели не найдены")
                print()
                print("Инструкция:")
                print("1. Откройте LM Studio")
                print("2. Перейдите в раздел 'Chat'")
                print("3. Загрузите модель (Select a model to load)")
                print("4. Убедитесь, что Local Server включен")
                return False
        else:
            print(f"[ERROR] Сервер недоступен (статус: {response.status_code})")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Не удалось подключиться к LM Studio")
        print()
        print("Возможные причины:")
        print("1. LM Studio не установлен")
        print("2. LM Studio не запущен")
        print("3. Local Server не включен")
        print()
        print("Решение:")
        print("1. Установите LM Studio: https://lmstudio.ai")
        print("2. Запустите LM Studio")
        print("3. Перейдите в Settings -> Local Server")
        print("4. Включите 'Local Server'")
        print("5. Нажмите 'Start Server'")
        return False
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = check_lmstudio()
    print()
    if success:
        print("[*] Запустите GUI: python gui.py")
    else:
        print("[*] См. инструкцию: LM_STUDIO_SETUP.md")
    print()
    input("Нажмите Enter для выхода...")

