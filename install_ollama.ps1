# Скрипт установки Ollama для Windows
# Запустите от имени администратора: powershell -ExecutionPolicy Bypass -File install_ollama.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Установка Ollama для AI Code Agent" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка прав администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "⚠ Предупреждение: Рекомендуется запустить от имени администратора" -ForegroundColor Yellow
}

# URL для скачивания Ollama
$ollamaUrl = "https://ollama.ai/download/windows"
$downloadPath = "$env:TEMP\ollama-windows-amd64.exe"

Write-Host "📥 Скачивание Ollama..." -ForegroundColor Yellow
Write-Host "Пожалуйста, скачайте Ollama вручную с: $ollamaUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Или используйте winget (если установлен):" -ForegroundColor Cyan
Write-Host "  winget install Ollama.Ollama" -ForegroundColor Green
Write-Host ""

# Попытка установки через winget
$wingetAvailable = Get-Command winget -ErrorAction SilentlyContinue
if ($wingetAvailable) {
    Write-Host "Обнаружен winget. Установить Ollama через winget? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Установка через winget..." -ForegroundColor Cyan
        winget install Ollama.Ollama
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Ollama успешно установлен!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Следующие шаги:" -ForegroundColor Cyan
            Write-Host "1. Перезапустите терминал" -ForegroundColor Yellow
            Write-Host "2. Запустите: ollama pull deepseek-coder:6.7b" -ForegroundColor Yellow
            Write-Host "3. Запустите GUI: python gui.py" -ForegroundColor Yellow
            exit 0
        }
    }
}

Write-Host ""
Write-Host "Ручная установка:" -ForegroundColor Cyan
Write-Host "1. Откройте браузер: $ollamaUrl" -ForegroundColor Yellow
Write-Host "2. Скачайте и установите Ollama" -ForegroundColor Yellow
Write-Host "3. После установки запустите: ollama pull deepseek-coder:6.7b" -ForegroundColor Yellow
Write-Host "4. Запустите GUI: python gui.py" -ForegroundColor Yellow
Write-Host ""

# Открытие браузера
Write-Host "Открыть страницу загрузки в браузере? (Y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    Start-Process $ollamaUrl
}

Write-Host ""
Write-Host "Нажмите любую клавишу для выхода..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

