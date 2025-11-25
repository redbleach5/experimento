# Check status and push
Clear-Host

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CHECK AND PUSH TO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check status
Write-Host "[REPOSITORY STATUS]" -ForegroundColor Yellow
Write-Host "-------------------" -ForegroundColor Gray
git status --short
Write-Host ""

Write-Host "[COMMITS]" -ForegroundColor Yellow
Write-Host "--------" -ForegroundColor Gray
git log --oneline -5
Write-Host ""

Write-Host "[REMOTE]" -ForegroundColor Yellow
Write-Host "-------" -ForegroundColor Gray
git remote -v
Write-Host ""

# Check repository existence
Write-Host "[CHECKING GITHUB REPOSITORY]" -ForegroundColor Yellow
Write-Host "----------------------------" -ForegroundColor Gray
$repoUrl = "https://github.com/redbleach5/experimento"
Write-Host "URL: $repoUrl" -ForegroundColor Cyan

$repoExists = $false
try {
    $response = Invoke-WebRequest -Uri $repoUrl -Method Head -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Repository exists!" -ForegroundColor Green
        $repoExists = $true
    }
} catch {
    Write-Host "[INFO] Repository not found or not accessible" -ForegroundColor Yellow
    Write-Host "      Create it at: https://github.com/new" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Menu
if ($repoExists) {
    Write-Host "Repository is ready for push!" -ForegroundColor Green
    Write-Host ""
    $choice = Read-Host "Push code? (y/n)"
    
    if ($choice -eq "y" -or $choice -eq "Y") {
        Write-Host ""
        Write-Host "Pushing code..." -ForegroundColor Cyan
        git push -u origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  SUCCESS! CODE PUSHED!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Repository: $repoUrl" -ForegroundColor Cyan
        } else {
            Write-Host ""
            Write-Host "[ERROR] Push failed" -ForegroundColor Red
            Write-Host "Authentication may be required" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "Create repository on GitHub:" -ForegroundColor Yellow
    Write-Host "1. Open: https://github.com/new" -ForegroundColor Cyan
    Write-Host "2. Name: experimento" -ForegroundColor Cyan
    Write-Host "3. DO NOT add README, .gitignore, license" -ForegroundColor Cyan
    Write-Host "4. Click 'Create repository'" -ForegroundColor Cyan
    Write-Host ""
    $choice = Read-Host "After creating, press Enter to check again"
    
    Write-Host ""
    Write-Host "Checking again..." -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri $repoUrl -Method Head -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Repository found! Pushing..." -ForegroundColor Green
            Write-Host ""
            git push -u origin main
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Green
                Write-Host "  SUCCESS! CODE PUSHED!" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Green
            }
        }
    } catch {
        Write-Host "[INFO] Repository still not created" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
