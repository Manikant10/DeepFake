#!/bin/bash

# DeepFake Recognition System - Production Deployment Script
# This script automates the complete deployment process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="deepfake-recognition"
DOMAIN=${DOMAIN:-"yourdomain.com"}
EMAIL=${EMAIL:-"admin@yourdomain.com"}

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f .env ]; then
        log_warning ".env file not found. Creating from template..."
        cp .env.example .env
        log_warning "Please edit .env file with your configuration before continuing."
        log_warning "Press Enter to continue or Ctrl+C to exit..."
        read -r
    fi
    
    log_success "Prerequisites check completed"
}

setup_ssl() {
    log_info "Setting up SSL certificates with Let's Encrypt..."
    
    # Create nginx directory
    mkdir -p nginx/ssl
    
    # Install certbot if not present
    if ! command -v certbot &> /dev/null; then
        log_info "Installing certbot..."
        sudo apt-get update
        sudo apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Generate SSL certificate
    if [ ! -f "nginx/ssl/fullchain.pem" ]; then
        log_info "Generating SSL certificate for $DOMAIN..."
        sudo certbot certonly --nginx -d $DOMAIN --email $EMAIL --agree-tos --no-eff-email --staging
        
        # Copy certificates
        sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/
        sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/
        sudo chown $USER:$USER nginx/ssl/*.pem
        
        log_success "SSL certificate generated"
    else
        log_info "SSL certificate already exists"
    fi
}

create_directories() {
    log_info "Creating necessary directories..."
    
    # Create data directories
    mkdir -p data/{postgres,redis,uploads,results,models,logs}
    mkdir -p nginx/{ssl,conf.d}
    mkdir -p monitoring/{prometheus,grafana}
    
    # Set permissions
    chmod 755 data/uploads
    chmod 755 data/results
    chmod 755 data/models
    chmod 755 data/logs
    
    log_success "Directories created"
}

setup_database() {
    log_info "Setting up database..."
    
    # Start PostgreSQL container
    docker-compose up -d postgres
    
    # Wait for PostgreSQL to be ready
    log_info "Waiting for PostgreSQL to be ready..."
    until docker-compose exec postgres pg_isready -U deepfake_user -d deepfake_db; do
        sleep 2
    done
    
    # Run database migrations
    log_info "Running database migrations..."
    docker-compose run --rm backend python -c "
from backend.database import create_tables
create_tables(engine)
print('Database tables created successfully')
"
    
    log_success "Database setup completed"
}

deploy_application() {
    log_info "Deploying application..."
    
    # Build and start all services
    docker-compose --profile production up -d --build
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    
    # Wait for backend
    until curl -f http://localhost:8000/health > /dev/null 2>&1; do
        sleep 5
        log_info "Waiting for backend service..."
    done
    
    # Wait for frontend
    until curl -f http://localhost:3000 > /dev/null 2>&1; do
        sleep 5
        log_info "Waiting for frontend service..."
    done
    
    log_success "Application deployed successfully"
}

setup_monitoring() {
    log_info "Setting up monitoring..."
    
    # Start monitoring services
    docker-compose --profile monitoring up -d
    
    # Wait for Prometheus
    until curl -f http://localhost:9090 > /dev/null 2>&1; do
        sleep 5
        log_info "Waiting for Prometheus..."
    done
    
    # Wait for Grafana
    until curl -f http://localhost:3001 > /dev/null 2>&1; do
        sleep 5
        log_info "Waiting for Grafana..."
    done
    
    log_success "Monitoring setup completed"
}

create_admin_user() {
    log_info "Creating admin user..."
    
    # Create admin user via API
    curl -X POST http://localhost:8000/auth/register \
        -H "Content-Type: application/json" \
        -d '{
            "email": "admin@yourdomain.com",
            "username": "admin",
            "password": "Admin123!@#",
            "full_name": "System Administrator"
        }'
    
    log_success "Admin user created"
}

run_tests() {
    log_info "Running deployment tests..."
    
    # Test backend health
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        exit 1
    fi
    
    # Test frontend
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        log_success "Frontend test passed"
    else
        log_error "Frontend test failed"
        exit 1
    fi
    
    # Test database connection
    if docker-compose exec postgres pg_isready > /dev/null 2>&1; then
        log_success "Database connection test passed"
    else
        log_error "Database connection test failed"
        exit 1
    fi
    
    log_success "All tests passed"
}

show_access_info() {
    log_success "Deployment completed successfully!"
    echo ""
    echo "=== Access Information ==="
    echo "Frontend: https://$DOMAIN"
    echo "API Documentation: https://$DOMAIN/docs"
    echo "Admin Panel: https://$DOMAIN/admin"
    echo ""
    echo "=== Monitoring ==="
    echo "Prometheus: http://localhost:9090"
    echo "Grafana: http://localhost:3001 (admin/admin123)"
    echo ""
    echo "=== Default Credentials ==="
    echo "Admin Username: admin"
    echo "Admin Password: Admin123!@#"
    echo ""
    echo "=== Management Commands ==="
    echo "View logs: docker-compose logs -f"
    echo "Stop services: docker-compose down"
    echo "Update services: docker-compose pull && docker-compose up -d"
    echo ""
    log_warning "Please change the default admin password immediately!"
}

main() {
    echo "========================================"
    echo "DeepFake Recognition System Deployment"
    echo "========================================"
    echo ""
    
    # Check if running as root for SSL setup
    if [ "$EUID" -ne 0 ] && [ ! -f "nginx/ssl/fullchain.pem" ]; then
        log_warning "SSL setup requires root privileges. You may be prompted for password."
    fi
    
    check_prerequisites
    create_directories
    
    # Setup SSL if domain is provided
    if [ "$DOMAIN" != "yourdomain.com" ]; then
        setup_ssl
    else
        log_warning "Using self-signed certificate for development"
        # Create self-signed certificate for development
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/privkey.pem \
            -out nginx/ssl/fullchain.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    fi
    
    setup_database
    deploy_application
    setup_monitoring
    create_admin_user
    run_tests
    show_access_info
}

# Handle script arguments
case "${1:-}" in
    "ssl-only")
        setup_ssl
        ;;
    "db-only")
        setup_database
        ;;
    "monitoring-only")
        setup_monitoring
        ;;
    "test-only")
        run_tests
        ;;
    *)
        main
        ;;
esac
