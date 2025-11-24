"""Поиск правильного порта для LM Studio"""
import requests
import socket

print("=" * 70)
print("ПОИСК ПРАВИЛЬНОГО ПОРТА LM STUDIO")
print("=" * 70)
print()

# Проверяем какие порты слушают
print("Проверка открытых портов...")
open_ports = []
for port in range(1230, 1250):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.1)
    result = sock.connect_ex(('127.0.0.1', port))
    if result == 0:
        open_ports.append(port)
        print(f"  Порт {port}: ОТКРЫТ")
    sock.close()

print()
print("Проверка найденных портов на LM Studio API...")
for port in open_ports:
    try:
        r = requests.get(f"http://127.0.0.1:{port}/v1/models", timeout=3)
        if r.status_code == 200:
            print(f"  [OK] Порт {port}: API работает!")
            try:
                models = r.json().get('data', [])
                print(f"      Найдено моделей: {len(models)}")
            except:
                pass
        elif r.status_code == 502:
            print(f"  [502] Порт {port}: Сервер отвечает, но модель не готова")
        else:
            print(f"  [{r.status_code}] Порт {port}")
    except:
        pass

print()
print("=" * 70)
print("РЕКОМЕНДАЦИИ:")
print("=" * 70)
print("1. Проверьте порт в LM Studio: Settings -> Local Server")
print("2. Если порт другой - обновите config.yaml")
print()

