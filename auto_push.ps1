# Автоматический пуш в Git
# Создает репозиторий на GitHub и пушит код

Write-Host "=== АВТОМАТИЧЕСКИЙ ПУШ В GIT ===" -ForegroundColor Cyan
Write-Host ""

# Проверяем GitHub CLI
$ghInstalled = Get-Command gh -ErrorAction SilentlyContinue
if ($ghInstalled) {
    Write-Host "[OK] GitHub CLI установлен" -ForegroundColor Green
    
    # Проверяем авторизацию
    $ghAuth = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Авторизован в GitHub" -ForegroundColor Green
        Write-Host ""
        
        $repoName = "zaebca"
        Write-Host "Создаю репозиторий: $repoName" -ForegroundColor Yellow
        
        # Создаем репозиторий
        gh repo create $repoName --public --source=. --remote=origin --push
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "=== УСПЕХ! Репозиторий создан и код запушен! ===" -ForegroundColor Green
            Write-Host "URL: https://github.com/$(gh api user --jq .login)/$repoName" -ForegroundColor Cyan
        } else {
            Write-Host "[ERROR] Не удалось создать репозиторий" -ForegroundColor Red
            Write-Host "Попробуйте вручную:" -ForegroundColor Yellow
            Write-Host "1. Создайте репозиторий на GitHub"
            Write-Host "2. Запустите: git remote add origin https://github.com/USERNAME/zaebca.git"
            Write-Host "3. Запустите: git push -u origin main"
        }
    } else {
        Write-Host "[WARNING] Не авторизован в GitHub" -ForegroundColor Yellow
        Write-Host "Выполните: gh auth login" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Или создайте репозиторий вручную и запустите:" -ForegroundColor Yellow
        Write-Host "git remote add origin https://github.com/USERNAME/zaebca.git"
        Write-Host "git push -u origin main"
    }
} else {
    Write-Host "[INFO] GitHub CLI не установлен" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Создайте репозиторий вручную:" -ForegroundColor Yellow
    Write-Host "1. Зайдите на https://github.com/new"
    Write-Host "2. Название: zaebca"
    Write-Host "3. НЕ добавляйте README, .gitignore, лицензию"
    Write-Host "4. Нажмите 'Create repository'"
    Write-Host ""
    Write-Host "Затем выполните:" -ForegroundColor Cyan
    Write-Host "git remote add origin https://github.com/USERNAME/zaebca.git"
    Write-Host "git push -u origin main"
}

