"""
Надежный запуск GUI с обработкой ошибок
"""

import sys
import os
import traceback

print("=" * 70)
print("ЗАПУСК AI CODE AGENT GUI")
print("=" * 70)
print()

# Проверка зависимостей
print("[*] Проверка зависимостей...")
try:
    import tkinter
    print("    [OK] tkinter")
except ImportError:
    print("    [ERROR] tkinter не установлен")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

try:
    import requests
    print("    [OK] requests")
except ImportError:
    print("    [ERROR] requests не установлен")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

try:
    import yaml
    print("    [OK] yaml")
except ImportError:
    print("    [ERROR] yaml не установлен")
    input("Нажмите Enter для выхода...")
    sys.exit(1)

print()

# Запуск GUI
print("[*] Запуск GUI интерфейса...")
print()

try:
    from gui import CodeAgentGUI
    import tkinter as tk
    
    root = tk.Tk()
    app = CodeAgentGUI(root)
    
    print("[OK] GUI запущен успешно!")
    print()
    print("Интерфейс должен быть открыт.")
    print("Если окно не видно, проверьте панель задач.")
    print()
    
    root.mainloop()
    
except KeyboardInterrupt:
    print("\n[!] Прервано пользователем")
except Exception as e:
    print(f"\n[ERROR] Ошибка при запуске GUI: {e}")
    print()
    print("Детали ошибки:")
    traceback.print_exc()
    print()
    input("Нажмите Enter для выхода...")

