"""
Диагностика проблем с LM Studio
"""

import requests
import socket

print("=" * 60)
print("ДИАГНОСТИКА LM STUDIO")
print("=" * 60)
print()

# Проверка 1: Порт доступен
print("[1] Проверка доступности порта 1234...")
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 1234))
    sock.close()
    
    if result == 0:
        print("    [OK] Порт 1234 открыт и доступен")
    else:
        print("    [ERROR] Порт 1234 недоступен")
        print("    Local Server может быть не запущен")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Проверка 2: HTTP соединение
print("[2] Проверка HTTP соединения...")
try:
    response = requests.get('http://127.0.0.1:1234/', timeout=5)
    print(f"    Статус: {response.status_code}")
    print(f"    Заголовки: {dict(list(response.headers.items())[:2])}")
except requests.exceptions.ConnectionError:
    print("    [ERROR] Не удалось подключиться")
    print("    Local Server не запущен или недоступен")
except requests.exceptions.HTTPError as e:
    print(f"    HTTP ошибка: {e.response.status_code}")
    if e.response.status_code == 502:
        print("    [502] Сервер работает, но не может обработать запрос")
except Exception as e:
    print(f"    [ERROR] {e}")

print()

# Проверка 3: Разные варианты адресов
print("[3] Проверка разных адресов...")
addresses = [
    "http://127.0.0.1:1234",
    "http://localhost:1234",
]

for addr in addresses:
    try:
        resp = requests.get(f"{addr}/v1/models", timeout=3)
        print(f"    {addr}: {resp.status_code}")
        if resp.status_code == 200:
            print(f"    [OK] Рабочий адрес: {addr}")
            break
    except:
        print(f"    {addr}: недоступен")

print()

# Итоговые рекомендации
print("=" * 60)
print("ДИАГНОСТИКА ЗАВЕРШЕНА")
print("=" * 60)
print()
print("ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ:")
print()
print("1. Local Server не запущен:")
print("   - Откройте LM Studio")
print("   - Settings → Local Server")
print("   - Включите 'Local Server'")
print("   - Нажмите 'Start Server'")
print()
print("2. Сервер запущен, но модель не готова:")
print("   - Убедитесь, что модель загружена в разделе Chat")
print("   - Проверьте статус - должно быть 'READY'")
print("   - Попробуйте отправить сообщение в Chat")
print()
print("3. Проблема с конфигурацией сервера:")
print("   - Перезапустите Local Server")
print("   - Проверьте, что порт 1234 не занят")
print("   - Проверьте логи в LM Studio (Developer Logs)")
print()
print("4. Модель слишком большая:")
print("   - Модель 30B требует много ресурсов")
print("   - Убедитесь, что достаточно VRAM/RAM")
print("   - Попробуйте использовать меньшую модель")
print()
print("=" * 60)

