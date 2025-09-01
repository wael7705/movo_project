# سكريبت فحص شامل لزر البسط (Resolve Button)
# التشغيل: powershell -ExecutionPolicy Bypass -File .\diagnostics\debug-resolve-button.ps1

Write-Host "🔧 بدء فحص شامل لزر البسط..." -ForegroundColor Cyan

# 1) فحص النظام الأساسي
Write-Host "`n📋 1. فحص النظام الأساسي" -ForegroundColor Yellow
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
            Write-Host "   - الطلب #$($order.order_id): $($order.customer_name) - $($order.restaurant_name)" -ForegroundColor White
        }
    } else {
        Write-Host "⚠️ لا يوجد طلبات في حالة مشكلة - إنشاء طلب للاختبار" -ForegroundColor Yellow
        # إنشاء طلب في حالة مشكلة
        try {
            $createResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/demo" -Method POST
            if ($createResponse.StatusCode -eq 200) {
                Write-Host "✅ تم إنشاء طلب جديد" -ForegroundColor Green
                # وضع الطلب في حالة مشكلة
                $newOrders = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders" -Method GET | Select-Object -ExpandProperty Content | ConvertFrom-Json
                $latestOrder = $newOrders | Sort-Object order_id -Descending | Select-Object -First 1
                $problemResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/$($latestOrder.order_id)/problem" -Method PATCH
                if ($problemResponse.StatusCode -eq 200) {
                    Write-Host "✅ تم وضع الطلب #$($latestOrder.order_id) في حالة مشكلة" -ForegroundColor Green
                }
            }
        } catch {
            Write-Host "❌ فشل في إنشاء طلب للاختبار: $_" -ForegroundColor Red
        }
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
        
        # اختبار API البسط
        $resolveBody = @{status = "pending"} | ConvertTo-Json
        $resolveResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/$($testOrder.order_id)/resolve" -Method PATCH -ContentType "application/json" -Body $resolveBody
        
        if ($resolveResponse.StatusCode -eq 200) {
            Write-Host "✅ API البسط يعمل بشكل صحيح" -ForegroundColor Green
            
            # إعادة الطلب إلى حالة مشكلة للاختبار
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
        
        # فحص وجود الملفات المطلوبة
        $distPath = "movo-ts/dist"
        if (Test-Path $distPath) {
            Write-Host "✅ مجلد dist موجود" -ForegroundColor Green
            
            $indexHtml = Join-Path $distPath "index.html"
            if (Test-Path $indexHtml) {
                Write-Host "✅ index.html موجود" -ForegroundColor Green
            } else {
                Write-Host "❌ index.html مفقود" -ForegroundColor Red
            }
            
            $assetsPath = Join-Path $distPath "assets"
            if (Test-Path $assetsPath) {
                $jsFiles = Get-ChildItem $assetsPath -Filter "*.js"
                $cssFiles = Get-ChildItem $assetsPath -Filter "*.css"
                Write-Host "✅ مجلد assets موجود - JS: $($jsFiles.Count), CSS: $($cssFiles.Count)" -ForegroundColor Green
            } else {
                Write-Host "❌ مجلد assets مفقود" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ مجلد dist مفقود - Frontend لم يتم بناؤه" -ForegroundColor Red
        }
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
    
    if ($orderCardContent -match "بسط") {
        Write-Host "✅ زر البسط موجود في الكود" -ForegroundColor Green
    } else {
        Write-Host "❌ زر البسط مفقود من الكود" -ForegroundColor Red
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
    
    if ($dashboardContent -match "StatusSelectionModal") {
        Write-Host "✅ StatusSelectionModal موجود" -ForegroundColor Green
    } else {
        Write-Host "❌ StatusSelectionModal مفقود" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Dashboard.tsx مفقود" -ForegroundColor Red
}

# فحص StatusSelectionModal.tsx
$modalPath = "movo-ts/src/components/StatusSelectionModal.tsx"
if (Test-Path $modalPath) {
    Write-Host "✅ StatusSelectionModal.tsx موجود" -ForegroundColor Green
} else {
    Write-Host "❌ StatusSelectionModal.tsx مفقود" -ForegroundColor Red
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
    
    if ($ordersContent -match "resolve_order_problem") {
        Write-Host "✅ دالة resolve_order_problem موجودة" -ForegroundColor Green
    } else {
        Write-Host "❌ دالة resolve_order_problem مفقودة" -ForegroundColor Red
    }
} else {
    Write-Host "❌ orders.py مفقود" -ForegroundColor Red
}

# 7) فحص api.ts
Write-Host "`n📡 7. فحص api.ts" -ForegroundColor Yellow
$apiPath = "movo-ts/src/lib/api.ts"
if (Test-Path $apiPath) {
    Write-Host "✅ api.ts موجود" -ForegroundColor Green
    
    $apiContent = Get-Content $apiPath -Raw
    if ($apiContent -match "resolve.*async") {
        Write-Host "✅ دالة resolve موجودة في api.ts" -ForegroundColor Green
    } else {
        Write-Host "❌ دالة resolve مفقودة من api.ts" -ForegroundColor Red
    }
} else {
    Write-Host "❌ api.ts مفقود" -ForegroundColor Red
}

# 8) فحص الحاويات
Write-Host "`n🐳 8. فحص الحاويات" -ForegroundColor Yellow
try {
    $containers = docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
    Write-Host "📊 حالة الحاويات:" -ForegroundColor White
    Write-Host $containers -ForegroundColor White
    
    $appContainers = docker compose ps --filter "name=app" --format "{{.Name}}"
    $appCount = ($appContainers -split "`n").Count
    Write-Host "✅ عدد حاويات app: $appCount" -ForegroundColor Green
    
    $nginxContainer = docker compose ps --filter "name=nginx" --format "{{.Name}}"
    if ($nginxContainer) {
        Write-Host "✅ nginx يعمل" -ForegroundColor Green
    } else {
        Write-Host "❌ nginx لا يعمل" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ فشل في فحص الحاويات: $_" -ForegroundColor Red
}

# 9) توصيات الإصلاح
Write-Host "`n🔧 9. توصيات الإصلاح" -ForegroundColor Yellow

# فحص إذا كان Frontend يحتاج إعادة بناء
$distPath = "movo-ts/dist"
$srcPath = "movo-ts/src"
if (Test-Path $distPath -and Test-Path $srcPath) {
    $distTime = (Get-Item $distPath).LastWriteTime
    $srcTime = (Get-ChildItem $srcPath -Recurse | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
    
    if ($srcTime -gt $distTime) {
        Write-Host "⚠️ الملفات المصدرية أحدث من dist - Frontend يحتاج إعادة بناء" -ForegroundColor Yellow
        Write-Host "💡 الحل: cd movo-ts; npm run build" -ForegroundColor Cyan
    } else {
        Write-Host "✅ Frontend محدث" -ForegroundColor Green
    }
}

# فحص إذا كان nginx يحتاج إعادة تشغيل
Write-Host "`n🔄 10. فحص nginx" -ForegroundColor Yellow
try {
    $nginxLogs = docker compose logs nginx --tail 10
    if ($nginxLogs -match "error" -or $nginxLogs -match "failed") {
        Write-Host "⚠️ nginx يحتاج إعادة تشغيل" -ForegroundColor Yellow
        Write-Host "💡 الحل: docker compose restart nginx" -ForegroundColor Cyan
    } else {
        Write-Host "✅ nginx يعمل بشكل طبيعي" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ فشل في فحص nginx" -ForegroundColor Red
}

Write-Host "`n🎯 ملخص الفحص:" -ForegroundColor Cyan
Write-Host "1. تحقق من وجود طلبات في حالة مشكلة" -ForegroundColor White
Write-Host "2. تأكد من عمل API البسط" -ForegroundColor White
Write-Host "3. تحقق من بناء Frontend" -ForegroundColor White
Write-Host "4. تأكد من تمرير onResolve إلى OrderCard" -ForegroundColor White
Write-Host "5. تحقق من وجود زر البسط في الكود" -ForegroundColor White

Write-Host "`n✅ انتهى الفحص الشامل!" -ForegroundColor Green
Write-Host "🔍 إذا كان كل شيء يبدو صحيحاً، المشكلة قد تكون في cache المتصفح" -ForegroundColor Yellow
Write-Host "💡 جرب: Ctrl+F5 أو فتح نافذة خاصة" -ForegroundColor Cyan
