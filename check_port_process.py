"""Проверка порта и процессов (Windows)"""
import subprocess
import sys

print("=" * 70)
print("ПРОВЕРКА ПОРТА И ПРОЦЕССОВ")
print("=" * 70)
print()

if sys.platform != "win32":
    print("Этот скрипт для Windows. Для Linux/macOS используйте:")
    print("  lsof -i :1234")
    sys.exit(0)

print("Проверка порта 1234...")
print()

# Проверка netstat
try:
    result = subprocess.run(
        ['netstat', '-ano'],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    found = False
    for line in result.stdout.split('\n'):
        if ':1234' in line and ('LISTENING' in line or 'LISTEN' in line):
            found = True
            parts = line.split()
            if len(parts) >= 5:
                pid = parts[-1]
                print(f"[OK] Порт 1234 занят процессом PID: {pid}")
                print(f"     Строка: {line.strip()}")
                print()
                
                # Получаем имя процесса
                try:
                    task_result = subprocess.run(
                        ['tasklist', '/FI', f'PID eq {pid}', '/FO', 'CSV'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    for task_line in task_result.stdout.split('\n'):
                        if pid in task_line and ',' in task_line:
                            process_name = task_line.split(',')[0].strip('"')
                            print(f"     Процесс: {process_name}")
                            if 'lmstudio' in process_name.lower() or 'lm studio' in process_name.lower():
                                print(f"     [OK] Это LM Studio!")
                            else:
                                print(f"     [WARNING] Это не LM Studio - возможно конфликт портов")
                except Exception as e:
                    print(f"     [WARNING] Не удалось получить имя процесса: {e}")
    
    if not found:
        print("[WARNING] Порт 1234 не занят")
        print("          → Local Server может быть не запущен")
        
except Exception as e:
    print(f"[ERROR] Ошибка проверки: {e}")

print()
print("=" * 70)
print("РЕКОМЕНДАЦИИ:")
print("=" * 70)
print()
print("Если порт занят НЕ LM Studio:")
print("  1. Найдите процесс по PID")
print("  2. Закройте его: taskkill /PID <PID> /F")
print("  3. Или используйте другой порт в настройках LM Studio")
print()
print("Если порт не занят:")
print("  1. В LM Studio: Settings -> Local Server API")
print("  2. Включите 'Enable Local Server API'")
print("  3. Перезапустите LM Studio")
print()

