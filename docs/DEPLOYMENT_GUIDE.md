# ATLAS AI - Deployment Guide

## Deployment Options

This guide covers deploying Atlas AI to production environments.

---

## Option 1: Docker Deployment (Recommended)

### Prerequisites
- Docker 20.0+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

### Step 1: Create Dockerfile for Backend

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY .env.example ./.env

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 2: Create Dockerfile for Frontend

Create `ui/Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Streamlit
RUN pip install streamlit httpx plotly pandas

# Copy frontend code
COPY app.py .
COPY ../backend/app ./backend/app

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Step 3: Docker Compose

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
    volumes:
      - ./vector_db:/app/vector_db
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./ui
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    environment:
      - API_BASE_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  vector_db:
  data:
```

### Step 4: Deploy

```bash
# Build and start containers
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop containers
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

**Access:**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000/docs

---

## Option 2: Railway Deployment

### Prerequisites
- Railway account (free tier available)
- GitHub repository

### Backend Deployment

1. **Create `railway.toml`:**
```toml
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10

[[services]]
name = "atlas-backend"
```

2. **Deploy:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to backend folder
railway link

# Deploy
railway up
```

3. **Environment Variables:**
```bash
railway variables set GROQ_API_KEY=your_key_here
railway variables set EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### Frontend Deployment

1. **Create separate Railway service**
2. **Set start command:**
```bash
streamlit run ui/app.py --server.port $PORT --server.address 0.0.0.0
```

3. **Link backend URL:**
```bash
railway variables set API_BASE_URL=https://your-backend.railway.app
```

---

## Option 3: Render Deployment

### Backend on Render

1. **Create `render.yaml`:**
```yaml
services:
  - type: web
    name: atlas-backend
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: GROQ_API_KEY
        sync: false
      - key: EMBEDDING_MODEL
        value: sentence-transformers/all-MiniLM-L6-v2
```

2. **Deploy:**
- Connect GitHub repo to Render
- Select `backend` folder as root
- Add environment variables
- Deploy

### Frontend on Render

1. **Create separate web service**
2. **Build command:**
```bash
pip install streamlit httpx plotly pandas
```

3. **Start command:**
```bash
streamlit run ui/app.py --server.port=$PORT --server.address=0.0.0.0
```

---

## Option 4: AWS EC2 Deployment

### Instance Setup

1. **Launch EC2 Instance:**
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.medium (2 vCPU, 4GB RAM)
   - Security Group: Allow ports 22, 8000, 8501

2. **SSH into instance:**
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

3. **Install Dependencies:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip nginx -y

# Install Python packages
pip3 install -r requirements.txt
```

4. **Setup Systemd Services:**

Create `/etc/systemd/system/atlas-backend.service`:
```ini
[Unit]
Description=Atlas AI Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Atlas/backend
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/atlas-frontend.service`:
```ini
[Unit]
Description=Atlas AI Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Atlas
Environment="PATH=/home/ubuntu/.local/bin"
ExecStart=/home/ubuntu/.local/bin/streamlit run ui/app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Start Services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable atlas-backend atlas-frontend
sudo systemctl start atlas-backend atlas-frontend
sudo systemctl status atlas-backend atlas-frontend
```

6. **Configure Nginx Reverse Proxy:**

Create `/etc/nginx/sites-available/atlas`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:8501/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/atlas /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Environment Variables

Required variables for production:

```bash
# Backend (.env)
GROQ_API_KEY=your_groq_api_key_here
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
LOG_LEVEL=INFO
VECTOR_DB_PATH=./vector_db
CORS_ORIGINS=https://your-frontend-domain.com

# Frontend
API_BASE_URL=https://your-backend-domain.com
```

---

## Database Persistence

### Vector Store Backup

```bash
# Backup vector database
tar -czf vector_db_backup_$(date +%Y%m%d).tar.gz vector_db/

# Restore
tar -xzf vector_db_backup_20260207.tar.gz
```

### Automated Backups (Cron)

```bash
# Add to crontab
0 2 * * * /home/ubuntu/backup_vector_db.sh
```

Create `/home/ubuntu/backup_vector_db.sh`:
```bash
#!/bin/bash
cd /home/ubuntu/Atlas
tar -czf /backups/vector_db_$(date +%Y%m%d).tar.gz vector_db/
# Keep only last 7 days
find /backups -name "vector_db_*.tar.gz" -mtime +7 -delete
```

---

## Monitoring & Logging

### Application Logs

```bash
# Backend logs
journalctl -u atlas-backend -f

# Frontend logs
journalctl -u atlas-frontend -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Frontend check
curl http://localhost:8501/_stcore/health
```

### Monitoring Setup (Optional)

Install Prometheus + Grafana for metrics:

```bash
# Install Prometheus
sudo apt install prometheus -y

# Configure scraping (add to /etc/prometheus/prometheus.yml)
scrape_configs:
  - job_name: 'atlas-backend'
    static_configs:
      - targets: ['localhost:8000']
```

---

## SSL/TLS Setup

### Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

Update Nginx config to redirect HTTP→HTTPS:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... rest of config
}
```

---

## Performance Optimization

### 1. Enable Gzip Compression

Add to Nginx config:
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 2. Cache Static Assets

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. Increase Uvicorn Workers

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Use Redis for Session Storage

```python
# Update backend to use Redis
import redis

redis_client = redis.Redis(host='localhost', port=6379)
```

---

## Security Checklist

- ✅ Enable firewall (UFW)
- ✅ Use HTTPS (SSL/TLS)
- ✅ Add authentication (JWT tokens)
- ✅ Rate limiting (nginx limit_req)
- ✅ Update dependencies regularly
- ✅ Disable debug mode in production
- ✅ Use environment variables for secrets
- ✅ Set secure CORS origins
- ✅ Enable HSTS headers
- ✅ Regular security audits

---

## Troubleshooting Production Issues

### High CPU Usage
```bash
# Check process usage
top -u ubuntu

# Limit workers
uvicorn app.main:app --workers 2 --limit-concurrency 100
```

### Memory Leaks
```bash
# Monitor memory
watch -n 1 free -h

# Restart services periodically
sudo systemctl restart atlas-backend
```

### Disk Space Full
```bash
# Check disk usage
df -h

# Clear old logs
sudo journalctl --vacuum-time=7d

# Rotate logs
sudo logrotate -f /etc/logrotate.conf
```

---

## Rollback Strategy

1. **Tag releases:**
```bash
git tag v1.0.0
git push origin v1.0.0
```

2. **Rollback:**
```bash
git checkout v1.0.0
docker-compose up -d --build
```

3. **Database restore:**
```bash
tar -xzf vector_db_backup_20260207.tar.gz
sudo systemctl restart atlas-backend
```

---

## Support & Maintenance

**Weekly Tasks:**
- Review application logs
- Check disk space
- Update dependencies

**Monthly Tasks:**
- Security patches
- Backup verification
- Performance analysis

**Quarterly Tasks:**
- Disaster recovery test
- Security audit
- Capacity planning
