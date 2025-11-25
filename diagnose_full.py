"""Полная диагностика LM Studio API - проверка всего"""
import requests
import socket
import os
import sys
from pathlib import Path

print("=" * 70)
print("ПОЛНАЯ ДИАГНОСТИКА LM STUDIO API")
print("=" * 70)
print()

# 1. Проверка порта
print("[1] Проверка порта 1234...")
print("-" * 70)
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('127.0.0.1', 1234))
    sock.close()
    
    if result == 0:
        print("[OK] Порт 1234 открыт и слушает")
    else:
        print("[ERROR] Порт 1234 не отвечает")
        print("       → Local Server может быть не запущен")
except Exception as e:
    print(f"[ERROR] Ошибка проверки порта: {e}")
print()

# 2. Проверка health endpoint
print("[2] Проверка /health endpoint...")
print("-" * 70)
for endpoint in ["/health", "/", "/v1/models"]:
    try:
        r = requests.get(f"http://127.0.0.1:1234{endpoint}", timeout=5)
        print(f"  {endpoint}: {r.status_code}")
        if r.status_code == 200:
            print(f"    [OK] API работает!")
            if endpoint == "/v1/models":
                try:
                    models = r.json().get('data', [])
                    print(f"    Найдено моделей: {len(models)}")
                except:
                    pass
        elif r.status_code == 502:
            print(f"    [502] Сервер отвечает, но не может обработать запрос")
    except requests.exceptions.ConnectionError:
        print(f"  {endpoint}: [НЕТ ПОДКЛЮЧЕНИЯ]")
    except Exception as e:
        print(f"  {endpoint}: [ОШИБКА] {e}")
print()

# 3. Поиск логов LM Studio
print("[3] Поиск логов LM Studio...")
print("-" * 70)

log_paths = []

# Windows
if sys.platform == "win32":
    appdata = os.getenv('APPDATA', '')
    if appdata:
        log_paths.append(Path(appdata) / "LMStudio" / "logs")
        log_paths.append(Path(appdata) / "LM Studio" / "logs")
    local_appdata = os.getenv('LOCALAPPDATA', '')
    if local_appdata:
        log_paths.append(Path(local_appdata) / "LMStudio" / "logs")
        log_paths.append(Path(local_appdata) / "LM Studio" / "logs")

# macOS
elif sys.platform == "darwin":
    home = Path.home()
    log_paths.append(home / "Library" / "Application Support" / "LMStudio" / "logs")
    log_paths.append(home / "Library" / "Application Support" / "LM Studio" / "logs")

# Linux
else:
    home = Path.home()
    log_paths.append(home / ".config" / "LMStudio" / "logs")
    log_paths.append(home / ".config" / "LM Studio" / "logs")

found_logs = []
for log_path in log_paths:
    if log_path.exists():
        print(f"[OK] Найдена папка логов: {log_path}")
        for log_file in log_path.glob("*.log"):
            if log_file.is_file():
                found_logs.append(log_file)
                print(f"  - {log_file.name} ({log_file.stat().st_size} bytes)")

if not found_logs:
    print("[WARNING] Логи не найдены в стандартных местах")
    print("          Проверьте вручную:")
    for log_path in log_paths:
        print(f"          {log_path}")
print()

# 4. Чтение последних строк логов
if found_logs:
    print("[4] Последние строки из логов (ищем ошибки)...")
    print("-" * 70)
    for log_file in found_logs[:3]:  # Проверяем первые 3 файла
        try:
            print(f"\n{log_file.name}:")
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # Последние 20 строк
                for line in lines[-20:]:
                    line = line.strip()
                    if any(keyword in line.lower() for keyword in ['error', 'fail', '502', 'port', 'bind', 'crash', 'server']):
                        print(f"  ! {line[:100]}")
        except Exception as e:
            print(f"  [ERROR] Не удалось прочитать: {e}")
print()

# 5. Проверка процессов (Windows)
if sys.platform == "win32":
    print("[5] Проверка процессов на порту 1234...")
    print("-" * 70)
    try:
        import subprocess
        result = subprocess.run(
            ['netstat', '-ano'],
            capture_output=True,
            text=True,
            timeout=5
        )
        for line in result.stdout.split('\n'):
            if ':1234' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"[OK] Найден процесс на порту 1234: PID {pid}")
                    # Пробуем узнать имя процесса
                    try:
                        task_result = subprocess.run(
                            ['tasklist', '/FI', f'PID eq {pid}'],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        for task_line in task_result.stdout.split('\n'):
                            if pid in task_line:
                                print(f"      Процесс: {task_line[:80]}")
                    except:
                        pass
    except Exception as e:
        print(f"[WARNING] Не удалось проверить процессы: {e}")
    print()

# 6. Итоговые рекомендации
print("=" * 70)
print("РЕКОМЕНДАЦИИ:")
print("=" * 70)
print()
print("1. В LM Studio проверьте:")
print("   Settings -> Local Server API")
print("   - 'Enable Local Server API' должен быть ВКЛЮЧЕН")
print("   - Порт должен быть 1234 (или свободный)")
print("   - Модель должна быть выбрана")
print()
print("2. Если API не запускается:")
print("   - Перезапустите LM Studio полностью")
print("   - Проверьте логи выше на наличие ошибок")
print("   - Убедитесь что порт 1234 свободен")
print()
print("3. Если порт занят:")
print("   - Найдите процесс (см. выше)")
print("   - Закройте его или используйте другой порт")
print()
print("4. Если модель не загружается для API:")
print("   - Попробуйте другую модель (меньше размер)")
print("   - Или используйте квантование Q4_K_M / Q5_K_S")
print()
print("=" * 70)

