#!/bin/bash

# DeepFake Recognition System - Quick Deploy Script
# Simplified deployment for development/testing

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "DeepFake Recognition System - Quick Deploy"
echo "=========================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create .env if not exists
if [ ! -f .env ]; then
    echo -e "${BLUE}Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your configuration.${NC}"
    echo -e "${YELLOW}Using default values for quick deployment...${NC}"
fi

# Create directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p data/{postgres,redis,uploads,results,models,logs}
mkdir -p nginx/ssl

# Create self-signed certificate
if [ ! -f nginx/ssl/fullchain.pem ]; then
    echo -e "${BLUE}Creating self-signed SSL certificate...${NC}"
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/C=US/ST=State/L=City/O=DeepFake/CN=localhost"
fi

# Deploy
echo -e "${BLUE}Starting deployment...${NC}"
docker-compose --profile production up -d --build

# Wait for services
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 30

# Check health
echo -e "${BLUE}Checking service health...${NC}"
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}Backend is healthy!${NC}"
else
    echo -e "${YELLOW}Backend not ready yet, please wait a moment...${NC}"
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}Frontend is healthy!${NC}"
else
    echo -e "${YELLOW}Frontend not ready yet, please wait a moment...${NC}"
fi

# Show access info
echo ""
echo -e "${GREEN}========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Access URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Health Check: http://localhost:8000/health"
echo ""
echo "Management Commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo ""
echo "Default Admin Credentials:"
echo "  Username: admin"
echo "  Password: Admin123!@#"
echo ""
echo -e "${YELLOW}IMPORTANT: Change default password immediately!${NC}"
echo ""
