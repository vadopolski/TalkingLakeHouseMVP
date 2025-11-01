#!/bin/bash

echo "================================"
echo "Sales Analytics Chat Assistant"
echo "Docker Setup with Local LLM"
echo "================================"
echo ""

echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed or not running"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "[1/4] Starting Docker services (PostgreSQL, Ollama, Backend, Frontend)..."
docker-compose up -d

echo ""
echo "[2/4] Waiting for services to be healthy..."
sleep 10

echo ""
echo "[3/4] Checking if Ollama model is available..."
if ! docker exec ollama ollama list | grep -q llama3.2; then
    echo "[INFO] Pulling llama3.2 model (this may take a few minutes)..."
    docker exec ollama ollama pull llama3.2
else
    echo "[INFO] llama3.2 model already available"
fi

echo ""
echo "[4/4] Services are starting up..."
echo ""
echo "================================"
echo "Services Status:"
echo "================================"
echo "PostgreSQL Database: http://localhost:5432"
echo "  - Database: analytics_db"
echo "  - User: readonly_user"
echo "  - Password: readonly123"
echo ""
echo "Ollama (Local LLM): http://localhost:11434"
echo "  - Model: llama3.2"
echo ""
echo "Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "Frontend UI: http://localhost:5173"
echo "================================"
echo ""
echo "To view logs:"
echo "  - All services:    docker-compose logs -f"
echo "  - Backend only:    docker-compose logs -f backend"
echo "  - Frontend only:   docker-compose logs -f frontend"
echo ""
echo "To stop all services:"
echo "  - docker-compose down"
echo ""
echo "Press Ctrl+C to exit logs view..."
sleep 2

docker-compose logs -f
