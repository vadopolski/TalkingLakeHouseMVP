# Docker Setup - Sales Analytics Chat Assistant

This guide shows you how to run the Sales Analytics Chat Assistant using Docker with a **local LLM** (no API keys needed!).

## What's Included

The Docker setup includes:
- **PostgreSQL** database with sample sales data (30 transactions)
- **Ollama** with llama3.2 model (local LLM - no API keys!)
- **Backend API** (FastAPI on port 8000)
- **Frontend UI** (React on port 5173)

## Prerequisites

**Only requirement: Docker Desktop**
- Windows/Mac: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
- Linux: Install `docker` and `docker-compose`

## Quick Start

### Windows

```bash
start-docker.bat
```

### Linux/Mac

```bash
chmod +x start-docker.sh
./start-docker.sh
```

That's it! The script will:
1. Start all Docker containers
2. Download the llama3.2 model (~2GB, one-time)
3. Initialize the database with sample data
4. Start the backend and frontend

## Access the Application

Once started, you can access:

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432
  - Database: `analytics_db`
  - User: `readonly_user`
  - Password: `readonly123`

## Try It Out!

Open http://localhost:5173 in your browser and try these questions:

### Sales Queries (MVP - User Story 1)
- "What were total sales this month?"
- "Show me top selling products"
- "What were sales last week?"
- "Total revenue yesterday"
- "Average sales this month"

The system will respond with:
- Natural language summary
- Bar chart or line chart visualization
- Data source citation

## Sample Data

The database includes 30+ sales transactions for the last 60 days:

**Products:**
- Laptop Pro 15 ($1,299.99)
- Wireless Mouse ($29.99)
- USB-C Hub ($49.99)
- Mechanical Keyboard ($149.99)
- Monitor 27" ($399.99)
- Webcam HD ($89.99)

**Date Range:** Last 60 days from today

## Managing Services

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Database only
docker-compose logs -f postgres
```

### Stop Services

```bash
docker-compose down
```

### Restart Services

```bash
docker-compose restart
```

### Rebuild After Code Changes

```bash
docker-compose down
docker-compose up -d --build
```

## Architecture

```
┌─────────────────┐
│   Frontend      │  http://localhost:5173
│   (React)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Backend API   │  http://localhost:8000
│   (FastAPI)     │
└────┬───────┬────┘
     │       │
     ▼       ▼
┌─────────┐ ┌─────────┐
│ Ollama  │ │PostgreSQL
│(llama3.2│ │ (Read-  │
└─────────┘ │  Only)  │
            └─────────┘
```

## How It Works (Constitutional Architecture)

1. **User asks question** in natural language
2. **Intent Classifier** determines query type (sales/traffic/conversion)
3. **Template Selector** picks best SQL template using similarity matching
4. **Parameter Extractor** finds dates, filters from query
5. **SQL Validator** checks against whitelist, blocks risky keywords
6. **LIMIT Injector** adds row limits for safety
7. **Query Executor** runs on read-only connection with timeout
8. **Response Formatter** creates text summary
9. **Chart Selector** picks visualization type
10. **Citation Generator** adds data source attribution

**No LLM API calls needed** - the system uses pattern matching and local Ollama only for optional enhancements!

## Troubleshooting

### Ollama model download is slow
The llama3.2 model is ~2GB and only downloads once. Subsequent starts are instant.

### Backend can't connect to database
```bash
# Check if PostgreSQL is healthy
docker-compose ps

# View database logs
docker-compose logs postgres
```

### Frontend shows connection error
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check backend logs
docker-compose logs backend
```

### Port conflicts (8000, 5173, 5432 already in use)
Edit `docker-compose.yml` to change port mappings:
```yaml
ports:
  - "8001:8000"  # Change 8000 to 8001
```

## Security Features

This setup enforces all constitutional principles:

✅ **Read-only database access** - `readonly_user` can only SELECT
✅ **Template-only SQL** - No dynamic SQL generation
✅ **Whitelisted tables** - Only `sales_transactions` and `website_visits`
✅ **Blocked keywords** - DROP, DELETE, UPDATE, INSERT, etc.
✅ **LIMIT enforcement** - All queries capped at 1000 rows
✅ **Query timeouts** - 30 second maximum
✅ **Rate limiting** - 10 queries/minute per user
✅ **Audit logging** - All queries logged

## Next Steps

### Extend with More Templates

1. Add SQL template to `templates/sql/your_template.json`
2. Add examples to `templates/few_shot_examples.json`
3. Rebuild: `docker-compose up -d --build backend`

### Connect Your Own Database

Edit `docker-compose.yml`:
```yaml
backend:
  environment:
    DATABASE_URL: postgresql://your_user:your_pass@your_host:5432/your_db
```

### Use Different LLM Model

```yaml
ollama:
  # After starting, pull different model:
  # docker exec ollama ollama pull llama2

backend:
  environment:
    OLLAMA_MODEL: llama2  # or mistral, codellama, etc.
```

## Support

For issues or questions:
- Check logs: `docker-compose logs`
- Review README.md for architecture details
- Open issue on GitHub

## Clean Up

To completely remove all containers and data:

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (deletes database data)
docker-compose down -v

# Remove images
docker rmi $(docker images -q "analytics*")
```
