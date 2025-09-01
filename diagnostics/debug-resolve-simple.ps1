# سكريبت فحص بسيط لزر البسط
Write-Host "🔧 بدء فحص زر البسط..." -ForegroundColor Cyan

# 1) فحص API
Write-Host "`n📋 1. فحص API" -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/counts" -Method GET
    Write-Host "✅ API يعمل - Status: $($health.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ API لا يعمل: $_" -ForegroundColor Red
    exit 1
}

# 2) فحص الطلبات في حالة مشكلة
Write-Host "`n🔍 2. فحص الطلبات في حالة مشكلة" -ForegroundColor Yellow
try {
    $orders = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json
    $problemOrders = $orders | Where-Object {$_.status -eq "problem"}
    Write-Host "📊 إجمالي الطلبات: $($orders.Count)" -ForegroundColor White
    Write-Host "🚨 الطلبات في حالة مشكلة: $($problemOrders.Count)" -ForegroundColor White
    
    if ($problemOrders.Count -gt 0) {
        Write-Host "✅ يوجد طلبات في حالة مشكلة للاختبار" -ForegroundColor Green
        foreach ($order in $problemOrders) {
            Write-Host "   - الطلب #$($order.order_id): $($order.customer_name)" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️ لا يوجد طلبات في حالة مشكلة" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ فشل في فحص الطلبات: $_" -ForegroundColor Red
}

# 3) فحص API البسط
Write-Host "`n🔧 3. فحص API البسط" -ForegroundColor Yellow
try {
    $problemOrders = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json | Where-Object {$_.status -eq "problem"}
    if ($problemOrders.Count -gt 0) {
        $testOrder = $problemOrders[0]
        Write-Host "🧪 اختبار API البسط مع الطلب #$($testOrder.order_id)" -ForegroundColor White
        
        $resolveBody = @{status = "pending"} | ConvertTo-Json
        $resolveResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/$($testOrder.order_id)/resolve" -Method PATCH -ContentType "application/json" -Body $resolveBody
        
        if ($resolveResponse.StatusCode -eq 200) {
            Write-Host "✅ API البسط يعمل بشكل صحيح" -ForegroundColor Green
            
            # إعادة الطلب إلى حالة مشكلة
            $backToProblem = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/$($testOrder.order_id)/problem" -Method PATCH
            if ($backToProblem.StatusCode -eq 200) {
                Write-Host "✅ تم إعادة الطلب إلى حالة مشكلة" -ForegroundColor Green
            }
        } else {
            Write-Host "❌ API البسط لا يعمل - Status: $($resolveResponse.StatusCode)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ لا يوجد طلبات في حالة مشكلة لاختبار API" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ فشل في اختبار API البسط: $_" -ForegroundColor Red
}

# 4) فحص Frontend
Write-Host "`n🌐 4. فحص Frontend" -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "✅ Frontend يعمل - Status: $($frontendResponse.StatusCode)" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend لا يعمل - Status: $($frontendResponse.StatusCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ فشل في فحص Frontend: $_" -ForegroundColor Red
}

# 5) فحص الملفات المصدرية
Write-Host "`n📁 5. فحص الملفات المصدرية" -ForegroundColor Yellow

# فحص OrderCard.tsx
$orderCardPath = "movo-ts/src/components/OrderCard.tsx"
if (Test-Path $orderCardPath) {
    Write-Host "✅ OrderCard.tsx موجود" -ForegroundColor Green
    
    $orderCardContent = Get-Content $orderCardPath -Raw
    if ($orderCardContent -match "onResolve") {
        Write-Host "✅ onResolve موجود في OrderCard.tsx" -ForegroundColor Green
    } else {
        Write-Host "❌ onResolve مفقود من OrderCard.tsx" -ForegroundColor Red
    }
    
    if ($orderCardContent -match "effectiveTab === 'problem' && onResolve") {
        Write-Host "✅ شرط عرض زر البسط موجود" -ForegroundColor Green
    } else {
        Write-Host "❌ شرط عرض زر البسط مفقود" -ForegroundColor Red
    }
} else {
    Write-Host "❌ OrderCard.tsx مفقود" -ForegroundColor Red
}

# فحص Dashboard.tsx
$dashboardPath = "movo-ts/src/pages/Dashboard.tsx"
if (Test-Path $dashboardPath) {
    Write-Host "✅ Dashboard.tsx موجود" -ForegroundColor Green
    
    $dashboardContent = Get-Content $dashboardPath -Raw
    if ($dashboardContent -match "handleResolve") {
        Write-Host "✅ handleResolve موجود في Dashboard.tsx" -ForegroundColor Green
    } else {
        Write-Host "❌ handleResolve مفقود من Dashboard.tsx" -ForegroundColor Red
    }
    
    if ($dashboardContent -match "onResolve={handleResolve}") {
        Write-Host "✅ onResolve يتم تمريره إلى OrderCard" -ForegroundColor Green
    } else {
        Write-Host "❌ onResolve لا يتم تمريره إلى OrderCard" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Dashboard.tsx مفقود" -ForegroundColor Red
}

# 6) فحص API routes
Write-Host "`n🔗 6. فحص API routes" -ForegroundColor Yellow
$ordersRoutePath = "backend/api/routes/orders.py"
if (Test-Path $ordersRoutePath) {
    Write-Host "✅ orders.py موجود" -ForegroundColor Green
    
    $ordersContent = Get-Content $ordersRoutePath -Raw
    if ($ordersContent -match "/resolve") {
        Write-Host "✅ route /resolve موجود" -ForegroundColor Green
    } else {
        Write-Host "❌ route /resolve مفقود" -ForegroundColor Red
    }
} else {
    Write-Host "❌ orders.py مفقود" -ForegroundColor Red
}

Write-Host "`n✅ انتهى الفحص!" -ForegroundColor Green
