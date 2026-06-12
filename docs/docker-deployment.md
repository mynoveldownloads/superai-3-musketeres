cat > docker-deployment.md << 'EOF'
# Docker Deployment Guide for superai-3-musketeres

This guide deploys 3 services with a single command:
- **Frontend**: Port 8000 (HTML pages)
- **SQL Backend**: Port 3000 (SQL query API)
- **ADK Agent**: Port 5000 (Google ADK agent server)

---

## Step 1: Create `docker-compose.yml`

```bash
cd ~/local_jupyter/superai-deployment/superai-3-musketeres

cat > docker-compose.yml << 'COMPOSE'
services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    container_name: frontend
    restart: unless-stopped

  sql-backend:
    build:
      context: .
      dockerfile: Dockerfile.sql
    ports:
      - "3000:3000"
    container_name: sql-backend
    restart: unless-stopped

  adk-agent:
    build:
      context: .
      dockerfile: Dockerfile.adk
    ports:
      - "5000:5000"
    container_name: adk-agent
    restart: unless-stopped
COMPOSE
```

---

## Step 2: Create `frontend/Dockerfile`

```bash
cat > frontend/Dockerfile << 'FRONTEND'
FROM python:3.11-slim

WORKDIR /app

# Copy frontend files
COPY . .

# Install Flask (optional, for future extension)
RUN pip install --no-cache-dir flask

# Start HTTP server
CMD ["python3", "-m", "http.server", "8000", "--bind", "0.0.0.0"]
FRONTEND
```

---

## Step 3: Create `Dockerfile.sql` (SQL Backend)

```bash
cat > Dockerfile.sql << 'SQL'
FROM python:3.11-slim

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy entire project
COPY . .

# Install uv and dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv sync

CMD ["uv", "run", "backend/init_server/api_server.py"]
SQL
```

---

## Step 4: Create `Dockerfile.adk` (ADK Agent)

```bash
cat > Dockerfile.adk << 'ADK'
FROM python:3.11-slim

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy entire project
COPY . .

# Install uv and dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"
RUN uv sync

CMD ["uv", "run", "backend/init_adk_server/fastapi_server.py"]
ADK
```

---

## Step 5: Install Docker (If Not Already Installed)

```bash
apt update
apt install docker.io -y
systemctl start docker
systemctl enable docker

# Install docker-compose
apt install docker-compose -y
```

---

## Step 6: Deploy All Services

```bash
# Build and start all services (background mode)
docker-compose up -d --build

# Verify services are running
docker-compose ps

# View logs
docker-compose logs -f
```

---

## Access URLs

| Service | Local URL | Tailscale URL |
|---------|-----------|---------------|
| Frontend | `http://localhost:8000` | `http://100.101.98.26:8000` |
| SQL Backend | `http://localhost:3000` | `http://100.101.98.26:3000` |
| ADK Agent | `http://localhost:5000` | `http://100.101.98.26:5000` |

---

## Manage Containers

```bash
# Stop all services
docker-compose down

# Restart all services
docker-compose restart

# Rebuild and restart (after code changes)
docker-compose up -d --build

# View container logs
docker-compose logs frontend
docker-compose logs sql-backend
docker-compose logs adk-agent

# Remove all containers and images
docker-compose down --rmi all
```

---

## Troubleshooting

### Check if ports are available
```bash
netstat -tlnp | grep -E '8000|3000|5000'
```

### Check container status
```bash
docker ps -a
```

### Rebuild from scratch
```bash
docker-compose down --rmi all
docker-compose up -d --build
```

---

## File Structure


```
superai-3-musketeres/
├── docker-compose.yml
├── Dockerfile.sql
├── Dockerfile.adk
├── docker-deployment.md
├── frontend/
│ ├── Dockerfile
│ ├── Homepage.html
│ ├── Inventory.html
│ ├── MainPage.html
│ └── ...
├── backend/
│ ├── init_server/api_server.py
│ ├── init_adk_server/fastapi_server.py
│ └── ...
├── uv.lock
├── pyproject.toml
└── requirements.txt
```

EOF

# Verify file was created
ls -la docker-deployment.md