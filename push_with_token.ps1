# Простой скрипт для пуша с токеном
# Просто вставьте токен когда попросит

param(
    [Parameter(Mandatory=$false)]
    [string]$Token = ""
)

$repoName = "experimento"
$username = "redbleach5"
$repoUrl = "https://github.com/$username/$repoName"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  АВТОМАТИЧЕСКИЙ ПУШ В GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Получаем токен
if (-not $Token) {
    Write-Host "Введите GitHub Personal Access Token:" -ForegroundColor Yellow
    Write-Host "(Получите здесь: https://github.com/settings/tokens)" -ForegroundColor Gray
    Write-Host ""
    $Token = Read-Host "Токен" 
}

if (-not $Token) {
    Write-Host "[ERROR] Токен не указан!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[1/4] Проверяю репозиторий..." -ForegroundColor Cyan

# Проверяем существование
$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$username/$repoName" -Headers $headers -Method Get -ErrorAction SilentlyContinue
    Write-Host "  [OK] Репозиторий существует" -ForegroundColor Green
    $repoExists = $true
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "  [INFO] Репозиторий не найден, создаю..." -ForegroundColor Yellow
        $repoExists = $false
    } else {
        Write-Host "  [ERROR] Ошибка: $_" -ForegroundColor Red
        exit 1
    }
}

# Создаем если не существует
if (-not $repoExists) {
    Write-Host "[2/4] Создаю репозиторий..." -ForegroundColor Cyan
    
    $body = @{
        name = $repoName
        description = "AI Agent для работы с локальными моделями (LM Studio, Ollama)"
        private = $false
        auto_init = $false
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body -ContentType "application/json"
        Write-Host "  [OK] Репозиторий создан!" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Не удалось создать: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[2/4] Репозиторий уже существует, пропускаю" -ForegroundColor Gray
}

# Настраиваем remote
Write-Host "[3/4] Настраиваю remote..." -ForegroundColor Cyan
$currentRemote = git remote get-url origin 2>$null

if (-not $currentRemote -or $currentRemote -ne "$repoUrl.git") {
    if ($currentRemote) {
        git remote set-url origin "$repoUrl.git"
    } else {
        git remote add origin "$repoUrl.git"
    }
    Write-Host "  [OK] Remote настроен" -ForegroundColor Green
} else {
    Write-Host "  [OK] Remote уже настроен" -ForegroundColor Green
}

# Пуш с токеном
Write-Host "[4/4] Отправляю код..." -ForegroundColor Cyan

# Используем токен в URL
$authUrl = 'https://' + $Token + '@github.com/' + $username + '/' + $repoName + '.git'
git remote set-url origin $authUrl

try {
    $output = git push -u origin main 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  УСПЕХ! КОД ЗАПУШЕН!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Репозиторий: $repoUrl" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Все готово!" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Ошибка при пуше" -ForegroundColor Red
        Write-Host $output
        Write-Host ""
        Write-Host "Попробуйте вручную:" -ForegroundColor Yellow
        Write-Host "git push -u origin main" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  [ERROR] Ошибка: $_" -ForegroundColor Red
}

# Возвращаем обычный URL
$normalUrl = $repoUrl + '.git'
git remote set-url origin $normalUrl

Write-Host ""

