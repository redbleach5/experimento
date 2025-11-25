"""
Проверка проблем с GUI
"""

import sys
import os

print("Проверка окружения для GUI...")
print()

# Проверка tkinter
try:
    import tkinter as tk
    print("[OK] tkinter доступен")
    
    # Пробуем создать тестовое окно
    root = tk.Tk()
    root.withdraw()  # Скрываем окно
    root.destroy()
    print("[OK] tkinter работает")
except ImportError:
    print("[ERROR] tkinter не установлен")
    print("Установите: pip install tk")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Проблема с tkinter: {e}")
    sys.exit(1)

# Проверка других зависимостей
dependencies = ['requests', 'yaml', 'agent']
for dep in dependencies:
    try:
        __import__(dep)
        print(f"[OK] {dep} доступен")
    except ImportError:
        print(f"[ERROR] {dep} не найден")

print()
print("Проверка завершена")

