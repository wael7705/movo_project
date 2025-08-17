# 🚀 دليل النشر الشامل - MOVO Delivery Platform

## نظرة عامة | Overview

هذا الدليل يغطي جميع جوانب نشر منصة MOVO للتوصيل في بيئات مختلفة، من التطوير إلى الإنتاج.

This guide covers all aspects of deploying the MOVO Delivery Platform in different environments, from development to production.

## 📋 المتطلبات الأساسية | Prerequisites

### النظام | System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50GB minimum
- **CPU**: 2 cores minimum, 4 cores recommended

### البرامج المطلوبة | Software Requirements
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Redis**: 6.0+ (للذاكرة المؤقتة)
- **Nginx**: 1.18+ (كخادم وكيل عكسي)
- **Docker**: 20.10+ (اختياري)

## 🏗️ إعداد البيئة | Environment Setup

### 1. إعداد الخادم | Server Setup

#### Ubuntu/Debian
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات الأساسية
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server

# تثبيت Git
sudo apt install -y git

# إنشاء مستخدم للنظام
sudo adduser movo
sudo usermod -aG sudo movo
```

#### CentOS/RHEL
```bash
# تحديث النظام
sudo yum update -y

# تثبيت المتطلبات الأساسية
sudo yum install -y python3 python3-pip postgresql postgresql-server nginx redis

# بدء الخدمات
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. إعداد قاعدة البيانات | Database Setup

```bash
# الدخول كـ postgres
sudo -u postgres psql

# إنشاء قاعدة البيانات والمستخدم
CREATE DATABASE movo_system;
CREATE USER movo_user WITH PASSWORD 'secure_password_2025';
GRANT ALL PRIVILEGES ON DATABASE movo_system TO movo_user;
ALTER USER movo_user CREATEDB;
\q
```

### 3. إعداد Python | Python Setup

```bash
# إنشاء مجلد المشروع
sudo mkdir -p /opt/movo
sudo chown movo:movo /opt/movo

# الدخول كمستخدم movo
sudo su - movo

# استنساخ المشروع
cd /opt/movo
git clone <repository-url> backend
cd backend

# إنشاء البيئة الافتراضية
python3 -m venv .venv
source .venv/bin/activate

# تثبيت المتطلبات
pip install -r requirements.txt
```

## 🔧 إعداد التكوين | Configuration Setup

### 1. ملف الإعدادات | Configuration File

```python
# /opt/movo/backend/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # إعدادات الإنتاج
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # قاعدة البيانات
    database_url: str = "postgresql+asyncpg://movo_user:secure_password_2025@localhost:5432/movo_system"
    
    # الأمان
    secret_key: str = "your-super-secret-key-change-this-in-production"
    
    # الذكاء الاصطناعي
    enable_monitoring: bool = True
    ai_model_path: str = "/opt/movo/models/"
    
    # التوصيل
    delivery_fee_per_meter: float = 0.001
    max_delivery_distance: float = 50.0
    free_delivery_threshold: float = 50.0
    
    class Config:
        env_file = ".env"
```

### 2. متغيرات البيئة | Environment Variables

```bash
# /opt/movo/backend/.env
DEBUG=False
DATABASE_URL=postgresql+asyncpg://movo_user:secure_password_2025@localhost:5432/movo_system
SECRET_KEY=your-super-secret-key-change-this-in-production
AI_ENABLED=True
MONITORING_ENABLED=True
LOG_LEVEL=INFO
```

### 3. إعدادات Nginx | Nginx Configuration

```nginx
# /etc/nginx/sites-available/movo
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # إعادة توجيه HTTP إلى HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # شهادات SSL
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # إعدادات SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # الأمان
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # الملفات الثابتة
    location /static/ {
        alias /opt/movo/backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

### 4. تفعيل موقع Nginx | Enable Nginx Site

```bash
# إنشاء رابط رمزي
sudo ln -s /etc/nginx/sites-available/movo /etc/nginx/sites-enabled/

# اختبار التكوين
sudo nginx -t

# إعادة تحميل Nginx
sudo systemctl reload nginx
```

## 🚀 النشر باستخدام Docker | Docker Deployment

### 1. Dockerfile

```dockerfile
# /opt/movo/backend/Dockerfile
FROM python:3.9-slim

# تثبيت المتطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# إنشاء مستخدم غير root
RUN useradd --create-home --shell /bin/bash movo

# تعيين مجلد العمل
WORKDIR /app

# نسخ متطلبات Python
COPY requirements.txt .

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# تغيير الملكية
RUN chown -R movo:movo /app

# التبديل للمستخدم
USER movo

# فتح المنفذ
EXPOSE 8000

# أمر التشغيل
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Docker Compose

```yaml
# /opt/movo/docker-compose.yml
version: '3.8'

services:
  app:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://movo_user:secure_password_2025@db:5432/movo_system
      - DEBUG=False
      - SECRET_KEY=your-super-secret-key
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=movo_system
      - POSTGRES_USER=movo_user
      - POSTGRES_PASSWORD=secure_password_2025
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### 3. تشغيل Docker

```bash
# بناء وتشغيل الخدمات
cd /opt/movo
docker-compose up -d

# مراقبة السجلات
docker-compose logs -f app

