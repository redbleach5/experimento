"""
Быстрая проверка готовности системы перед тестированием
"""

import requests
import yaml
import time

print("=" * 60)
print("Проверка готовности системы для тестирования")
print("=" * 60)
print()

# Проверка 1: LM Studio сервер
print("[1] Проверка LM Studio сервера...")
try:
    response = requests.get('http://127.0.0.1:1234/v1/models', timeout=5)
    if response.status_code == 200:
        models = response.json().get('data', [])
        if models:
            print(f"    [OK] Сервер доступен, найдено моделей: {len(models)}")
            model_name = models[0].get('id', '')
            print(f"    [OK] Первая модель: {model_name}")
        else:
            print("    [!] Сервер доступен, но модели не найдены")
    else:
        print(f"    [ERROR] Сервер вернул код: {response.status_code}")
except Exception as e:
    print(f"    [ERROR] Не удалось подключиться: {e}")

print()

# Проверка 2: Конфигурация
print("[2] Проверка конфигурации...")
try:
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    provider = config.get('model', {}).get('provider', '')
    model_name = config.get('model', {}).get('model_name', '')
    
    print(f"    [OK] Провайдер: {provider}")
    print(f"    [OK] Модель: {model_name}")
    
    if provider == 'lmstudio':
        print("    [OK] Конфигурация настроена на LM Studio")
    else:
        print(f"    [!] Провайдер установлен на: {provider}")
        
except Exception as e:
    print(f"    [ERROR] Ошибка чтения конфигурации: {e}")

print()

# Проверка 3: Зависимости
print("[3] Проверка зависимостей...")
try:
    import requests
    import yaml
    import tkinter
    print("    [OK] Все основные зависимости установлены")
except ImportError as e:
    print(f"    [ERROR] Отсутствует зависимость: {e}")

print()

# Итог
print("=" * 60)
print("РЕЗУЛЬТАТ:")
print("=" * 60)
print()
print("GUI интерфейс должен быть запущен.")
print()
print("ИНСТРУКЦИЯ ДЛЯ ТЕСТИРОВАНИЯ:")
print("1. В GUI выберите провайдер 'lmstudio' в боковой панели")
print("2. Нажмите 'Обновить список моделей'")
print("3. Выберите модель из списка")
print("4. Введите тестовый запрос, например:")
print("   'Напиши функцию на Python для вычисления факториала'")
print("5. Нажмите 'Отправить' или Ctrl+Enter")
print()
print("Если возникнут ошибки:")
print("- Убедитесь, что в LM Studio статус 'READY'")
print("- Проверьте, что модель полностью загружена")
print("- Попробуйте перезапустить Local Server в LM Studio")
print()
print("=" * 60)

