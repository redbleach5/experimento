@echo off
REM Скрипт для установки модели Ollama

echo ========================================
echo   Установка модели для AI Code Agent
echo ========================================
echo.

REM Проверка Ollama
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Ollama не найден!
    echo Установите Ollama сначала: https://ollama.ai
    echo Или запустите: install_ollama.ps1
    pause
    exit /b 1
)

echo Доступные модели для кодирования:
echo 1. deepseek-coder:6.7b (рекомендуется для RTX 3090)
echo 2. codellama:13b (лучше качество, больше памяти)
echo 3. codellama:7b (быстрее)
echo 4. qwen2.5-coder:7b (современная)
echo 5. starcoder2:7b (специализированная)
echo.
set /p choice="Выберите модель (1-5): "

if "%choice%"=="1" (
    set model=deepseek-coder:6.7b
) else if "%choice%"=="2" (
    set model=codellama:13b
) else if "%choice%"=="3" (
    set model=codellama:7b
) else if "%choice%"=="4" (
    set model=qwen2.5-coder:7b
) else if "%choice%"=="5" (
    set model=starcoder2:7b
) else (
    echo Неверный выбор, используем deepseek-coder:6.7b
    set model=deepseek-coder:6.7b
)

echo.
echo Установка модели: %model%
echo Это может занять несколько минут и потребует ~4-7 GB места...
echo.

ollama pull %model%

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Не удалось установить модель
    pause
    exit /b 1
) else (
    echo.
    echo [УСПЕХ] Модель %model% успешно установлена!
    echo Теперь можно запустить GUI: python gui.py
    echo.
    pause
)

