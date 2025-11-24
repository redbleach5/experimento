# Simple push script
param([string]$Token = "")

$repoName = "experimento"
$username = "redbleach5"
$repoUrl = "https://github.com/$username/$repoName"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AUTOMATIC PUSH TO GITHUB" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not $Token) {
    Write-Host "Enter GitHub Personal Access Token:" -ForegroundColor Yellow
    Write-Host "(Get it here: https://github.com/settings/tokens)" -ForegroundColor Gray
    Write-Host ""
    $Token = Read-Host "Token"
}

if (-not $Token) {
    Write-Host "[ERROR] Token not provided!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[1/4] Checking repository..." -ForegroundColor Cyan

$headers = @{
    "Authorization" = "token $Token"
    "Accept" = "application/vnd.github.v3+json"
}

try {
    $response = Invoke-RestMethod -Uri "https://api.github.com/repos/$username/$repoName" -Headers $headers -Method Get -ErrorAction SilentlyContinue
    Write-Host "  [OK] Repository exists" -ForegroundColor Green
    $repoExists = $true
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "  [INFO] Repository not found, creating..." -ForegroundColor Yellow
        $repoExists = $false
    } else {
        Write-Host "  [ERROR] Error: $_" -ForegroundColor Red
        exit 1
    }
}

if (-not $repoExists) {
    Write-Host "[2/4] Creating repository..." -ForegroundColor Cyan
    
    $body = @{
        name = $repoName
        description = "AI Agent for local models (LM Studio, Ollama)"
        private = $false
        auto_init = $false
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body -ContentType "application/json"
        Write-Host "  [OK] Repository created!" -ForegroundColor Green
    } catch {
        Write-Host "  [ERROR] Failed to create: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[2/4] Repository exists, skipping" -ForegroundColor Gray
}

Write-Host "[3/4] Setting up remote..." -ForegroundColor Cyan
$repoUrlWithGit = $repoUrl + '.git'
$currentRemote = git remote get-url origin 2>$null

if (-not $currentRemote -or $currentRemote -ne $repoUrlWithGit) {
    if ($currentRemote) {
        git remote set-url origin $repoUrlWithGit
    } else {
        git remote add origin $repoUrlWithGit
    }
    Write-Host "  [OK] Remote configured" -ForegroundColor Green
} else {
    Write-Host "  [OK] Remote already configured" -ForegroundColor Green
}

Write-Host "[4/4] Pushing code..." -ForegroundColor Cyan

$authUrl = 'https://' + $Token + '@github.com/' + $username + '/' + $repoName + '.git'
git remote set-url origin $authUrl

try {
    $output = git push -u origin main 2>&1 | Out-String
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  SUCCESS! CODE PUSHED!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Repository: $repoUrl" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "All done!" -ForegroundColor Green
    } else {
        Write-Host "  [ERROR] Push failed" -ForegroundColor Red
        Write-Host $output
        Write-Host ""
        Write-Host "Try manually: git push -u origin main" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [ERROR] Error: $_" -ForegroundColor Red
}

git remote set-url origin $repoUrlWithGit

Write-Host ""

