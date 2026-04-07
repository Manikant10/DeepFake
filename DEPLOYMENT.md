# Deployment Guide

This guide will help you deploy the DeepFake Recognition System in production.

## Quick Start (Development/Testing)

### Windows
```bash
# Run the quick deploy script
quick-deploy.bat

# Or manually:
docker-compose --profile production up -d --build
```

### Linux/Mac
```bash
# Make the script executable
chmod +x quick-deploy.sh

# Run the quick deploy script
./quick-deploy.sh

# Or manually:
docker-compose --profile production up -d --build
```

## Production Deployment

### Prerequisites
- Docker and Docker Compose
- Domain name (for SSL)
- SSL certificate (Let's Encrypt recommended)

### Step 1: Configuration

1. **Copy environment template**
```bash
cp .env.example .env
```

2. **Edit configuration**
Edit `.env` file with your production values:
- `DOMAIN`: Your domain name
- `SECRET_KEY`: Generate a strong secret key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `EMAIL`: Your email for SSL certificate

### Step 2: SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)
```bash
# Install certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com --email admin@yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
sudo chown $USER:$USER nginx/ssl/*.pem
```

#### Option B: Self-signed (Development)
```bash
# The deployment script will create a self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/privkey.pem \
    -out nginx/ssl/fullchain.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"
```

### Step 3: Deploy

#### Automated Deployment (Recommended)
```bash
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows
deploy.bat
```

#### Manual Deployment
```bash
# Create directories
mkdir -p data/{postgres,redis,uploads,results,models,logs}
mkdir -p nginx/ssl

# Deploy services
docker-compose --profile production up -d --build

# Setup monitoring (optional)
docker-compose --profile monitoring up -d
```

### Step 4: Verify Deployment

1. **Check service health**
```bash
# Backend health
curl -f http://localhost:8000/health

# Frontend
curl -f http://localhost:3000

# Database
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping
```

2. **Access the application**
- Frontend: `https://yourdomain.com`
- API Docs: `https://yourdomain.com/docs`
- Admin Panel: `https://yourdomain.com/admin`

### Step 5: Post-Deployment

1. **Change default admin password**
   - Login with admin/Admin123!@#
   - Change password immediately

2. **Configure monitoring**
   - Grafana: `http://localhost:3001`
   - Prometheus: `http://localhost:9090`

3. **Setup backups**
   - Configure backup script in crontab
   - Test backup restoration

## Service Management

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop specific service
docker-compose stop backend
```

### Update Services
```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up -d --build
```

### Database Management
```bash
# Connect to database
docker-compose exec postgres psql -U deepfake_user -d deepfake_db

# Backup database
docker-compose exec postgres pg_dump -U deepfake_user deepfake_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U deepfake_user deepfake_db < backup.sql
```

## Monitoring

### Grafana Dashboards
- URL: `http://localhost:3001`
- Username: `admin`
- Password: `admin123`

### Prometheus Metrics
- URL: `http://localhost:9090`
- Targets: System metrics, application metrics

### Key Metrics to Monitor
- API response time
- Error rates
- Database connections
- Memory usage
- Disk space
- Analysis queue length

## Security Considerations

### Firewall Configuration
```bash
# Allow only necessary ports
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### SSL Certificate Renewal
```bash
# Add to crontab
0 12 * * * /usr/bin/certbot renew --quiet && docker-compose restart nginx
```

### Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker-compose pull
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Services not starting**
```bash
# Check logs
docker-compose logs service-name

# Check resource usage
docker stats

# Restart service
docker-compose restart service-name
```

2. **Database connection issues**
```bash
# Check database status
docker-compose exec postgres pg_isready

# Check connection string
echo $DATABASE_URL
```

3. **SSL certificate issues**
```bash
# Check certificate expiration
openssl x509 -in nginx/ssl/fullchain.pem -noout -dates

# Test SSL configuration
openssl s_client -connect yourdomain.com:443
```

4. **High memory usage**
```bash
# Check container resource usage
docker stats

# Optimize Docker resources
# Edit docker-compose.yml to add resource limits
```

### Performance Optimization

1. **Database Optimization**
```sql
-- Create indexes
CREATE INDEX ON analyses(user_id, created_at);
CREATE INDEX ON analyses(label);
```

2. **Redis Optimization**
```bash
# Check Redis memory usage
docker-compose exec redis redis-cli info memory

# Optimize Redis configuration
# Edit redis.conf in docker-compose
```

3. **Application Optimization**
```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Enable caching
# Check Redis caching is working
```

## Backup and Recovery

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/deepfake"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T postgres pg_dump -U deepfake_user deepfake_db > $BACKUP_DIR/db_$DATE.sql

# Backup uploads
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz data/uploads/

# Backup configuration
cp .env $BACKUP_DIR/env_$DATE
cp docker-compose.yml $BACKUP_DIR/compose_$DATE.yml

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### Recovery Process
```bash
# Stop services
docker-compose down

# Restore database
docker-compose up -d postgres
docker-compose exec -T postgres psql -U deepfake_user deepfake_db < backup/db_20231201_120000.sql

# Restore uploads
tar -xzf backup/uploads_20231201_120000.tar.gz

# Start all services
docker-compose up -d
```

## Scaling

### Horizontal Scaling
```bash
# Scale backend services
docker-compose up -d --scale backend=3 --scale celery-worker=2

# Add load balancer configuration
# Update nginx.conf for multiple backend instances
```

### Vertical Scaling
```bash
# Increase resource limits
# Edit docker-compose.yml:
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## Support

For additional support:
1. Check the logs: `docker-compose logs -f`
2. Review the troubleshooting section
3. Check the API documentation: `http://yourdomain.com/docs`
4. Open an issue on GitHub
