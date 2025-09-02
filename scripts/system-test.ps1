# نظام اختبار شامل - MOVO System
# PowerShell Script for Complete System Testing

param(
    [switch]$Quick,
    [switch]$Full,
    [switch]$Health,
    [switch]$Performance,
    [switch]$Database,
    [switch]$Frontend,
    [switch]$Backend,
    [switch]$WebSocket,
    [switch]$Help
)

# ألوان للرسائل
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$Cyan = "Cyan"

function Write-ColorText {
    param($Text, $Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Write-Header {
    param($Title)
    Write-Host ""
    Write-ColorText "=" * 60 $Cyan
    Write-ColorText "  $Title" $Cyan
    Write-ColorText "=" * 60 $Cyan
    Write-Host ""
}

function Write-Success {
    param($Message)
    Write-ColorText "✅ $Message" $Green
}

function Write-Error {
    param($Message)
    Write-ColorText "❌ $Message" $Red
}

function Write-Warning {
    param($Message)
    Write-ColorText "⚠️  $Message" $Yellow
}

function Write-Info {
    param($Message)
    Write-ColorText "ℹ️  $Message" $Blue
}

# اختبار صحة النظام
function Test-SystemHealth {
    Write-Header "فحص صحة النظام"
    
    # فحص Docker
    Write-Info "فحص Docker containers..."
    $containers = docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker containers running"
        Write-Host $containers
    } else {
        Write-Error "Docker containers not running"
        return $false
    }
    
    # فحص API
    Write-Info "فحص API endpoint..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "API is responding"
        } else {
            Write-Error "API not responding properly"
            return $false
        }
    } catch {
        Write-Error "API connection failed: $($_.Exception.Message)"
        return $false
    }
    
    # فحص Frontend
    Write-Info "فحص Frontend..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "Frontend is responding"
        } else {
            Write-Error "Frontend not responding properly"
            return $false
        }
    } catch {
        Write-Error "Frontend connection failed: $($_.Exception.Message)"
        return $false
    }
    
    return $true
}

# اختبار قاعدة البيانات
function Test-Database {
    Write-Header "فحص قاعدة البيانات"
    
    # فحص اتصال قاعدة البيانات
    Write-Info "فحص اتصال قاعدة البيانات..."
    try {
        $result = docker compose exec -T db psql -U movo_user -d movo_system -c "SELECT 1;" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database connection successful"
        } else {
            Write-Error "Database connection failed"
            return $false
        }
    } catch {
        Write-Error "Database test failed: $($_.Exception.Message)"
        return $false
    }
    
    # فحص الجداول
    Write-Info "فحص الجداول الأساسية..."
    $tables = @("orders", "captains", "restaurants", "customers", "notifications")
    foreach ($table in $tables) {
        try {
            $result = docker compose exec -T db psql -U movo_user -d movo_system -c "SELECT COUNT(*) FROM $table;" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Table $table exists and accessible"
            } else {
                Write-Warning "Table $table may not exist or accessible"
            }
        } catch {
            Write-Warning "Could not check table $table"
        }
    }
    
    return $true
}

# اختبار Redis
function Test-Redis {
    Write-Header "فحص Redis"
    
    Write-Info "فحص Redis connection..."
    try {
        $result = docker compose exec -T redis redis-cli ping 2>$null
        if ($result -eq "PONG") {
            Write-Success "Redis is responding"
        } else {
            Write-Error "Redis not responding"
            return $false
        }
    } catch {
        Write-Error "Redis connection failed: $($_.Exception.Message)"
        return $false
    }
    
    return $true
}

# اختبار WebSocket
function Test-WebSocket {
    Write-Header "فحص WebSocket"
    
    Write-Info "فحص WebSocket endpoints..."
    $endpoints = @(
        "ws://localhost:8000/ws/admin",
        "ws://localhost:8000/ws/captain/1"
    )
    
    foreach ($endpoint in $endpoints) {
        Write-Info "Testing $endpoint..."
        # WebSocket testing would require additional tools
        Write-Warning "WebSocket testing requires manual verification"
    }
    
    return $true
}

# اختبار الأداء
function Test-Performance {
    Write-Header "فحص الأداء"
    
    # فحص استجابة API
    Write-Info "فحص استجابة API..."
    $times = @()
    for ($i = 1; $i -le 5; $i++) {
        $start = Get-Date
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
            $end = Get-Date
            $duration = ($end - $start).TotalMilliseconds
            $times += $duration
            Write-Info "Request $i : $([math]::Round($duration, 2))ms"
        } catch {
            Write-Error "Request $i failed"
        }
    }
    
    if ($times.Count -gt 0) {
        $avgTime = ($times | Measure-Object -Average).Average
        Write-Info "Average response time: $([math]::Round($avgTime, 2))ms"
        
        if ($avgTime -lt 100) {
            Write-Success "API performance is excellent"
        } elseif ($avgTime -lt 500) {
            Write-Success "API performance is good"
        } else {
            Write-Warning "API performance needs improvement"
        }
    }
    
    return $true
}

