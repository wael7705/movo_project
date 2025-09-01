# Quick System Check Script
# Usage: powershell -ExecutionPolicy Bypass -File .\diagnostics\quick-check.ps1

Write-Host "Quick System Check..." -ForegroundColor Cyan

# Check main API
try { 
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/counts" -Method GET -UseBasicParsing
    Write-Host "✅ API Working - Status: $($response.StatusCode)" -ForegroundColor Green
} catch { 
    Write-Host "❌ API Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# Check containers
$containers = docker compose ps --format "table {{.Name}}\t{{.Status}}"
Write-Host "`nContainer Status:" -ForegroundColor Yellow
Write-Host $containers -ForegroundColor White

# Check workers
$workerCount = (docker compose logs app | Select-String "Booting worker").Count
Write-Host "`nActive Workers: $workerCount" -ForegroundColor Green

# Check database
try {
    $dbCheck = docker compose exec -T db psql -U postgres -d movo_system -c "SELECT COUNT(*) FROM orders;" 2>$null
    if ($dbCheck) {
        Write-Host "✅ Database Connected" -ForegroundColor Green
    }
} catch { 
    Write-Host "❌ Database Error" -ForegroundColor Red 
}

# Check Redis
try {
    $redisCheck = docker compose exec -T redis redis-cli ping 2>$null
    if ($redisCheck -eq "PONG") {
        Write-Host "✅ Redis Connected" -ForegroundColor Green
    }
} catch { 
    Write-Host "❌ Redis Error" -ForegroundColor Red 
}

# Check Grafana
try { 
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -UseBasicParsing
    Write-Host "✅ Grafana Working" -ForegroundColor Green
} catch { 
    Write-Host "❌ Grafana Error" -ForegroundColor Red 
}

Write-Host "`nQuick check completed!" -ForegroundColor Green
