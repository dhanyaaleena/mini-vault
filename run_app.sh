#!/bin/bash

echo "Starting Mini Vault Application"

mkdir -p data

echo "Stopping existing containers"
docker-compose down --remove-orphans

echo "Building and starting application"
docker-compose up --build -d

echo "⏳ Waiting for application to start..."
sleep 10

# Show status
echo "Application Status:"
docker-compose ps


echo "Application URLs:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
