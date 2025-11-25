# Быстрый пуш в Git - просто введите URL репозитория

Write-Host "=== БЫСТРЫЙ ПУШ В GIT ===" -ForegroundColor Cyan
Write-Host ""

# Проверяем текущий статус
Write-Host "Текущий статус:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Проверяем remote
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "Найден remote: $remote" -ForegroundColor Green
    $use = Read-Host "Использовать этот remote? (y/n)"
    if ($use -eq "y" -or $use -eq "Y") {
        Write-Host ""
        Write-Host "Пушим..." -ForegroundColor Cyan
        git push -u origin main
        exit 0
    }
}

# Запрашиваем URL
Write-Host "Введите URL репозитория:" -ForegroundColor Yellow
Write-Host "Пример: https://github.com/USERNAME/zaebca.git" -ForegroundColor Gray
$url = Read-Host "URL"

if (-not $url) {
    Write-Host "Ошибка: URL не указан!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Добавляю remote и пушу..." -ForegroundColor Cyan

# Удаляем старый remote если есть
git remote remove origin 2>$null

# Добавляем новый
git remote add origin $url

# Пушим
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== УСПЕХ! Код запушен! ===" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== ОШИБКА ===" -ForegroundColor Red
    Write-Host "Убедитесь что:" -ForegroundColor Yellow
    Write-Host "1. Репозиторий создан на GitHub/GitLab"
    Write-Host "2. URL правильный"
    Write-Host "3. У вас есть права на запись"
}

