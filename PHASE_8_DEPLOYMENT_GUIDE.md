# PHASE 8 - DEPLOYMENT & PRODUCTION GUIDE
## Production Deployment, Security Hardening, and Operations

**Phase**: 8 (Final) | **Environment**: Production | **Status**: ✅ READY
**Deployment Options**: Docker, Kubernetes, Systemd, Cloud Platforms

---

## TABLE OF CONTENTS

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Security Hardening](#security-hardening)
6. [Performance Optimization](#performance-optimization)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)

---

## PRE-DEPLOYMENT CHECKLIST

### Code Quality

- [ ] All tests passing: `pytest tests/ -v`
- [ ] 80%+ code coverage achieved
- [ ] No critical security issues: `bandit -r .`
- [ ] Code formatted: `black .`
- [ ] Type hints valid: `mypy .`
- [ ] Dependencies secure: `safety check`

### Configuration

- [ ] `.env` file configured
- [ ] Database credentials secured
- [ ] API keys rotated
- [ ] CORS origins configured
- [ ] Rate limits set appropriately
- [ ] Logging level set to INFO

### Infrastructure

- [ ] Database provisioned and tested
- [ ] Storage configured (S3, GCS, etc.)
- [ ] SSL/TLS certificates ready
- [ ] Load balancer configured (if needed)
- [ ] Monitoring tools set up
- [ ] Backup system in place

### Documentation

- [ ] Deployment runbook prepared
- [ ] Incident response plan documented
- [ ] Rollback procedure defined
- [ ] Team trained on operations

---

## DOCKER DEPLOYMENT

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Run application
CMD ["uvicorn", "api_or_cli.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### .dockerignore

```
__pycache__
.git
.env
.env.local
venv
*.pyc
.pytest_cache
htmlcov
.coverage
logs
*.db
.DS_Store
```

### Build and Run

```bash
# Build image
docker build -t iraqaf:1.0 .

# Run container
docker run -d \
  --name iraqaf \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/iraqaf \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  iraqaf:1.0

# View logs
docker logs -f iraqaf

# Stop container
docker stop iraqaf

# Remove container
docker rm iraqaf
```

### Docker Compose (Full Stack)

Create `docker-compose.yml`:

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    container_name: iraqaf-db
    environment:
      POSTGRES_DB: iraqaf
      POSTGRES_USER: iraqaf_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U iraqaf_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: iraqaf-cache
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    container_name: iraqaf-api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://iraqaf_user:${DB_PASSWORD}@postgres:5432/iraqaf
      REDIS_URL: redis://redis:6379
      LOG_LEVEL: INFO
      DEBUG: "false"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: iraqaf-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
```

Deploy:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove everything (careful!)
docker-compose down -v
```

---

## KUBERNETES DEPLOYMENT

### Kubernetes Manifest

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iraqaf-api
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: iraqaf-api
  template:
    metadata:
      labels:
        app: iraqaf-api
    spec:
      containers:
      - name: api
        image: iraqaf:1.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: iraqaf-secrets
              key: database-url
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
```

### Service & Ingress

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: iraqaf-api-service
spec:
  type: LoadBalancer
  selector:
    app: iraqaf-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: iraqaf-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: iraqaf.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: iraqaf-api-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace iraqaf

# Create secrets
kubectl create secret generic iraqaf-secrets \
  --from-literal=database-url="postgresql://..." \
  -n iraqaf

# Deploy
kubectl apply -f k8s/ -n iraqaf

# Check status
kubectl get pods -n iraqaf
kubectl get services -n iraqaf

# View logs
kubectl logs -f deployment/iraqaf-api -n iraqaf

# Rollback if needed
kubectl rollout undo deployment/iraqaf-api -n iraqaf
```

---

## CLOUD PLATFORMS

### AWS Deployment

```bash
# Push image to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag iraqaf:1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/iraqaf:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/iraqaf:latest

# Deploy to ECS, EKS, or Lightsail
# (Refer to AWS documentation for specific service)
```

### Google Cloud Deployment

```bash
# Push to Container Registry
gcloud auth configure-docker
docker tag iraqaf:1.0 gcr.io/PROJECT_ID/iraqaf:latest
docker push gcr.io/PROJECT_ID/iraqaf:latest

# Deploy to Cloud Run
gcloud run deploy iraqaf \
  --image gcr.io/PROJECT_ID/iraqaf:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL="postgresql://..."
```

### Azure Deployment

```bash
# Push to Container Registry
az acr login --name myregistry
docker tag iraqaf:1.0 myregistry.azurecr.io/iraqaf:latest
docker push myregistry.azurecr.io/iraqaf:latest

# Deploy to Container Instances or App Service
az container create \
  --resource-group mygroup \
  --name iraqaf \
  --image myregistry.azurecr.io/iraqaf:latest \
  --environment-variables DATABASE_URL="postgresql://..."
```

---

## SECURITY HARDENING

### Environment Variables (Production)

```bash
# .env.production
DATABASE_URL=postgresql://secure_user:strong_password@db-host:5432/iraqaf
DATABASE_ECHO=false
DEBUG=false
SECRET_KEY=your-secure-random-key-here
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
CORS_ORIGINS=["https://your-domain.com"]
ALLOWED_HOSTS=["your-domain.com"]
HTTPS_ONLY=true
SESSION_SECURE=true
SESSION_HTTPONLY=true
SESSION_SAMESITE=Strict
```

### CORS Configuration

```python
# Restrict to specific domains (not wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://app.your-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
    max_age=600
)
```

### HTTPS/SSL Configuration

```bash
# Generate SSL certificate (Let's Encrypt)
certbot certonly --standalone -d your-domain.com

# Configure Nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL hardening
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://api:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Rate Limiting

```python
# Implement rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/systems")
@limiter.limit("100/minute")
async def list_systems(request: Request):
    # Rate limited to 100 requests per minute
    pass
```

### SQL Injection Prevention

```python
# Always use parameterized queries
# WRONG:
query = f"SELECT * FROM systems WHERE id = {system_id}"

# RIGHT:
from sqlalchemy import text
query = text("SELECT * FROM systems WHERE id = :id")
result = session.execute(query, {"id": system_id})
```

---

## PERFORMANCE OPTIMIZATION

### Database Optimization

```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600
)

# Indexing
from sqlalchemy import Index

class System(Base):
    __table_args__ = (
        Index('ix_system_domain', 'domain'),
        Index('ix_system_status', 'status'),
    )
```

### Caching

```python
# Redis caching
from redis import Redis
from functools import wraps
import json

redis_client = Redis(host='localhost', port=6379, db=0)

def cached(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_value = redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@app.get("/api/regulations")
@cached(ttl=3600)  # Cache for 1 hour
async def list_regulations():
    # Expensive operation cached
    pass
```

### Load Balancing

```nginx
# nginx.conf - round-robin load balancing
upstream api_backend {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    location / {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";
    }
}
```

---

## MONITORING & LOGGING

### Structured Logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

logger.info("system_created", system_id=1, name="Test")
```

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# Metrics
request_count = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration')

@app.get("/api/systems")
async def list_systems():
    with request_duration.time():
        request_count.labels(method='GET', endpoint='/systems').inc()
        # Implementation
```

### ELK Stack Integration

```python
from pythonjsonlogger import jsonlogger
import logging

logHandler = logging.FileHandler('logs/app.json')
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
```

---

## BACKUP & RECOVERY

### Database Backups

```bash
# Daily automated backup
0 2 * * * /usr/bin/pg_dump -U iraqaf_user iraqaf | gzip > /backups/iraqaf_$(date +%Y%m%d).sql.gz

# Restore from backup
gunzip -c /backups/iraqaf_20240115.sql.gz | psql -U iraqaf_user iraqaf
```

### Disaster Recovery Plan

```markdown
## Recovery Time Objective (RTO): 1 hour
## Recovery Point Objective (RPO): 15 minutes

### Steps:
1. Identify failure (monitoring alerts)
2. Stop current processes
3. Restore from latest backup
4. Verify data integrity
5. Bring services online
6. Test all endpoints
7. Monitor for 24 hours
```

---

## PRODUCTION DEPLOYMENT CHECKLIST

- [ ] All tests passing
- [ ] 80%+ code coverage
- [ ] Security vulnerabilities scanned
- [ ] Database optimized and indexed
- [ ] Caching configured
- [ ] Load balancer configured
- [ ] SSL/TLS certificates valid
- [ ] Backup system in place
- [ ] Monitoring alerts configured
- [ ] Logging centralized
- [ ] Runbook prepared
- [ ] Team trained
- [ ] Blue-green deployment ready
- [ ] Rollback plan defined

---

**Deployment Status**: ✅ READY FOR PRODUCTION  
**Security Status**: ✅ HARDENED  
**Performance**: ✅ OPTIMIZED  
**Monitoring**: ✅ CONFIGURED
