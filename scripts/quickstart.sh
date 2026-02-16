#!/bin/bash

# Fraud Detection RLM - Quick Start Script

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Fraud Detection RLM System - Quick Start                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed"
    echo "Please install Docker from: https://www.docker.com/get-started"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: Docker Compose is not installed"
    echo "Please install Docker Compose"
    exit 1
fi

echo "✓ Docker is installed"
echo ""

# Check for .env file
if [ ! -f "backend/.env" ]; then
    echo "Creating .env file from template..."
    cp backend/.env.example backend/.env

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  IMPORTANT: Configure your API keys"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Please edit backend/.env and add your OpenAI API key:"
    echo "  OPENAI_API_KEY=sk-your-openai-api-key-here"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
    echo ""
fi

# Check for API key
if ! grep -q "sk-" backend/.env 2>/dev/null; then
    echo "⚠️  Warning: OpenAI API key not found in backend/.env"
    echo "The application may not work without a valid API key."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for dataset
if [ ! -f "backend/data/creditcard.csv" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Dataset Not Found"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "The Kaggle Credit Card Fraud dataset is required."
    echo ""
    echo "Option 1: Manual Download (Recommended)"
    echo "  1. Visit: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud"
    echo "  2. Click 'Download' (requires Kaggle account)"
    echo "  3. Extract creditcard.csv"
    echo "  4. Place in: backend/data/creditcard.csv"
    echo ""
    echo "Option 2: Automatic Download (requires Kaggle API setup)"
    echo "  Run: python scripts/download_dataset.py --auto"
    echo ""
    read -p "Have you downloaded the dataset? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please download the dataset first, then run this script again."
        exit 1
    fi

    # Check again
    if [ ! -f "backend/data/creditcard.csv" ]; then
        echo "❌ Error: Dataset still not found at backend/data/creditcard.csv"
        exit 1
    fi
fi

echo "✓ Dataset found"
echo ""

# Build and start containers
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting Services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Building Docker images (this may take a few minutes)..."
docker-compose build

echo ""
echo "Starting containers..."
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                    🎉 SUCCESS! 🎉                              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Services are running:"
    echo ""
    echo "  📊 Streamlit Dashboard:  http://localhost:8501"
    echo "  🔌 API Documentation:    http://localhost:8000/docs"
    echo "  ❤️  Health Check:         http://localhost:8000/health"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Next Steps:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Open Streamlit Dashboard: http://localhost:8501"
    echo "2. Select transaction sample type"
    echo "3. Click 'Run Analysis'"
    echo "4. Compare Naive LLM vs RAG vs RLM approaches!"
    echo ""
    echo "Useful Commands:"
    echo "  View logs:     docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart:       docker-compose restart"
    echo ""
    echo "Documentation:"
    echo "  Setup Guide:   docs/SETUP.md"
    echo "  Usage Guide:   docs/USAGE.md"
    echo "  Architecture:  docs/ARCHITECTURE.md"
    echo ""
else
    echo ""
    echo "❌ Error: Services failed to start"
    echo ""
    echo "View logs with: docker-compose logs"
    exit 1
fi
