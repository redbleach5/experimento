"""Автоматическое создание репозитория на GitHub и пуш кода"""
import requests
import subprocess
import sys
import os
import json

print("=" * 70)
print("АВТОМАТИЧЕСКОЕ СОЗДАНИЕ РЕПОЗИТОРИЯ И ПУШ")
print("=" * 70)
print()

# Параметры
repo_name = "experimento"
username = "redbleach5"
repo_url = f"https://github.com/{username}/{repo_name}"

print(f"Репозиторий: {repo_url}")
print()

# Шаг 1: Получаем токен
print("[1] Получение GitHub токена...")
print("-" * 70)

# Пробуем найти токен в переменных окружения
token = os.getenv('GITHUB_TOKEN')

if not token:
    print("Токен не найден в переменных окружения.")
    print()
    print("Для создания репозитория нужен GitHub Personal Access Token.")
    print("Получите его здесь: https://github.com/settings/tokens")
    print()
    token = input("Введите токен (или нажмите Enter для пропуска): ").strip()

if not token:
    print()
    print("[SKIP] Токен не указан. Пропускаю создание репозитория.")
    print()
    print("Создайте репозиторий вручную:")
    print(f"1. Зайдите на https://github.com/new")
    print(f"2. Название: {repo_name}")
    print(f"3. Не добавляйте README, .gitignore, license")
    print(f"4. Нажмите 'Create repository'")
    print()
    print("Затем выполните:")
    print(f"git push -u origin main")
    sys.exit(0)

print("[OK] Токен получен")
print()

# Шаг 2: Проверяем, существует ли репозиторий
print("[2] Проверка существования репозитория...")
print("-" * 70)

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}

try:
    response = requests.get(
        f"https://api.github.com/repos/{username}/{repo_name}",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        print(f"[OK] Репозиторий уже существует: {repo_url}")
        repo_exists = True
    elif response.status_code == 404:
        print("[INFO] Репозиторий не найден. Создаю...")
        repo_exists = False
    else:
        print(f"[ERROR] Ошибка при проверке: {response.status_code}")
        print(f"Ответ: {response.text[:200]}")
        sys.exit(1)
except Exception as e:
    print(f"[ERROR] Ошибка подключения: {e}")
    sys.exit(1)

print()

# Шаг 3: Создаем репозиторий (если не существует)
if not repo_exists:
    print("[3] Создание репозитория...")
    print("-" * 70)
    
    data = {
        "name": repo_name,
        "description": "AI Agent для работы с локальными моделями (LM Studio, Ollama) - заебца проект",
        "private": False,
        "auto_init": False  # Не создаем README, у нас уже есть
    }
    
    try:
        response = requests.post(
            "https://api.github.com/user/repos",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 201:
            print(f"[OK] Репозиторий создан: {repo_url}")
        else:
            print(f"[ERROR] Не удалось создать репозиторий: {response.status_code}")
            print(f"Ответ: {response.text[:200]}")
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Ошибка при создании: {e}")
        sys.exit(1)
    
    print()

# Шаг 4: Проверяем remote
print("[4] Проверка remote...")
print("-" * 70)

try:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        current_url = result.stdout.strip()
        if current_url == repo_url or current_url == f"{repo_url}.git":
            print(f"[OK] Remote уже настроен: {current_url}")
        else:
            print(f"[INFO] Обновляю remote...")
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], check=True)
            print(f"[OK] Remote обновлен: {repo_url}")
    else:
        print("[INFO] Добавляю remote...")
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        print(f"[OK] Remote добавлен: {repo_url}")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Ошибка при настройке remote: {e}")
    sys.exit(1)

print()

# Шаг 5: Пуш кода
print("[5] Пуш кода в репозиторий...")
print("-" * 70)

# Настраиваем credential helper для использования токена
try:
    # Используем токен в URL для аутентификации
    auth_url = repo_url.replace("https://", f"https://{token}@")
    subprocess.run(["git", "remote", "set-url", "origin", auth_url], check=True)
    
    print("Отправляю код...")
    result = subprocess.run(
        ["git", "push", "-u", "origin", "main"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode == 0:
        print()
        print("=" * 70)
        print("[SUCCESS] КОД УСПЕШНО ЗАПУШЕН!")
        print("=" * 70)
        print()
        print(f"Репозиторий: {repo_url}")
        print()
        print("Все готово! Проект доступен на GitHub.")
    else:
        print()
        print("[ERROR] Ошибка при пуше:")
        print(result.stderr)
        print()
        print("Попробуйте вручную:")
        print(f"git push -u origin main")
        print()
        print("При запросе:")
        print(f"Username: {username}")
        print("Password: вставьте токен")
        
except subprocess.CalledProcessError as e:
    print(f"[ERROR] Ошибка: {e}")
    print()
    print("Попробуйте вручную:")
    print(f"git push -u origin main")

print()

