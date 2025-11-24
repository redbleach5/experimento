@echo off
chcp 65001 >nul
echo ========================================
echo   ФИНАЛЬНЫЙ ПУШ В GITHUB
echo ========================================
echo.

echo [СТАТУС]
git status --short
echo.

echo [КОММИТЫ]
git log --oneline -4
echo.

echo [REMOTE]
git remote -v
echo.

echo ========================================
echo.
echo Репозиторий: https://github.com/redbleach5/experimento
echo.
echo Если репозиторий создан, нажмите любую клавишу для пуша...
pause >nul

echo.
echo Отправляю код...
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   УСПЕХ! КОД ЗАПУШЕН!
    echo ========================================
    echo.
    echo Репозиторий: https://github.com/redbleach5/experimento
) else (
    echo.
    echo [ОШИБКА] Не удалось запушить
    echo.
    echo Возможные причины:
    echo 1. Репозиторий не создан - создайте на https://github.com/new
    echo 2. Нужна аутентификация - используйте токен вместо пароля
)

echo.
pause

