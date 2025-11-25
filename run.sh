#!/bin/bash
# Скрипт быстрого запуска AI Code Agent для Linux/Mac

echo "========================================"
echo "  AI Code Agent - Быстрый запуск"
echo "========================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "[ОШИБКА] Python3 не найден!"
    echo "Установите Python 3.9+"
    exit 1
fi

# Проверка Ollama
if ! command -v ollama &> /dev/null; then
    echo "[ПРЕДУПРЕЖДЕНИЕ] Ollama не найден!"
    echo "Установите Ollama с https://ollama.ai"
    echo ""
fi

echo "Выберите режим запуска:"
echo "1. CLI интерфейс (рекомендуется)"
echo "2. Веб-интерфейс"
echo "3. Установка зависимостей"
echo "4. Проверка системы"
echo ""
read -p "Ваш выбор (1-4): " choice

case $choice in
    1)
        echo ""
        echo "Запуск CLI интерфейса..."
        python3 cli.py
        ;;
    2)
        echo ""
        echo "Запуск веб-интерфейса..."
        echo "Откройте браузер: http://127.0.0.1:8000"
        python3 web_ui.py
        ;;
    3)
        echo ""
        echo "Установка зависимостей..."
        pip3 install -r requirements.txt
        echo ""
        echo "Готово! Теперь запустите скрипт снова."
        ;;
    4)
        echo ""
        python3 setup.py
        ;;
    *)
        echo "Неверный выбор!"
        exit 1
        ;;
esac

