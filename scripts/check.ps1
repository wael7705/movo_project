#!/usr/bin/env pwsh
# System Health Check

Write-Host "Starting system health check..." -ForegroundColor Cyan

# 1. Check containers
Write-Host "`nChecking containers..." -ForegroundColor Yellow
try {
    $containers = docker compose ps --format json | ConvertFrom-Json
    $running = $containers | Where-Object { $_.State -eq "running" }
    $total = $containers.Count
    $runningCount = $running.Count
    
    Write-Host "Containers: $runningCount/$total running" -ForegroundColor Green
    
    if ($runningCount -lt $total) {
        Write-Host "Warning: Some containers not running" -ForegroundColor Red
        $containers | Where-Object { $_.State -ne "running" } | ForEach-Object {
            Write-Host "  - $($_.Name): $($_.State)" -ForegroundColor Red
        }
    }
} catch {
    Write-Host "Error checking containers: $_" -ForegroundColor Red
}

# 2. Check API
Write-Host "`nChecking API..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "API is working" -ForegroundColor Green
    } else {
        Write-Host "API status: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "API not working: $_" -ForegroundColor Red
}

# 3. Check database
Write-Host "`nChecking database..." -ForegroundColor Yellow
try {
    $dbCheck = docker compose exec -T db psql -U postgres -d movo_system -c "SELECT 1;" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Database connected" -ForegroundColor Green
    } else {
        Write-Host "Database issue" -ForegroundColor Red
    }
} catch {
    Write-Host "Error checking database: $_" -ForegroundColor Red
}

# 4. Check Redis
Write-Host "`nChecking Redis..." -ForegroundColor Yellow
try {
    $redisCheck = docker compose exec -T redis redis-cli ping 2>$null
    if ($redisCheck -eq "PONG") {
        Write-Host "Redis is working" -ForegroundColor Green
    } else {
        Write-Host "Redis not responding" -ForegroundColor Red
    }
} catch {
    Write-Host "Error checking Redis: $_" -ForegroundColor Red
}

# 5. Check frontend
Write-Host "`nChecking frontend..." -ForegroundColor Yellow
try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
    if ($frontendCheck.StatusCode -eq 200) {
        Write-Host "Frontend is working" -ForegroundColor Green
    } else {
        Write-Host "Frontend status: $($frontendCheck.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Frontend not working: $_" -ForegroundColor Red
}

Write-Host "`nHealth check completed" -ForegroundColor Green