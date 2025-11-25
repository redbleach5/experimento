"""Проверка модели в конфиге"""
import yaml

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
    model_name = config.get('model', {}).get('model_name', 'не найдена')
    provider = config.get('model', {}).get('provider', 'не найден')
    
print(f"Провайдер: {provider}")
print(f"Модель: {model_name}")

