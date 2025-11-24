@echo off
chcp 65001 >nul 2>&1
echo ========================================
echo   AI Code Agent - Запуск с LM Studio
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    pause
    exit /b 1
)

echo [*] Проверка LM Studio...
python -c "import requests; r = requests.get('http://localhost:1234/v1/models', timeout=3); print('[OK] LM Studio доступен!' if r.status_code == 200 else '[!] LM Studio не доступен (статус: ' + str(r.status_code) + ')')" 2>nul

if errorlevel 1 (
    echo.
    echo [!] LM Studio не запущен или сервер не включен!
    echo.
    echo Инструкция:
    echo 1. Установите LM Studio: https://lmstudio.ai
    echo 2. Запустите LM Studio
    echo 3. Перейдите в Settings -^> Local Server
    echo 4. Включите "Local Server"
    echo 5. Нажмите "Start Server"
    echo 6. Загрузите модель в разделе Chat
    echo.
    echo Продолжить запуск GUI? (Y/N)
    set /p continue="> "
    if /i not "%continue%"=="Y" (
        exit /b 1
    )
)

echo.
echo [*] Запуск GUI интерфейса...
echo.
echo В GUI выберите провайдер "lmstudio" в боковой панели
echo.

python gui.py

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось запустить GUI
    pause
)

