@echo off
REM Скрипт быстрого запуска AI Code Agent для Windows

echo ========================================
echo   AI Code Agent - Быстрый запуск
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python 3.9+ с https://www.python.org
    pause
    exit /b 1
)

REM Проверка Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Ollama не найден!
    echo Установите Ollama с https://ollama.ai
    echo.
)

echo Выберите режим запуска:
echo 1. CLI интерфейс (рекомендуется)
echo 2. Веб-интерфейс
echo 3. Установка зависимостей
echo 4. Проверка системы
echo.
set /p choice="Ваш выбор (1-4): "

if "%choice%"=="1" (
    echo.
    echo Запуск CLI интерфейса...
    python cli.py
) else if "%choice%"=="2" (
    echo.
    echo Запуск веб-интерфейса...
    echo Откройте браузер: http://127.0.0.1:8000
    python web_ui.py
) else if "%choice%"=="3" (
    echo.
    echo Установка зависимостей...
    pip install -r requirements.txt
    echo.
    echo Готово! Теперь запустите скрипт снова.
    pause
) else if "%choice%"=="4" (
    echo.
    python setup.py
    pause
) else (
    echo Неверный выбор!
    pause
)

