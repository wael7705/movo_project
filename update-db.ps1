Write-Host "Starting database update..." -ForegroundColor Cyan

# Copy missing columns file to container
Write-Host "Copying missing columns file..." -ForegroundColor Yellow
docker cp database_missing_columns.sql movo_project-db-1:/tmp/database_missing_columns.sql

# Apply missing columns
Write-Host "Applying missing columns..." -ForegroundColor Yellow
docker compose exec -T db psql -U postgres -d movo_system -f /tmp/database_missing_columns.sql

# Test system
Write-Host "Testing system..." -ForegroundColor Yellow

# Test Note button
try {
    $notesTest = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/1/notes" -Method GET
    if ($notesTest.StatusCode -eq 200) {
        Write-Host "Note button works" -ForegroundColor Green
    } else {
        Write-Host "Note button failed" -ForegroundColor Red
    }
} catch {
    Write-Host "Note button error: $_" -ForegroundColor Red
}

# Test Captain Assignment
try {
    $captainTest = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/assign/orders/1/candidates" -Method GET
    if ($captainTest.StatusCode -eq 200) {
        Write-Host "Captain Assignment works" -ForegroundColor Green
    } else {
        Write-Host "Captain Assignment failed" -ForegroundColor Red
    }
} catch {
    Write-Host "Captain Assignment error: $_" -ForegroundColor Red
}

# Test Demo button
try {
    $demoTest = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/orders/demo/processing" -Method POST
    if ($demoTest.StatusCode -eq 200) {
        Write-Host "Demo button works" -ForegroundColor Green
    } else {
        Write-Host "Demo button failed" -ForegroundColor Red
    }
} catch {
    Write-Host "Demo button error: $_" -ForegroundColor Red
}

Write-Host "Database update completed!" -ForegroundColor Green
