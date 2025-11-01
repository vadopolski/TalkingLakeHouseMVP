# Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Start Docker Desktop

Make sure Docker Desktop is running on your computer:
- **Windows**: Open Docker Desktop from Start menu
- **Mac**: Open Docker Desktop from Applications
- **Linux**: Ensure Docker daemon is running: `sudo systemctl start docker`

### Step 2: Run the Application

**Windows:**
```bash
start-docker.bat
```

**Linux/Mac:**
```bash
chmod +x start-docker.sh
./start-docker.sh
```

### Step 3: Open Your Browser

Go to: **http://localhost:5173**

## 🎯 Try These Questions

Once the app is running, try asking:

1. **"What were total sales this month?"**
2. **"Show me top selling products"**
3. **"Sales from last week"**
4. **"Total revenue yesterday"**

You'll get:
- ✅ Natural language answer
- ✅ Beautiful chart
- ✅ Data source citation

## 📊 What's Running?

- **Frontend**: http://localhost:5173 (React chat interface)
- **Backend API**: http://localhost:8000 (FastAPI)
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)
- **Database**: PostgreSQL with 30+ sample transactions
- **Local LLM**: Ollama with llama3.2 (no API keys!)

## 🛑 Stop the Application

```bash
docker-compose down
```

## 📖 Need More Help?

See **README-DOCKER.md** for:
- Troubleshooting
- Viewing logs
- Adding your own database
- Customizing SQL templates
- Architecture details

## 💡 No API Keys Required!

This setup uses **Ollama** (local LLM) so you don't need:
- ❌ OpenAI API key
- ❌ Anthropic API key
- ❌ Any cloud services

Everything runs **locally** on your computer!