# إيقاف الخدمات
docker-compose down
```

## 🔄 النشر المستمر | Continuous Deployment

### 1. GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.4
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.KEY }}
        script: |
          cd /opt/movo/backend
          git pull origin main
          source .venv/bin/activate
          pip install -r requirements.txt
          sudo systemctl restart movo
```

### 2. Systemd Service

```ini
# /etc/systemd/system/movo.service
[Unit]
Description=MOVO Delivery Platform
After=network.target postgresql.service

[Service]
Type=exec
User=movo
Group=movo
WorkingDirectory=/opt/movo/backend
Environment=PATH=/opt/movo/backend/.venv/bin
ExecStart=/opt/movo/backend/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 3. تفعيل الخدمة | Enable Service

```bash
# إعادة تحميل systemd
sudo systemctl daemon-reload

# تفعيل الخدمة
sudo systemctl enable movo

# بدء الخدمة
sudo systemctl start movo

# مراقبة الحالة
sudo systemctl status movo

# مراقبة السجلات
sudo journalctl -u movo -f
```

## 🔒 الأمان | Security

### 1. جدار الحماية | Firewall

```bash
# إعداد UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 2. شهادات SSL | SSL Certificates

```bash
# تثبيت Certbot
sudo apt install certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# تجديد تلقائي
sudo crontab -e
# إضافة السطر التالي:
0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. مراقبة الأمان | Security Monitoring

```bash
# تثبيت Fail2ban
sudo apt install fail2ban

# إعداد Fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 📊 المراقبة | Monitoring

### 1. Prometheus & Grafana

```yaml
# /opt/movo/monitoring/docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
```

### 2. Log Management

```bash
# إعداد logrotate
sudo tee /etc/logrotate.d/movo << EOF
/opt/movo/backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 movo movo
    postrotate
        systemctl reload movo
    endscript
}
EOF
```

## 🔄 النسخ الاحتياطي | Backup

### 1. قاعدة البيانات | Database Backup

```bash
#!/bin/bash
# /opt/movo/scripts/backup_db.sh

BACKUP_DIR="/opt/movo/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="movo_system"

# إنشاء مجلد النسخ الاحتياطي
mkdir -p $BACKUP_DIR

# نسخ احتياطي لقاعدة البيانات
pg_dump -h localhost -U movo_user $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# ضغط الملف
gzip $BACKUP_DIR/db_backup_$DATE.sql

# حذف النسخ الاحتياطية القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Database backup completed: db_backup_$DATE.sql.gz"
```

### 2. جدولة النسخ الاحتياطي | Backup Schedule

```bash
# إضافة إلى crontab
sudo crontab -e

# نسخ احتياطي يومي في 2 صباحاً
0 2 * * * /opt/movo/scripts/backup_db.sh

# نسخ احتياطي أسبوعي يوم الأحد
0 3 * * 0 /opt/movo/scripts/full_backup.sh
```

## 🚨 استكشاف الأخطاء | Troubleshooting

### 1. مشاكل شائعة | Common Issues

#### خطأ في الاتصال بقاعدة البيانات
```bash
# فحص حالة PostgreSQL
sudo systemctl status postgresql

# فحص الاتصال
psql -h localhost -U movo_user -d movo_system

# فحص السجلات
sudo tail -f /var/log/postgresql/postgresql-*.log
```

#### خطأ في التطبيق
```bash
# فحص حالة الخدمة
sudo systemctl status movo

# مراقبة السجلات
sudo journalctl -u movo -f

# اختبار التطبيق
curl http://localhost:8000/health
```

#### خطأ في Nginx
```bash
# اختبار التكوين
sudo nginx -t

# فحص السجلات
sudo tail -f /var/log/nginx/error.log

# إعادة تحميل Nginx
sudo systemctl reload nginx
```

### 2. أدوات التشخيص | Diagnostic Tools

```bash
# فحص استخدام الموارد
htop
df -h
free -h

# فحص الشبكة
netstat -tulpn
ss -tulpn

# فحص العمليات
ps aux | grep movo
```

## 📈 تحسين الأداء | Performance Optimization

### 1. تحسين قاعدة البيانات

```sql
-- إنشاء فهارس
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_chat_messages_order_id ON chat_messages(order_id);

-- تحليل الجداول
ANALYZE orders;
ANALYZE chat_messages;
```

### 2. تحسين التطبيق

```python
# إعدادات Gunicorn
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
```

### 3. تحسين Nginx

```nginx
# إعدادات الأداء
worker_processes auto;
worker_connections 1024;
keepalive_timeout 65;
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

## 🎯 الخلاصة | Conclusion

هذا الدليل يغطي جميع جوانب نشر منصة MOVO للتوصيل. تأكد من:

1. **الأمان**: تحديث جميع البرامج بانتظام
2. **المراقبة**: مراقبة الأداء والسجلات
3. **النسخ الاحتياطي**: عمل نسخ احتياطية منتظمة
4. **التحديثات**: تحديث النظام والمكتبات
5. **الاختبار**: اختبار النظام بانتظام

This guide covers all aspects of deploying the MOVO Delivery Platform. Make sure to:

1. **Security**: Update all software regularly
2. **Monitoring**: Monitor performance and logs
3. **Backup**: Perform regular backups
4. **Updates**: Update system and libraries
5. **Testing**: Test the system regularly

---

**MOVO Delivery Platform** - منصة التوصيل الذكية | The Smart Delivery Platform 