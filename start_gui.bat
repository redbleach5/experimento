@echo off
REM Быстрый запуск GUI интерфейса

echo ========================================
echo   AI Code Agent - GUI Запуск
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    pause
    exit /b 1
)

REM Проверка Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Ollama не найден!
    echo.
    echo Установите Ollama:
    echo 1. Запустите: install_ollama.ps1
    echo 2. Или скачайте с: https://ollama.ai
    echo.
    echo Продолжить без Ollama? (Y/N)
    set /p continue="> "
    if /i not "%continue%"=="Y" (
        exit /b 1
    )
)

echo Запуск GUI интерфейса...
echo.

python gui.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось запустить GUI
    echo Проверьте, что все зависимости установлены: pip install -r requirements.txt
    pause
)

