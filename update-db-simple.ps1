Write-Host "بدء تحديث قاعدة البيانات..." -ForegroundColor Cyan

# نسخ ملف الأعمدة المفقودة إلى الحاوية
Write-Host "نسخ ملف الأعمدة المفقودة..." -ForegroundColor Yellow
docker cp database_missing_columns.sql movo_project-db-1:/tmp/database_missing_columns.sql

# تطبيق الأعمدة المفقودة
Write-Host "تطبيق الأعمدة المفقودة..." -ForegroundColor Yellow
docker compose exec -T db psql -U postgres -d movo_system -f /tmp/database_missing_columns.sql

# اختبار النظام
Write-Host "اختبار النظام..." -ForegroundColor Yellow

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

Write-Host "تم تحديث قاعدة البيانات بنجاح!" -ForegroundColor Green
