# Wait for repository creation and push
Write-Host "Waiting for repository creation..." -ForegroundColor Yellow
Write-Host "After creating repository on GitHub, press any key to continue..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Pushing code..." -ForegroundColor Green
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS! Code pushed!" -ForegroundColor Green
    Write-Host "Repository: https://github.com/redbleach5/experimento" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "Push failed. Make sure:" -ForegroundColor Yellow
    Write-Host "1. Repository is created" -ForegroundColor Yellow
    Write-Host "2. You have access" -ForegroundColor Yellow
    Write-Host "3. Credentials are correct" -ForegroundColor Yellow
}

