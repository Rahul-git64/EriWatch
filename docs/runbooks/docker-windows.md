# Runbook: Docker Desktop & Windows WSL2 Troubleshooting

## Context & Overview

EriWatch orchestrates four microservices via Docker Compose (`infra/docker/docker-compose.yml`):
- `eriwatch-db`: PostgreSQL 16 + PostGIS 3.4 + pgvector
- `eriwatch-api`: FastAPI backend with structured JSON logging and health checks
- `eriwatch-web`: Next.js 14 App Router dashboard
- `eriwatch-n8n`: n8n workflow engine (v1.68)

On Windows developer machines using Docker Desktop with WSL2 backend, specific host service and path mounting issues can arise upon machine restart. This runbook documents the failure mode, the workaround used during Corrective Stage R, why that workaround is fragile, and the clean procedure to operate the stack.

---

## The Startup Failure Mode

After a Windows host restart, running `docker compose` or `docker info` may fail with:
```text
failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.
```

### Root Causes
1. **Windows Host Service Stopped:**
   The background Windows service `com.docker.service` (`Docker Desktop Service`) was stopped upon machine reboot. Non-elevated shells cannot start Windows services (`Start-Service com.docker.service` yields permission denied).
2. **WSL2 Automount Path Mismatch:**
   Inside the `docker-desktop` WSL distribution, the Windows system drive is automounted under `/mnt/host/c` (as specified in `/etc/wsl.conf` `[automount] root = /mnt/host`).
   However, Docker Desktop's internal backend script (`wsl-bootstrap run`) attempts to load base images and CLI tools using the absolute path `/c/Program Files/Docker/Docker/resources/...`.
   Because `/c` did not exist inside the distribution, the bootstrap engine timed out and failed to create the Windows named pipe `\\.\pipe\dockerDesktopLinuxEngine`.

---

## The Workaround Used in Stage R & Why It Is Fragile

### The Workaround
From PowerShell, a symlink was injected into the root filesystem of the `docker-desktop` WSL distribution:
```powershell
wsl -d docker-desktop -u root -e /bin/sh -c "ln -sf /mnt/host/c /c && ln -sf /mnt/host/c /mnt/c"
```
Once `/c` resolved to `/mnt/host/c`, Docker Desktop started cleanly and bound the engine pipe.

### Why This Is Fragile
1. **WSL2 Lifecycle Volatility:** The `docker-desktop` distro is managed by Docker Desktop. Updates or resets to Docker Desktop can recreate or re-import the root virtual hard disk (`ext4.vhdx`), obliterating root symlinks.
2. **Permission Boundary:** If the host user reboots without Docker Desktop set to auto-start in Windows startup apps, non-admin CLI tools cannot start the underlying Windows service.

---

## Clean Way to Start and Verify the Stack

### 1. Launch Docker Desktop
Launch Docker Desktop from the Start Menu or via PowerShell:
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```
Wait for the Docker system tray icon to steady.

### 2. Verify Engine Connectivity
```powershell
docker version
```
Ensure both `Client` and `Server: Docker Desktop` respond with versions.

### 3. Start the Stack via Make
```bash
make stack-up
```
This builds any updated images and starts all four containers in detached mode:
- `db` (`5432`)
- `api` (`8000`)
- `web` (`3000`)
- `n8n` (`5678`)

### 4. Verify Stack Status & Endpoints
```bash
make stack-status
```
Expected output:
- All 4 containers show `Up ... (healthy)`
- `http://localhost:8000/health` returns `{"status":"ok", ...}`
- `http://localhost:3000/` returns `HTTP/1.1 200 OK`
- `http://localhost:5678/healthz` returns `{"status":"ok"}`

### 5. Tear Down the Stack
```bash
make stack-down
```
To preserve persistent volume data (PostgreSQL database state and n8n workflows), `stack-down` leaves Docker volumes intact.
