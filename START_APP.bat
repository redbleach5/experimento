@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   AI Code Agent - Запуск приложения
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    pause
    exit /b 1
)

echo [*] Запуск GUI интерфейса...
echo.
echo Инструкция:
echo 1. В GUI выберите провайдер "lmstudio"
echo 2. Нажмите "Обновить список моделей"
echo 3. Выберите модель qwen3-30b-a3b-instruct-2507
echo 4. Отправьте тестовый запрос
echo.

python gui.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось запустить приложение
    pause
)

