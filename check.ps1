$ErrorActionPreference='SilentlyContinue'

# تشغيل الحاويات
docker compose up -d --build | Out-Null

Write-Host "`n== Services =="; docker compose ps

Write-Host "`n== DB =="
docker compose exec -T db pg_isready -h 127.0.0.1 -p 5432 -U postgres
$exists = docker compose exec -T db psql -U postgres -tAc "SELECT 1 FROM pg_database WHERE datname='movo_system';"
if ($exists.Trim() -eq '1') {"✅ movo_system موجودة"} else {"❌ قاعدة movo_system غير موجودة"}

Write-Host "`n== PgBouncer =="
docker compose exec -T pgbouncer psql -h pgbouncer -p 6432 -U postgres -d movo_system -c "select 1;" | Out-Null
if ($LASTEXITCODE -eq 0) {"✅ PgBouncer OK"} else {"❌ PgBouncer فشل"}

Write-Host "`n== Redis =="
$rp = docker compose exec -T redis redis-cli PING
if ($rp.Trim() -eq 'PONG') {"✅ Redis OK"} else {"❌ Redis فشل"}

Write-Host "`n== HTTP/WS =="
function H($p){ try{ (Invoke-WebRequest -UseBasicParsing -TimeoutSec 5 "http://localhost:8000$p").StatusCode }catch{ 0 } }
"health: $(H('/health'))  db_ping: $(H('/db_ping'))  redis_ping: $(H('/redis_ping'))  socket.io: $(H('/socket.io/?EIO=4&transport=polling'))"

$app = (docker compose ps --format json | ConvertFrom-Json) | ?{ $_.Service -eq 'app' }
"app containers: $($app.Count)"
