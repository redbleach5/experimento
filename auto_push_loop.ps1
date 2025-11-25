# Auto push loop - checks and pushes automatically
$repoUrl = "https://github.com/redbleach5/experimento"
$maxAttempts = 30
$delaySeconds = 10

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTOMATIC PUSH - WAITING FOR REPO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: $repoUrl" -ForegroundColor Yellow
Write-Host "Checking every $delaySeconds seconds..." -ForegroundColor Gray
Write-Host "Max attempts: $maxAttempts" -ForegroundColor Gray
Write-Host ""
Write-Host "Create repository at: https://github.com/new" -ForegroundColor Cyan
Write-Host "Name: experimento" -ForegroundColor Cyan
Write-Host "DO NOT add README, .gitignore, license" -ForegroundColor Cyan
Write-Host ""
Write-Host "Waiting for repository creation..." -ForegroundColor Yellow
Write-Host ""

for ($i = 1; $i -le $maxAttempts; $i++) {
    Write-Host "[$i/$maxAttempts] Checking..." -ForegroundColor Gray -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $repoUrl -Method Head -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host " FOUND!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Repository exists! Pushing code..." -ForegroundColor Green
            Write-Host ""
            
            git push -u origin main
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Green
                Write-Host "  SUCCESS! CODE PUSHED!" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "Repository: $repoUrl" -ForegroundColor Cyan
                exit 0
            } else {
                Write-Host ""
                Write-Host "[ERROR] Push failed. May need authentication." -ForegroundColor Red
                Write-Host "Try manually: git push -u origin main" -ForegroundColor Yellow
                exit 1
            }
        }
    } catch {
        Write-Host " Not found" -ForegroundColor Yellow
    }
    
    if ($i -lt $maxAttempts) {
        Start-Sleep -Seconds $delaySeconds
    }
}

Write-Host ""
Write-Host "[TIMEOUT] Repository not created after $maxAttempts attempts" -ForegroundColor Red
Write-Host "Create it manually at: https://github.com/new" -ForegroundColor Yellow
Write-Host "Then run: git push -u origin main" -ForegroundColor Yellow

