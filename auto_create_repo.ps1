# Автоматическое создание репозитория и пуш
# Использование: $env:GITHUB_TOKEN="ваш_токен"; .\auto_create_repo.ps1

$repoName = "experimento"
$username = "redbleach5"
$repoUrl = "https://github.com/$username/$repoName"

Write-Host "=== АВТОМАТИЧЕСКОЕ СОЗДАНИЕ РЕПОЗИТОРИЯ ===" -ForegroundColor Cyan
Write-Host ""

# Получаем токен
$token = $env:GITHUB_TOKEN

if (-not $token) {
    Write-Host "[INFO] Токен не найден в переменных окружения" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Для автоматического создания нужен GitHub токен." -ForegroundColor Yellow
    Write-Host "Получите его: https://github.com/settings/tokens" -ForegroundColor Yellow
    Write-Host ""
    $token = Read-Host "Введите токен (или нажмите Enter для пропуска)"
}

if (-not $token) {
    Write-Host ""
    Write-Host "[SKIP] Токен не указан. Создайте репозиторий вручную:" -ForegroundColor Yellow
    Write-Host "1. https://github.com/new" -ForegroundColor Cyan
    Write-Host "2. Название: $repoName" -ForegroundColor Cyan
    Write-Host "3. Не добавляйте README, .gitignore, license" -ForegroundColor Cyan
    Write-Host "4. Нажмите 'Create repository'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Затем выполните: git push -u origin main" -ForegroundColor Green
    exit 0
}

Write-Host "[OK] Токен получен" -ForegroundColor Green
Write-Host ""

# Проверяем существование репозитория
Write-Host "[1] Проверка репозитория..." -ForegroundColor Cyan
$headers = @{
    "Authorization" = "token $token"
    "Accept" = "application/vnd.github.v3+json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$username/$repoName" -Headers $headers -Method Get -ErrorAction SilentlyContinue
    Write-Host "[OK] Репозиторий уже существует" -ForegroundColor Green
    $repoExists = $true
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "[INFO] Репозиторий не найден. Создаю..." -ForegroundColor Yellow
        $repoExists = $false
    } else {
        Write-Host "[ERROR] Ошибка при проверке: $_" -ForegroundColor Red
        exit 1
    }
}

# Создаем репозиторий
if (-not $repoExists) {
    Write-Host "[2] Создание репозитория..." -ForegroundColor Cyan
    
    $body = @{
        name = $repoName
        description = "AI Agent для работы с локальными моделями (LM Studio, Ollama) - заебца проект"
        private = $false
        auto_init = $false
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body -ContentType "application/json"
        Write-Host "[OK] Репозиторий создан: $repoUrl" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Не удалось создать репозиторий: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Настраиваем remote
Write-Host "[3] Настройка remote..." -ForegroundColor Cyan
$currentRemote = git remote get-url origin 2>$null

if ($currentRemote) {
    if ($currentRemote -eq $repoUrl -or $currentRemote -eq "$repoUrl.git") {
        Write-Host "[OK] Remote уже настроен" -ForegroundColor Green
    } else {
        git remote set-url origin $repoUrl
        Write-Host "[OK] Remote обновлен" -ForegroundColor Green
    }
} else {
    git remote add origin $repoUrl
    Write-Host "[OK] Remote добавлен" -ForegroundColor Green
}

Write-Host ""

# Пуш с токеном
Write-Host "[4] Пуш кода..." -ForegroundColor Cyan

# Используем токен в URL
$authUrl = $repoUrl -replace "https://", "https://${token}@"
git remote set-url origin $authUrl

try {
    git push -u origin main 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "[SUCCESS] КОД УСПЕШНО ЗАПУШЕН!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Репозиторий: $repoUrl" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Все готово! Проект доступен на GitHub." -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[ERROR] Ошибка при пуше" -ForegroundColor Red
        Write-Host "Попробуйте вручную: git push -u origin main" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[ERROR] Ошибка: $_" -ForegroundColor Red
}

# Возвращаем обычный URL
git remote set-url origin $repoUrl

Write-Host ""

