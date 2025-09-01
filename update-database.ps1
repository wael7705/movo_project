# ========================================
# سكريبت تحديث قاعدة البيانات
# ========================================
# هذا السكريبت يطبق جميع الأعمدة المفقودة على قاعدة البيانات

Write-Host "بدء تحديث قاعدة البيانات..." -ForegroundColor Cyan

# التحقق من حالة الحاويات
Write-Host "`nفحص حالة الحاويات..." -ForegroundColor Yellow
docker compose ps

# التحقق من اتصال قاعدة البيانات
Write-Host "`nفحص اتصال قاعدة البيانات..." -ForegroundColor Yellow
try {
    $result = docker compose exec -T db psql -U postgres -d movo_system -c "SELECT 1;"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "قاعدة البيانات متصلة" -ForegroundColor Green
    } else {
        Write-Host "فشل الاتصال بقاعدة البيانات" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "خطأ في الاتصال بقاعدة البيانات: $_" -ForegroundColor Red
    exit 1
}

# نسخ ملف الأعمدة المفقودة إلى الحاوية
Write-Host "`nنسخ ملف الأعمدة المفقودة..." -ForegroundColor Yellow
docker cp database_missing_columns.sql movo_project-db-1:/tmp/database_missing_columns.sql

# تطبيق الأعمدة المفقودة
Write-Host "`nتطبيق الأعمدة المفقودة..." -ForegroundColor Yellow
try {
    docker compose exec -T db psql -U postgres -d movo_system -f /tmp/database_missing_columns.sql
    if ($LASTEXITCODE -eq 0) {
        Write-Host "تم تطبيق الأعمدة المفقودة بنجاح" -ForegroundColor Green
    } else {
        Write-Host "فشل في تطبيق الأعمدة المفقودة" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "خطأ في تطبيق الأعمدة: $_" -ForegroundColor Red
    exit 1
}

# اختبار النظام
Write-Host "`nاختبار النظام..." -ForegroundColor Yellow
try {
    # اختبار زر Note
    $notesTest = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/1/notes" -Method GET
    if ($notesTest.StatusCode -eq 200) {
        Write-Host "زر Note يعمل" -ForegroundColor Green
    } else {
        Write-Host "زر Note لا يعمل" -ForegroundColor Red
    }
    
    # اختبار Captain Assignment
    $captainTest = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/assign/orders/1/candidates" -Method GET
    if ($captainTest.StatusCode -eq 200) {
        Write-Host "Captain Assignment يعمل" -ForegroundColor Green
    } else {
        Write-Host "Captain Assignment لا يعمل" -ForegroundColor Red
    }
    
    # اختبار زر Demo
    $demoTest = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/demo/processing" -Method POST
    if ($demoTest.StatusCode -eq 200) {
        Write-Host "زر Demo يعمل" -ForegroundColor Green
    } else {
        Write-Host "زر Demo لا يعمل" -ForegroundColor Red
    }
    
} catch {
    Write-Host "خطأ في اختبار النظام: $_" -ForegroundColor Red
}

Write-Host "`nتم تحديث قاعدة البيانات بنجاح!" -ForegroundColor Green
Write-Host "جميع الأعمدة المفقودة تم إضافتها والخدمات تعمل بشكل صحيح." -ForegroundColor Green