param(
  [Parameter(Mandatory=$true)][int]$OrderId,
  [Parameter(Mandatory=$true)][int]$CaptainId
)

Write-Host "TRACE start: OrderId=$OrderId, CaptainId=$CaptainId"

# 1) Show compose state
try { docker compose ps | Out-Host } catch { Write-Warning $_ }

# Container IDs
$appId   = (docker compose ps -q app)
$dbId    = (docker compose ps -q db)
$nginxId = (docker compose ps -q nginx)
$pgbId   = (docker compose ps -q pgbouncer)
$redisId = (docker compose ps -q redis)

# 2) Health checks
Write-Host "Health checks..."
try { curl.exe -s http://localhost:8000/health | Out-Host } catch {}
try { docker compose exec -T db psql -U postgres -d movo_system -c "select now();" | Out-Host } catch {}
try { docker compose exec -T pgbouncer sh -lc 'pg_isready -h db -p 5432 -U postgres || true' | Out-Host } catch {}

# 3) Start logs as jobs
$jobs = @()

if ($appId) {
  $jobs += Start-Job -Name "app-logs" -ScriptBlock {
    param($id)
    Write-Host "APP logs:"
    docker logs -f $id
  } -ArgumentList $appId
}

if ($nginxId) {
  $jobs += Start-Job -Name "nginx-logs" -ScriptBlock {
    param($id)
    Write-Host "Nginx logs:"
    docker exec -i $id sh -lc 'tail -F /var/log/nginx/access.log /var/log/nginx/error.log'
  } -ArgumentList $nginxId
}

if ($pgbId) {
  $jobs += Start-Job -Name "pgbouncer-logs" -ScriptBlock {
    param($id)
    Write-Host "PgBouncer logs:"
    docker exec -i $id sh -lc 'tail -F /var/log/pgbouncer/pgbouncer.log 2>/dev/null || tail -F /var/log/pgbouncer.log 2>/dev/null || tail -F /proc/1/fd/1'
  } -ArgumentList $pgbId
}

# 4) DB watch (order status and last note)
$jobs += Start-Job -Name "db-watch" -ScriptBlock {
  param($orderId)
  $prev = ""
  Write-Host "DB watch running..."
  while ($true) {
    try {
      $st = docker compose exec -T db psql -U postgres -d movo_system -Atc "select status from orders where order_id=$orderId;"
      if ($st -and $st -ne $prev) { Write-Host ("[DB] order {0} status -> {1}" -f $orderId, $st); $prev = $st }
      $note = docker compose exec -T db psql -U postgres -d movo_system -Atc "select coalesce((select left(note_text,80) from notes where target_type='order' and reference_id=$orderId order by created_at desc limit 1),'')"
      if ($note) { Write-Host ("[DB] last note: {0}" -f $note) }
    } catch {}
    Start-Sleep -Seconds 1
  }
} -ArgumentList $OrderId

# 5) API ping
$jobs += Start-Job -Name "api-ping" -ScriptBlock {
  param($orderId)
  Write-Host "API ping running..."
  while ($true) { try { curl.exe -s "http://localhost:8000/api/v1/orders/$orderId" | Out-Null } catch {}; Start-Sleep -Seconds 2 }
} -ArgumentList $OrderId

Write-Host "Ready. Open UI and click Assign Captain for order $OrderId (captain $CaptainId)."
Write-Host "Press Ctrl+C to stop. Then: Get-Job | Stop-Job *; Remove-Job *"

Wait-Job -Any $jobs | Out-Null
