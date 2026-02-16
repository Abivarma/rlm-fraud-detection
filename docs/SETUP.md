# Setup Guide

This guide will walk you through setting up the Fraud Detection RLM system.

## Prerequisites

- **Python 3.11+**
- **PostgreSQL 15+** (with pgvector extension) OR **Docker**
- **OpenAI API Key** (required)
- **Kaggle Account** (for dataset download)

## Quick Start with Docker (Recommended)

### 1. Clone and Navigate

```bash
cd RLM
```

### 2. Set Up Environment Variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your API keys:
```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Download Dataset

Option A - Manual:
```bash
# Visit https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
# Download creditcard.csv
# Place in backend/data/creditcard.csv
```

Option B - Kaggle API (requires setup):
```bash
pip install kaggle
python scripts/download_dataset.py --auto
```

### 4. Start with Docker Compose

```bash
docker-compose up -d
```

This will start:
- **PostgreSQL** with pgvector on port 5432
- **FastAPI backend** on port 8000
- **Streamlit dashboard** on port 8501

### 5. Access the Application

- **Streamlit Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1/

---

## Manual Setup (Without Docker)

### 1. Install PostgreSQL with pgvector

**macOS (Homebrew)**:
```bash
brew install postgresql@16
brew install pgvector
brew services start postgresql@16
```

**Ubuntu/Debian**:
```bash
sudo apt-get install postgresql-16 postgresql-16-pgvector
sudo systemctl start postgresql
```

**Windows**:
- Download PostgreSQL from https://www.postgresql.org/download/
- Install pgvector from https://github.com/pgvector/pgvector

### 2. Create Database

```bash
createdb fraud_detection
psql fraud_detection -c "CREATE EXTENSION vector;"
```

### 3. Set Up Python Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```bash
# API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here  # Optional

# Database (update if needed)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fraud_detection
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/fraud_detection

# Models
MAIN_MODEL=openai:gpt-4o
SUB_MODEL=openai:gpt-4o-mini
```

### 5. Download Dataset

```bash
python scripts/download_dataset.py
# Or download manually from Kaggle
```

### 6. Initialize Database

```bash
cd backend
python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"
```

### 7. Run the Application

**Terminal 1 - FastAPI Backend**:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Streamlit Dashboard**:
```bash
cd backend
streamlit run app/ui/streamlit_dashboard.py
```

---

## Verification

### Check Backend is Running

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "version": "0.1.0"}
```

### Check Database Connection

```bash
psql fraud_detection -c "SELECT version();"
psql fraud_detection -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

### Test API Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/analyze/naive \
  -H "Content-Type: application/json" \
  -d '{"transactions": [...]}'
```

---

## Troubleshooting

### Database Connection Issues

**Error**: `could not connect to server`

**Solution**:
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS

# Check connection
psql -U postgres -h localhost
```

### pgvector Not Found

**Error**: `extension "vector" does not exist`

**Solution**:
```bash
# Install pgvector
# macOS
brew install pgvector

# Ubuntu/Debian
sudo apt-get install postgresql-16-pgvector

# Then create extension
psql fraud_detection -c "CREATE EXTENSION vector;"
```

### Dataset Not Found

**Error**: `Dataset not found at ./data/creditcard.csv`

**Solution**:
```bash
# Create data directory
mkdir -p backend/data

# Download dataset
python scripts/download_dataset.py

# Or manually place creditcard.csv in backend/data/
```

### OpenAI API Key Issues

**Error**: `AuthenticationError: Invalid API key`

**Solution**:
1. Verify key in `.env` file
2. Check key is valid at https://platform.openai.com/api-keys
3. Ensure `.env` is in `backend/` directory
4. Restart the application

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'pydantic_ai_rlm'`

**Solution**:
```bash
# Ensure you're in virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt

# If pydantic-ai-rlm is not available, check:
pip install pydantic-ai-rlm
# If not published yet, you may need to install from source
```

---

## Next Steps

- [Usage Guide](USAGE.md) - Learn how to use the system
- [API Documentation](http://localhost:8000/docs) - Explore the API
- [Architecture Overview](ARCHITECTURE.md) - Understand the system design

## Support

For issues or questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs in the console output
- Open an issue on GitHub
