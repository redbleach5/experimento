# Скрипт для автоматического пуша в Git
# Использование: .\push_to_git.ps1 -RepoUrl "https://github.com/USERNAME/REPO.git"

param(
    [Parameter(Mandatory=$false)]
    [string]$RepoUrl = ""
)

Write-Host "=== ПУШ В GIT ===" -ForegroundColor Cyan
Write-Host ""

# Проверяем, есть ли уже remote
$existingRemote = git remote -v
if ($existingRemote) {
    Write-Host "Найден remote:" -ForegroundColor Yellow
    Write-Host $existingRemote
    Write-Host ""
    $useExisting = Read-Host "Использовать существующий? (y/n)"
    if ($useExisting -eq "y" -or $useExisting -eq "Y") {
        Write-Host "Пушим в существующий remote..." -ForegroundColor Green
        git push -u origin main
        exit 0
    }
}

# Если URL не указан, спрашиваем
if (-not $RepoUrl) {
    Write-Host "Введите URL репозитория (например: https://github.com/USERNAME/zaebca.git)" -ForegroundColor Yellow
    $RepoUrl = Read-Host "URL"
}

if (-not $RepoUrl) {
    Write-Host "Ошибка: URL не указан!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Добавляю remote: $RepoUrl" -ForegroundColor Cyan
git remote add origin $RepoUrl

if ($LASTEXITCODE -ne 0) {
    Write-Host "Пробую обновить существующий remote..." -ForegroundColor Yellow
    git remote set-url origin $RepoUrl
}

Write-Host ""
Write-Host "Пушим в репозиторий..." -ForegroundColor Green
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== УСПЕХ! Проект запушен! ===" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=== ОШИБКА ПРИ ПУШЕ ===" -ForegroundColor Red
    Write-Host "Возможные причины:" -ForegroundColor Yellow
    Write-Host "1. Репозиторий не создан на GitHub/GitLab"
    Write-Host "2. Неверный URL"
    Write-Host "3. Проблемы с аутентификацией"
    Write-Host ""
    Write-Host "Создайте репозиторий на GitHub/GitLab и попробуйте снова"
}

