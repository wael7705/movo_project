$ErrorActionPreference = "Stop"

Write-Host "== Checking Frontend env =="
if (!(Test-Path "movo-ts/.env.local")) {
  "VITE_API_BASE_URL=http://localhost:8000" | Out-File -Encoding utf8 "movo-ts/.env.local"
}

Write-Host "== Start Backend =="
Start-Process -NoNewWindow powershell -ArgumentList "uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "== Install/Start Frontend =="
Push-Location movo-ts
if (Test-Path pnpm-lock.yaml) {
  pnpm install
  Start-Process -NoNewWindow powershell -ArgumentList "pnpm run dev"
} else {
  npm install
  Start-Process -NoNewWindow powershell -ArgumentList "npm run dev"
}
Pop-Location

Write-Host "== Ready: open http://localhost:5173 =="


