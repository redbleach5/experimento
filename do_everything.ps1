# Do everything automatically
$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTOMATIC REPOSITORY CREATION & PUSH" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$repoName = "experimento"
$username = "redbleach5"
$repoUrl = "https://github.com/$username/$repoName"

# Method 1: Try GitHub CLI
Write-Host "[1] Trying GitHub CLI..." -ForegroundColor Yellow
$ghPath = Get-Command gh -ErrorAction SilentlyContinue
if ($ghPath) {
    Write-Host "  GitHub CLI found!" -ForegroundColor Green
    
    # Check auth
    $ghAuth = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  Authenticated!" -ForegroundColor Green
        
        # Create repo
        Write-Host "  Creating repository..." -ForegroundColor Cyan
        gh repo create $repoName --public --source=. --remote=origin --push 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  SUCCESS! REPOSITORY CREATED & PUSHED!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Repository: $repoUrl" -ForegroundColor Cyan
            exit 0
        }
    } else {
        Write-Host "  Not authenticated. Skipping..." -ForegroundColor Yellow
    }
} else {
    Write-Host "  GitHub CLI not found. Skipping..." -ForegroundColor Yellow
}

Write-Host ""

# Method 2: Check if repo exists and push
Write-Host "[2] Checking if repository exists..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $repoUrl -Method Head -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "  Repository exists!" -ForegroundColor Green
        Write-Host "  Pushing code..." -ForegroundColor Cyan
        
        git push -u origin main 2>&1 | Out-String
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "  SUCCESS! CODE PUSHED!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Repository: $repoUrl" -ForegroundColor Cyan
            exit 0
        }
    }
} catch {
    Write-Host "  Repository not found" -ForegroundColor Yellow
}

Write-Host ""

# Method 3: Open creation page and wait
Write-Host "[3] Opening repository creation page..." -ForegroundColor Yellow
Start-Process "https://github.com/new?name=$repoName&description=AI+Agent"

Write-Host "  Page opened!" -ForegroundColor Green
Write-Host ""
Write-Host "Waiting for repository creation..." -ForegroundColor Cyan
Write-Host "Checking every 5 seconds (max 2 minutes)..." -ForegroundColor Gray
Write-Host ""

for ($i = 1; $i -le 24; $i++) {
    Start-Sleep -Seconds 5
    Write-Host "[$i/24] Checking... " -ForegroundColor Gray -NoNewline
    
    try {
        $response = Invoke-WebRequest -Uri $repoUrl -Method Head -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "FOUND!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Pushing code..." -ForegroundColor Cyan
            
            git push -u origin main 2>&1 | Out-String
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "========================================" -ForegroundColor Green
                Write-Host "  SUCCESS! CODE PUSHED!" -ForegroundColor Green
                Write-Host "========================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "Repository: $repoUrl" -ForegroundColor Cyan
                exit 0
            } else {
                Write-Host "[ERROR] Push failed" -ForegroundColor Red
                Write-Host "Try manually: git push -u origin main" -ForegroundColor Yellow
                exit 1
            }
        } else {
            Write-Host "not found" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "not found" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[TIMEOUT] Repository not created" -ForegroundColor Red
Write-Host "Create it manually and run: git push -u origin main" -ForegroundColor Yellow

