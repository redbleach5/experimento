"""
Скрипт установки и настройки AI Code Agent
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 9):
        print("❌ Требуется Python 3.9 или выше")
        print(f"   Текущая версия: {sys.version}")
        return False
    print(f"✓ Python {sys.version.split()[0]}")
    return True

def check_ollama():
    """Проверка наличия Ollama"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ Ollama установлен")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("❌ Ollama не найден")
    print("   Установите Ollama: https://ollama.ai")
    return False

def check_cuda():
    """Проверка наличия CUDA"""
    try:
        result = subprocess.run(['nvidia-smi'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✓ NVIDIA GPU обнаружен")
            # Извлекаем информацию о GPU
            for line in result.stdout.split('\n'):
                if 'RTX' in line or 'GeForce' in line:
                    print(f"  {line.strip()}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    
    print("⚠ NVIDIA GPU не обнаружен (будет использоваться CPU)")
    return False

def install_dependencies():
    """Установка Python зависимостей"""
    print("\n📦 Установка зависимостей...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                      check=True)
        print("✓ Зависимости установлены")
        return True
    except subprocess.CalledProcessError:
        print("❌ Ошибка установки зависимостей")
        return False

def check_models():
    """Проверка установленных моделей"""
    print("\n🔍 Проверка моделей Ollama...")
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            models = result.stdout.strip().split('\n')[1:]  # Пропускаем заголовок
            if models:
                print("✓ Установленные модели:")
                for model in models:
                    if model.strip():
                        print(f"  • {model.strip()}")
            else:
                print("⚠ Модели не установлены")
                print("   Рекомендуется: ollama pull deepseek-coder:6.7b")
            return True
    except Exception as e:
        print(f"⚠ Не удалось проверить модели: {e}")
    
    return False

def create_directories():
    """Создание необходимых директорий"""
    dirs = ['history', 'templates']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
    print("✓ Директории созданы")

def main():
    """Основная функция установки"""
    print("=" * 60)
    print("🚀 Установка AI Code Agent")
    print("=" * 60)
    
    # Проверки
    print("\n📋 Проверка системы:")
    all_ok = True
    
    if not check_python_version():
        all_ok = False
    
    check_cuda()
    
    ollama_ok = check_ollama()
    if not ollama_ok:
        all_ok = False
    
    # Установка зависимостей
    if all_ok:
        if install_dependencies():
            create_directories()
            check_models()
    
    # Итоги
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ Установка завершена успешно!")
        print("\n📝 Следующие шаги:")
        print("   1. Установите модель: ollama pull deepseek-coder:6.7b")
        print("   2. Запустите CLI: python cli.py")
        print("   3. Или веб-интерфейс: python web_ui.py")
    else:
        print("⚠ Установка завершена с предупреждениями")
        print("   Проверьте сообщения выше и исправьте проблемы")
    print("=" * 60)

if __name__ == "__main__":
    main()

