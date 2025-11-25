"""Чтение логов LM Studio для поиска ошибок"""
import os
import sys
from pathlib import Path

print("=" * 70)
print("ЧТЕНИЕ ЛОГОВ LM STUDIO")
print("=" * 70)
print()

# Поиск папки с логами
log_paths = []

if sys.platform == "win32":
    appdata = os.getenv('APPDATA', '')
    local_appdata = os.getenv('LOCALAPPDATA', '')
    if appdata:
        log_paths.extend([
            Path(appdata) / "LMStudio" / "logs",
            Path(appdata) / "LM Studio" / "logs"
        ])
    if local_appdata:
        log_paths.extend([
            Path(local_appdata) / "LMStudio" / "logs",
            Path(local_appdata) / "LM Studio" / "logs"
        ])
elif sys.platform == "darwin":
    home = Path.home()
    log_paths.extend([
        home / "Library" / "Application Support" / "LMStudio" / "logs",
        home / "Library" / "Application Support" / "LM Studio" / "logs"
    ])
else:
    home = Path.home()
    log_paths.extend([
        home / ".config" / "LMStudio" / "logs",
        home / ".config" / "LM Studio" / "logs"
    ])

# Поиск логов
found_logs = []
for log_path in log_paths:
    if log_path.exists():
        print(f"[OK] Найдена папка: {log_path}")
        for log_file in sorted(log_path.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True):
            if log_file.is_file():
                found_logs.append(log_file)

if not found_logs:
    print("[WARNING] Логи не найдены")
    print()
    print("Проверьте вручную:")
    for log_path in log_paths:
        print(f"  {log_path}")
    sys.exit(1)

print(f"\nНайдено {len(found_logs)} лог-файлов")
print()

# Ключевые слова для поиска
keywords = [
    'error', 'fail', '502', 'port', 'bind', 'crash', 'server',
    'cannot', 'unable', 'exception', 'timeout', 'refused'
]

# Читаем последние строки из каждого лога
print("=" * 70)
print("ПОИСК ОШИБОК В ЛОГАХ:")
print("=" * 70)
print()

for log_file in found_logs[:5]:  # Проверяем 5 последних файлов
    print(f"\n{'='*70}")
    print(f"Файл: {log_file.name}")
    print(f"Размер: {log_file.stat().st_size} bytes")
    print(f"{'='*70}")
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            
        # Последние 50 строк
        recent_lines = lines[-50:] if len(lines) > 50 else lines
        
        # Ищем строки с ошибками
        error_lines = []
        for i, line in enumerate(recent_lines, start=len(lines) - len(recent_lines) + 1):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                error_lines.append((i, line.strip()))
        
        if error_lines:
            print(f"\nНайдено {len(error_lines)} строк с ошибками:")
            for line_num, line in error_lines[-10:]:  # Последние 10 ошибок
                print(f"  Строка {line_num}: {line[:150]}")
        else:
            print("\nОшибок не найдено в последних строках")
            print("Последние 5 строк:")
            for line in recent_lines[-5:]:
                print(f"  {line.strip()[:150]}")
                
    except Exception as e:
        print(f"[ERROR] Не удалось прочитать файл: {e}")

print()
print("=" * 70)
print("РЕКОМЕНДАЦИИ:")
print("=" * 70)
print()
print("Если найдены ошибки:")
print("  1. Скопируйте строки с ошибками")
print("  2. Проверьте что они означают")
print("  3. Исправьте проблему (порт, память, модель)")
print()
print("Если ошибок нет:")
print("  1. API сервер может быть просто не запущен")
print("  2. Проверьте настройки в LM Studio")
print("  3. Перезапустите LM Studio")
print()

