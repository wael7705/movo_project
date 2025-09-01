# System Diagnostics Scripts

This folder contains PowerShell scripts for system diagnostics and monitoring.

## Available Scripts

### 1. `trace-check.ps1` - Comprehensive Diagnostics
**Usage:** `powershell -ExecutionPolicy Bypass -File .\diagnostics\trace-check.ps1`

**Features:**
- ✅ Next Button functionality
- ✅ Orders Count API
- ✅ Rating Button functionality  
- ✅ Notes Button functionality
- ✅ Captain Assignment functionality
- ✅ Container Status check
- ✅ Worker Status (16 workers across 4 containers)
- ✅ WebSocket Status
- ✅ Database Connection
- ✅ Redis Connection
- ✅ Grafana Status

### 2. `quick-check.ps1` - Quick System Check
**Usage:** `powershell -ExecutionPolicy Bypass -File .\diagnostics\quick-check.ps1`

**Features:**
- ✅ Main API status
- ✅ Container status
- ✅ Worker count
- ✅ Database connection
- ✅ Redis connection
- ✅ Grafana status

## System Architecture

- **4 Application Containers** with 4 workers each (16 total workers)
- **Hybrid System:** uvicorn + gunicorn with async support
- **Load Balancing:** nginx
- **Database:** PostgreSQL + PgBouncer
- **Cache:** Redis
- **Monitoring:** Grafana

## Troubleshooting

If any component shows errors:
1. Check container logs: `docker compose logs [service-name]`
2. Restart services: `docker compose restart [service-name]`
3. Check system resources: `docker stats`
4. Run full diagnostics: `.\diagnostics\trace-check.ps1`
