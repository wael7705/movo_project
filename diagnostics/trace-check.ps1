# Comprehensive System Diagnostics Script
# Usage: powershell -ExecutionPolicy Bypass -File .\diagnostics\trace-check.ps1

Write-Host "Starting comprehensive system diagnostics..." -ForegroundColor Cyan

# 1) Next Button
Write-Host "`nChecking Next Button" -ForegroundColor Yellow
try { 
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/next" -Method GET -UseBasicParsing
    Write-Host "Next Button OK - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch { 
    Write-Host "Next Button Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 2) Orders Count
Write-Host "`nChecking Orders Count" -ForegroundColor Yellow
try { 
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/counts" -Method GET -UseBasicParsing
    Write-Host "Orders Count OK - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch { 
    Write-Host "Orders Count Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 3) Rating Button
Write-Host "`nChecking Rating Button" -ForegroundColor Yellow
try { 
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/1/rating" -Method GET -UseBasicParsing
    Write-Host "Rating Button OK - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch { 
    Write-Host "Rating Button Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 4) Notes Button
Write-Host "`nChecking Notes Button" -ForegroundColor Yellow
try { 
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/1/notes" -Method GET -UseBasicParsing
    Write-Host "Notes Button OK - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch { 
    Write-Host "Notes Button Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 5) Captain Assignment
Write-Host "`nChecking Captain Assignment" -ForegroundColor Yellow
try { 
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/assign/orders/1/candidates" -Method GET -UseBasicParsing
    Write-Host "Captain Assignment OK - Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)" -ForegroundColor White
} catch { 
    Write-Host "Captain Assignment Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 6) Container Status
Write-Host "`nChecking Container Status" -ForegroundColor Yellow
try {
    $containers = docker compose ps
    Write-Host "Container Status:" -ForegroundColor Green
    Write-Host $containers -ForegroundColor White
} catch { 
    Write-Host "Container Check Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 7) Worker Status
Write-Host "`nChecking Worker Status" -ForegroundColor Yellow
try {
    $workers = docker compose logs app | Select-String "Booting worker" | Select-Object -Last 16
    Write-Host "Active Workers:" -ForegroundColor Green
    $workers | ForEach-Object { Write-Host $_.Line -ForegroundColor White }
} catch { 
    Write-Host "Worker Check Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 8) WebSocket Status
Write-Host "`nChecking WebSocket Status" -ForegroundColor Yellow
try {
    $websocketLogs = docker compose logs app | Select-String "WebSocket" | Select-Object -Last 5
    if ($websocketLogs) {
        Write-Host "WebSocket Active:" -ForegroundColor Green
        $websocketLogs | ForEach-Object { Write-Host $_.Line -ForegroundColor White }
    } else {
        Write-Host "No recent WebSocket messages" -ForegroundColor Yellow
    }
} catch { 
    Write-Host "WebSocket Check Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 9) Database Status
Write-Host "`nChecking Database Status" -ForegroundColor Yellow
try {
    $dbCheck = docker compose exec -T db psql -U postgres -d movo_system -c "SELECT COUNT(*) as total_orders FROM orders;" 2>$null
    if ($dbCheck) {
        Write-Host "Database Connected" -ForegroundColor Green
        Write-Host "Orders Count: $($dbCheck -split '\n' | Where-Object { $_ -match '\d+' } | Select-Object -First 1)" -ForegroundColor White
    } else {
        Write-Host "Database Connection Error" -ForegroundColor Red
    }
} catch { 
    Write-Host "Database Check Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 10) Redis Status
Write-Host "`nChecking Redis Status" -ForegroundColor Yellow
try {
    $redisCheck = docker compose exec -T redis redis-cli ping 2>$null
    if ($redisCheck -eq "PONG") {
        Write-Host "Redis Connected and Working" -ForegroundColor Green
    } else {
        Write-Host "Redis Not Connected" -ForegroundColor Red
    }
} catch { 
    Write-Host "Redis Check Error: $($_.Exception.Message)" -ForegroundColor Red 
}

# 11) Grafana Status
Write-Host "`nChecking Grafana Status" -ForegroundColor Yellow
try { 
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method GET -UseBasicParsing
    Write-Host "Grafana Working - Status: $($response.StatusCode)" -ForegroundColor Green
} catch { 
    Write-Host "Grafana Error: $($_.Exception.Message)" -ForegroundColor Red 
}

Write-Host "`nComprehensive diagnostics completed. Check outputs above." -ForegroundColor Green
Write-Host "`nSystem Summary:" -ForegroundColor Cyan
Write-Host "   - 4 application containers with 4 workers each (16 total workers)" -ForegroundColor White
Write-Host "   - Hybrid uvicorn + gunicorn system with async support" -ForegroundColor White
Write-Host "   - nginx load balancing" -ForegroundColor White
Write-Host "   - PostgreSQL + PgBouncer + Redis + Grafana" -ForegroundColor White