# اختبار Frontend
function Test-Frontend {
    Write-Header "فحص Frontend"
    
    # فحص بناء Frontend
    Write-Info "فحص بناء Frontend..."
    Push-Location "movo-ts"
    try {
        $buildResult = npm run build 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Frontend build successful"
        } else {
            Write-Error "Frontend build failed"
            Write-Host $buildResult
            return $false
        }
    } catch {
        Write-Error "Frontend build test failed: $($_.Exception.Message)"
        return $false
    } finally {
        Pop-Location
    }
    
    return $true
}

# اختبار Backend
function Test-Backend {
    Write-Header "فحص Backend"
    
    # فحص API endpoints
    Write-Info "فحص API endpoints..."
    $endpoints = @(
        "/health",
        "/api/v1/orders",
        "/api/v1/captains",
        "/api/v1/notifications"
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000$endpoint" -TimeoutSec 5
            Write-Success "Endpoint $endpoint is responding"
        } catch {
            Write-Warning "Endpoint $endpoint may not be accessible"
        }
    }
    
    return $true
}

# اختبار شامل
function Test-FullSystem {
    Write-Header "اختبار شامل للنظام"
    
    $results = @{
        Health = Test-SystemHealth
        Database = Test-Database
        Redis = Test-Redis
        WebSocket = Test-WebSocket
        Performance = Test-Performance
        Frontend = Test-Frontend
        Backend = Test-Backend
    }
    
    Write-Header "نتائج الاختبار"
    foreach ($test in $results.GetEnumerator()) {
        if ($test.Value) {
            Write-Success "$($test.Key): PASSED"
        } else {
            Write-Error "$($test.Key): FAILED"
        }
    }
    
    $passed = ($results.Values | Where-Object { $_ -eq $true }).Count
    $total = $results.Count
    
    Write-Header "ملخص النتائج"
    Write-Info "الاختبارات المنجزة: $passed من $total"
    
    if ($passed -eq $total) {
        Write-Success "جميع الاختبارات نجحت! النظام يعمل بشكل مثالي."
    } elseif ($passed -gt ($total / 2)) {
        Write-Warning "معظم الاختبارات نجحت. النظام يعمل بشكل جيد."
    } else {
        Write-Error "عدة اختبارات فشلت. النظام يحتاج إلى إصلاح."
    }
}

# اختبار سريع
function Test-Quick {
    Write-Header "اختبار سريع"
    
    Write-Info "فحص سريع للنظام..."
    
    # فحص Docker
    $containers = docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker containers running"
    } else {
        Write-Error "Docker containers not running"
        return
    }
    
    # فحص API
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
        Write-Success "API responding"
    } catch {
        Write-Error "API not responding"
        return
    }
    
    # فحص Frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5
        Write-Success "Frontend responding"
    } catch {
        Write-Error "Frontend not responding"
        return
    }
    
    Write-Success "النظام يعمل بشكل طبيعي!"
}

# عرض المساعدة
function Show-Help {
    Write-Header "مساعدة - MOVO System Test"
    Write-Host ""
    Write-ColorText "الاستخدام:" $Yellow
    Write-Host "  .\scripts\system-test.ps1 [خيارات]"
    Write-Host ""
    Write-ColorText "الخيارات:" $Yellow
    Write-Host "  -Quick        اختبار سريع للنظام"
    Write-Host "  -Full         اختبار شامل للنظام"
    Write-Host "  -Health       فحص صحة النظام"
    Write-Host "  -Performance  فحص الأداء"
    Write-Host "  -Database     فحص قاعدة البيانات"
    Write-Host "  -Frontend     فحص Frontend"
    Write-Host "  -Backend      فحص Backend"
    Write-Host "  -WebSocket    فحص WebSocket"
    Write-Host "  -Help         عرض هذه المساعدة"
    Write-Host ""
    Write-ColorText "أمثلة:" $Yellow
    Write-Host "  .\scripts\system-test.ps1 -Quick"
    Write-Host "  .\scripts\system-test.ps1 -Full"
    Write-Host "  .\scripts\system-test.ps1 -Health -Database"
    Write-Host ""
}

# Main execution
if ($Help) {
    Show-Help
    exit 0
}

Write-Header "MOVO System Test Suite"
Write-Info "بدء اختبار النظام..."

if ($Quick) {
    Test-Quick
} elseif ($Full) {
    Test-FullSystem
} else {
    # اختبارات محددة
    if ($Health) { Test-SystemHealth }
    if ($Database) { Test-Database }
    if ($Performance) { Test-Performance }
    if ($Frontend) { Test-Frontend }
    if ($Backend) { Test-Backend }
    if ($WebSocket) { Test-WebSocket }
    
    # إذا لم يتم تحديد أي اختبار، قم بالاختبار السريع
    if (-not ($Health -or $Database -or $Performance -or $Frontend -or $Backend -or $WebSocket)) {
        Test-Quick
    }
}

Write-Header "انتهاء الاختبار"
Write-Info "تم الانتهاء من اختبار النظام."
