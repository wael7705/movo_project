# Performance Testing Script
# Usage: powershell -ExecutionPolicy Bypass -File .\diagnostics\performance-test.ps1

Write-Host "Performance Testing Script" -ForegroundColor Cyan

# Test API response times
Write-Host "`nTesting API Response Times..." -ForegroundColor Yellow

$endpoints = @(
    "http://localhost:8000/api/v1/orders/counts",
    "http://localhost:8000/api/v1/orders/1/rating",
    "http://localhost:8000/api/v1/orders/1/notes",
    "http://localhost:8000/api/v1/assign/orders/1/candidates"
)

foreach ($endpoint in $endpoints) {
    $times = @()
    for ($i = 1; $i -le 10; $i++) {
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $response = Invoke-WebRequest -Uri $endpoint -Method GET -UseBasicParsing
            $stopwatch.Stop()
            $times += $stopwatch.ElapsedMilliseconds
        } catch {
            $stopwatch.Stop()
            Write-Host "Error testing $endpoint" -ForegroundColor Red
        }
    }
    
    if ($times.Count -gt 0) {
        $avgTime = ($times | Measure-Object -Average).Average
        $minTime = ($times | Measure-Object -Minimum).Minimum
        $maxTime = ($times | Measure-Object -Maximum).Maximum
        
        Write-Host "Endpoint: $endpoint" -ForegroundColor White
        Write-Host "  Average: $([math]::Round($avgTime, 2))ms" -ForegroundColor Green
        Write-Host "  Min: $minTime ms" -ForegroundColor Green
        Write-Host "  Max: $maxTime ms" -ForegroundColor Green
    }
}

# Test concurrent requests
Write-Host "`nTesting Concurrent Requests..." -ForegroundColor Yellow

$jobs = @()
for ($i = 1; $i -le 20; $i++) {
    $job = Start-Job -ScriptBlock {
        param($url)
        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        try {
            $response = Invoke-WebRequest -Uri $url -Method GET -UseBasicParsing
            $stopwatch.Stop()
            return @{
                Success = $true
                Time = $stopwatch.ElapsedMilliseconds
                StatusCode = $response.StatusCode
            }
        } catch {
            $stopwatch.Stop()
            return @{
                Success = $false
                Time = $stopwatch.ElapsedMilliseconds
                Error = $_.Exception.Message
            }
        }
    } -ArgumentList "http://localhost:8000/api/v1/orders/counts"
    $jobs += $job
}

$results = $jobs | Wait-Job | Receive-Job
$jobs | Remove-Job

$successCount = ($results | Where-Object { $_.Success }).Count
$avgConcurrentTime = ($results | Where-Object { $_.Success } | ForEach-Object { $_.Time } | Measure-Object -Average).Average

Write-Host "Concurrent Test Results:" -ForegroundColor White
Write-Host "  Successful Requests: $successCount/20" -ForegroundColor Green
Write-Host "  Average Response Time: $([math]::Round($avgConcurrentTime, 2))ms" -ForegroundColor Green

# Check system resources
Write-Host "`nSystem Resources:" -ForegroundColor Yellow
$stats = docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
Write-Host $stats -ForegroundColor White

# Check worker distribution
Write-Host "`nWorker Distribution:" -ForegroundColor Yellow
$workerLogs = docker compose logs app | Select-String "Booting worker" | Select-Object -Last 24
$app1Workers = ($workerLogs | Where-Object { $_.Line -match "app-1" }).Count
$app2Workers = ($workerLogs | Where-Object { $_.Line -match "app-2" }).Count
$app3Workers = ($workerLogs | Where-Object { $_.Line -match "app-3" }).Count
$app4Workers = ($workerLogs | Where-Object { $_.Line -match "app-4" }).Count

Write-Host "App-1 Workers: $app1Workers" -ForegroundColor Green
Write-Host "App-2 Workers: $app2Workers" -ForegroundColor Green
Write-Host "App-3 Workers: $app3Workers" -ForegroundColor Green
Write-Host "App-4 Workers: $app4Workers" -ForegroundColor Green
Write-Host "Total Workers: $($app1Workers + $app2Workers + $app3Workers + $app4Workers)" -ForegroundColor Cyan

Write-Host "`nPerformance test completed!" -ForegroundColor Green
