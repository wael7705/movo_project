# Debug Resolve Button Script
Write-Host "Starting Resolve Button Debug..." -ForegroundColor Cyan

# 1) Check API
Write-Host "`n1. Checking API" -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/counts" -Method GET
    Write-Host "API Working - Status: $($health.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "API Not Working: $_" -ForegroundColor Red
    exit 1
}

# 2) Check Problem Orders
Write-Host "`n2. Checking Problem Orders" -ForegroundColor Yellow
try {
    $orders = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json
    $problemOrders = $orders | Where-Object {$_.status -eq "problem"}
    Write-Host "Total Orders: $($orders.Count)" -ForegroundColor White
    Write-Host "Problem Orders: $($problemOrders.Count)" -ForegroundColor White
    
    if ($problemOrders.Count -gt 0) {
        Write-Host "Found problem orders for testing" -ForegroundColor Green
        foreach ($order in $problemOrders) {
            Write-Host "   - Order #$($order.order_id): $($order.customer_name)" -ForegroundColor White
        }
    } else {
        Write-Host "No problem orders found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Failed to check orders: $_" -ForegroundColor Red
}

# 3) Check Resolve API
Write-Host "`n3. Checking Resolve API" -ForegroundColor Yellow
try {
    $problemOrders = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json | Where-Object {$_.status -eq "problem"}
    if ($problemOrders.Count -gt 0) {
        $testOrder = $problemOrders[0]
        Write-Host "Testing Resolve API with Order #$($testOrder.order_id)" -ForegroundColor White
        
        $resolveBody = @{status = "pending"} | ConvertTo-Json
        $resolveResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/$($testOrder.order_id)/resolve" -Method PATCH -ContentType "application/json" -Body $resolveBody
        
        if ($resolveResponse.StatusCode -eq 200) {
            Write-Host "Resolve API Working" -ForegroundColor Green
            
            # Put order back to problem
            $backToProblem = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/$($testOrder.order_id)/problem" -Method PATCH
            if ($backToProblem.StatusCode -eq 200) {
                Write-Host "Order put back to problem status" -ForegroundColor Green
            }
        } else {
            Write-Host "Resolve API Not Working - Status: $($resolveResponse.StatusCode)" -ForegroundColor Red
        }
    } else {
        Write-Host "No problem orders to test API" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Failed to test Resolve API: $_" -ForegroundColor Red
}

# 4) Check Frontend
Write-Host "`n4. Checking Frontend" -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "Frontend Working - Status: $($frontendResponse.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "Frontend Not Working - Status: $($frontendResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "Failed to check Frontend: $_" -ForegroundColor Red
}

# 5) Check Source Files
Write-Host "`n5. Checking Source Files" -ForegroundColor Yellow

# Check OrderCard.tsx
$orderCardPath = "movo-ts/src/components/OrderCard.tsx"
if (Test-Path $orderCardPath) {
    Write-Host "OrderCard.tsx exists" -ForegroundColor Green
    
    $orderCardContent = Get-Content $orderCardPath -Raw
    if ($orderCardContent -match "onResolve") {
        Write-Host "onResolve found in OrderCard.tsx" -ForegroundColor Green
    } else {
        Write-Host "onResolve missing from OrderCard.tsx" -ForegroundColor Red
    }
    
    if ($orderCardContent -match "effectiveTab === 'problem' && onResolve") {
        Write-Host "Resolve button condition found" -ForegroundColor Green
    } else {
        Write-Host "Resolve button condition missing" -ForegroundColor Red
    }
} else {
    Write-Host "OrderCard.tsx missing" -ForegroundColor Red
}

# Check Dashboard.tsx
$dashboardPath = "movo-ts/src/pages/Dashboard.tsx"
if (Test-Path $dashboardPath) {
    Write-Host "Dashboard.tsx exists" -ForegroundColor Green
    
    $dashboardContent = Get-Content $dashboardPath -Raw
    if ($dashboardContent -match "handleResolve") {
        Write-Host "handleResolve found in Dashboard.tsx" -ForegroundColor Green
    } else {
        Write-Host "handleResolve missing from Dashboard.tsx" -ForegroundColor Red
    }
    
    if ($dashboardContent -match "onResolve={handleResolve}") {
        Write-Host "onResolve being passed to OrderCard" -ForegroundColor Green
    } else {
        Write-Host "onResolve not being passed to OrderCard" -ForegroundColor Red
    }
} else {
    Write-Host "Dashboard.tsx missing" -ForegroundColor Red
}

# 6) Check API routes
Write-Host "`n6. Checking API routes" -ForegroundColor Yellow
$ordersRoutePath = "backend/api/routes/orders.py"
if (Test-Path $ordersRoutePath) {
    Write-Host "orders.py exists" -ForegroundColor Green
    
    $ordersContent = Get-Content $ordersRoutePath -Raw
    if ($ordersContent -match "/resolve") {
        Write-Host "route /resolve found" -ForegroundColor Green
    } else {
        Write-Host "route /resolve missing" -ForegroundColor Red
    }
} else {
    Write-Host "orders.py missing" -ForegroundColor Red
}

Write-Host "`nDebug Complete!" -ForegroundColor Green
