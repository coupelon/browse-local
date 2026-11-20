# Deployment Guide

This document provides comprehensive deployment instructions for the Browse Local Web Page HTML Retrieval API.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Docker Container](#docker-container)
3. [Docker Compose](#docker-compose)
4. [Kubernetes](#kubernetes)
5. [Environment Variables](#environment-variables)
6. [Health Checks & Monitoring](#health-checks--monitoring)
7. [Scaling Considerations](#scaling-considerations)
8. [Production Best Practices](#production-best-practices)

---

## Quick Start

### Minimal Docker Deployment

```bash
# Build the image
docker build -t browse-local:latest .

# Run the container
docker run -d \
  -p 8000:8000 \
  --name browse-local \
  --restart unless-stopped \
  browse-local:latest

# Verify health
curl http://localhost:8000/health
```

### Basic Request

```bash
curl "http://localhost:8000/v1/html?url=https://example.com"
```

---

## Docker Container

### Image Details

- **Base Image**: `mcr.microsoft.com/playwright/python:v1.65.2-noble`
- **Non-root User**: `appuser` (UID 1001)
- **Port**: 8000
- **Health Check**: Built-in via HEALTHCHECK directive

### Container Environment

```dockerfile
# Labels (OCI metadata)
LABEL maintainer="Browse Local Team"
LABEL org.opencontainers.image.description="Web Page HTML Retrieval API with Playwright"
LABEL org.opencontainers.image.source="https://github.com/your-org/browse-local"
LABEL org.opencontainers.image.version="1.0.0"

# Health check runs every 30 seconds
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Security Features

- **Non-root user**: Runs as `appuser` (UID 1001) - container cannot be escalated to root
- **Minimal surface**: Only necessary dependencies included
- **Health verification**: Container automatically restarted on health check failure

### Run Command Options

```bash
# Basic run with logging
docker run -d \
  -p 8000:8000 \
  --name browse-local \
  browse-local:latest

# With automatic restart
docker run -d \
  -p 8000:8000 \
  --name browse-local \
  --restart unless-stopped \
  browse-local:latest

# With environment variables
docker run -d \
  -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  -e TIMEOUT_SECONDS=30 \
  --name browse-local \
  browse-local:latest

# With resource limits
docker run -d \
  -p 8000:8000 \
  --memory=2g \
  --cpus=1.5 \
  --name browse-local \
  browse-local:latest

# With log rotation
docker run -d \
  -p 8000:8000 \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  --name browse-local \
  browse-local:latest

# Full production-ready example
docker run -d \
  --name browse-local \
  --restart unless-stopped \
  -p 8000:8000 \
  -e LOG_LEVEL=INFO \
  -e TIMEOUT_SECONDS=30 \
  --memory=2g \
  --cpus=1.5 \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  browse-local:latest
```

---

## Docker Compose

### Single Container

```yaml
version: '3.8'

services:
  browse-local:
    image: browse-local:latest
    container_name: browse-local
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - TIMEOUT_SECONDS=30
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Production with Resources & Monitoring

```yaml
version: '3.8'

services:
  browse-local:
    image: browse-local:latest
    container_name: browse-local
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - TIMEOUT_SECONDS=30
      - MAX_WORKERS=4
    restart: unless-stopped
    
    # Resource limits
    deploy:
      resources:
        limits:
          cpus: '1.5'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
    
    # Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
        labels: "service=browse-local"
    
    labels:
      - "app=browse-local"
      - "version=1.0.0"

  # Optional: Prometheus metrics collector
  # prometheus:
  #   image: prom/prometheus:latest
  #   ports:
  #     - "9090:9090"
  #   volumes:
  #     - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

### Run Compose Stack

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f browse-local

# Health status
docker-compose ps

# Stop services
docker-compose down
```

---

## Kubernetes

### Minimal Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: browse-local
  labels:
    app: browse-local
    version: "1.0.0"
spec:
  replicas: 2
  selector:
    matchLabels:
      app: browse-local
  template:
    metadata:
      labels:
        app: browse-local
    spec:
      containers:
      - name: browse-local
        image: browse-local:latest
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: TIMEOUT_SECONDS
          value: "30"
        
        # Resource limits
        resources:
          requests:
            memory: "1G"
            cpu: "1"
          limits:
            memory: "2G"
            cpu: "1.5"
        
        # Health check
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

---
apiVersion: v1
kind: Service
metadata:
  name: browse-local
spec:
  selector:
    app: browse-local
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP
```

### Deploy to Kubernetes

```bash
# Apply manifest
kubectl apply -f deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/browse-local

# Port forward for local testing
kubectl port-forward service/browse-local 8000:8000

# Describe deployment for debugging
kubectl describe deployment browse-local
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `TIMEOUT_SECONDS` | `30` | Default timeout for page navigation (seconds) |
| `MAX_WORKERS` | `4` | Maximum concurrent browser sessions (for scalability) |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |

### Setting Environment Variables

**Docker:**
```bash
docker run -e LOG_LEVEL=DEBUG -e TIMEOUT_SECONDS=45 browse-local:latest
```

**Docker Compose:**
```yaml
environment:
  - LOG_LEVEL=DEBUG
  - TIMEOUT_SECONDS=45
```

**Kubernetes:**
```yaml
env:
- name: LOG_LEVEL
  value: "DEBUG"
- name: TIMEOUT_SECONDS
  value: "45"
```

---

## Health Checks & Monitoring

### Built-in Health Endpoint

The container includes a built-in `/health` endpoint that responds with:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "browser_ready": true
}
```

#### Health Check Request

```bash
curl http://localhost:8000/health
```

### Monitoring Health

**Docker:**
```bash
# Check container health status
docker inspect --format='{{.State.Health.Status}}' browse-local

# View detailed health history
docker inspect browse-local | jq '.[] | .State.Health'
```

**Docker Compose:**
```bash
# Show health status
docker-compose ps

# View specific container health
docker-compose exec browse-local curl http://localhost:8000/health
```

**Kubernetes:**
```bash
# Check pod status
kubectl get pods -o wide

# Describe pod for health probe status
kubectl describe pod <pod-name>

# View logs for errors
kubectl logs <pod-name> --tail=50
```

### Prometheus Metrics (Optional)

To enable Prometheus metrics, configure `/metrics` endpoint. Example:

```python
from prometheus_client import Counter, Histogram

request_count = Counter('browse_local_requests_total', 'Total requests')
request_duration = Histogram('browse_local_request_duration_seconds', 'Request duration')
```

Scrape configuration:
```yaml
scrape_configs:
  - job_name: 'browse-local'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Multiple Container Instances**:
   ```bash
   # Run multiple instances on different ports
   docker run -d -p 8001:8000 --name browse-local-1 browse-local:latest
   docker run -d -p 8002:8000 --name browse-local-2 browse-local:latest
   docker run -d -p 8003:8000 --name browse-local-3 browse-local:latest
   ```

2. **Load Balancer (nginx)**:
   ```nginx
   upstream browse_local_backend {
       server localhost:8001;
       server localhost:8002;
       server localhost:8003;
   }
   
   server {
       listen 80;
       location / {
           proxy_pass http://browse_local_backend;
       }
   }
   ```

3. **Kubernetes HPA (Horizontal Pod Autoscaler)**:
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: browse-local-hpa
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: browse-local
     minReplicas: 2
     maxReplicas: 10
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
   ```

### Vertical Scaling

Increase memory/CPU per instance:

```bash
# Docker: run with more resources
docker run -d \
  -p 8000:8000 \
  --memory=4g \
  --cpus=2 \
  browse-local:latest

# Kubernetes: update resource limits
kubectl set resources deployment browse-local \
  --limits=cpu=2,memory=4G \
  --requests=cpu=1.5,memory=3G
```

### Connection Pooling

The API manages browser sessions efficiently:
- Each request gets a dedicated browser context
- Contexts are properly cleaned up after requests
- Playwright browser instance reused across requests

---

## Production Best Practices

### 1. Image Registry

```bash
# Tag for registry
docker tag browse-local:latest myregistry.azurecr.io/browse-local:1.0.0

# Push to registry
docker push myregistry.azurecr.io/browse-local:1.0.0

# Kubernetes: Use registry pull secret
kubectl create secret docker-registry regcred \
  --docker-server=myregistry.azurecr.io \
  --docker-username=<username> \
  --docker-password=<password>

# Reference in deployment
imagePullSecrets:
  - name: regcred
```

### 2. Security

- Run container as non-root user (default: `appuser`)
- Use network policies to restrict traffic
- Scan image for vulnerabilities: `docker scan browse-local:latest`
- Keep base image updated: `FROM mcr.microsoft.com/playwright/python:v1.65.2-noble`

### 3. Logging & Monitoring

- Set `LOG_LEVEL=INFO` for production (not DEBUG)
- Configure centralized logging (ELK, Loki, CloudWatch)
- Monitor health endpoint regularly
- Alert on health check failures

### 4. Resource Management

- Set memory limit to 2GB minimum (Playwright requires memory)
- Reserve 1GB minimum per instance
- Monitor actual usage and adjust based on load

### 5. Gradual Rollout

```bash
# Kubernetes: Rolling update strategy
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### 6. Rollback Plan

```bash
# Docker: Quick rollback
docker run -d --name browse-local-old browse-local:previous-version

# Kubernetes: Rollback to previous deployment
kubectl rollout undo deployment/browse-local

# View rollout history
kubectl rollout history deployment/browse-local
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs browse-local

# Check configuration
docker inspect browse-local

# Test health endpoint
docker exec browse-local curl http://localhost:8000/health
```

### High Memory Usage

- Check if browser sessions are being properly closed
- Monitor concurrent requests: `LOG_LEVEL=DEBUG`
- Consider increasing container memory limit
- Implement request queuing for high load

### Slow Response Times

- Check network latency to target URLs
- Monitor server logs for page load times
- Adjust `TIMEOUT_SECONDS` if needed (default 30s)
- Consider implementing response caching

### Health Check Failures

```bash
# Manual health check
curl -v http://localhost:8000/health

# Check if port is listening
netstat -an | grep 8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Increase health check timeout if needed
# (adjust in HEALTHCHECK or readinessProbe)
```

---

## Next Steps

1. **Build & Test**: `docker build -t browse-local:latest .`
2. **Deploy Locally**: `docker-compose up -d`
3. **Monitor**: `docker-compose logs -f browse-local`
4. **Scale**: Deploy multiple instances behind a load balancer
5. **Integrate**: Add to existing monitoring/logging infrastructure

For more information, see [README.md](./README.md) and [DEVELOPMENT.md](./DEVELOPMENT.md).
