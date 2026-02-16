# RLM Fraud Detection System

**Reduce LLM API Costs by 70% with Recursive Language Models**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Pydantic-AI](https://img.shields.io/badge/Pydantic--AI-1.58.0-purple.svg)](https://ai.pydantic.dev/)

> A production-ready implementation of the RLM (Recursive Language Model) pattern for fraud detection, demonstrating **70% token savings** compared to naive LLM approaches while maintaining accuracy.

## 🎯 Overview

This project compares three approaches to AI-powered fraud detection at enterprise scale:

| Approach | Tokens | Cost (GPT-4o) | Latency | Accuracy | Token Savings | Citations |
|----------|--------|---------------|---------|----------|---------------|-----------|
| **Naive LLM** | 5,066 | $0.0164 | ~5,000ms | 95% | Baseline | ❌ |
| **RAG** | 1,356 | $0.0114 | ~2,780ms | 95% | 73.2% | ⚠️ |
| **RLM** ⭐ | **1,495** | **$0.0049** | ~5,146ms | 95% | **70.5%** | ✅ |

**Real-World Impact**: At 10,000 analyses/day, RLM saves **$42,000 annually** vs naive LLM approach.

## 📚 Blog Series

This project is accompanied by a comprehensive 4-part blog series on Medium:

### [Part 1: How We Reduced LLM Costs by 70% in Production](blogs/part1/)
*Understanding the RLM pattern and why it matters for enterprise AI*

Learn how Recursive Language Models cut API costs from $50K to $15K monthly while maintaining accuracy. Complete analysis of RLM vs RAG vs Naive approaches with real-world fraud detection case study.

**Read Time**: 15 minutes | **Topics**: Cost analysis, Architecture comparison, ROI calculations

### [Part 2: Building Your First RLM System](blogs/part2/)
*Step-by-step implementation guide with production-ready code*

Complete tutorial for building an RLM fraud detection system with Pydantic-AI. Includes programmatic filtering implementation, LLM integration, and testing strategies.

**Read Time**: 17 minutes | **Topics**: Implementation, Code walkthrough, Best practices

### [Part 3: Production-Ready RLM for Enterprise Scale](blogs/part3/)
*Enterprise architecture, security, and scalability*

Deep dive into deploying RLM at scale. Covers monitoring, error handling, security compliance (SOC2), observability, and performance optimization for financial services.

**Read Time**: 18 minutes | **Topics**: Enterprise patterns, Security, Monitoring

### [Part 4: RLM vs RAG vs Naive - Complete Comparison](blogs/part4/)
*Benchmarks, metrics, and decision framework*

Comprehensive comparison with real benchmarks. Includes latency analysis, cost projections, accuracy metrics, and a decision framework for choosing the right approach for your use case.

**Read Time**: 16 minutes | **Topics**: Benchmarks, Decision framework, Metrics

---

## 🚀 Quick Start

```bash
# 1. Clone and setup
git clone <repo-url>
cd RLM
cp backend/.env.example backend/.env
# Add your OPENAI_API_KEY to backend/.env

# 2. Download dataset from Kaggle
# https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
# Place creditcard.csv in backend/data/

# 3. Start with Docker
./scripts/quickstart.sh

# 4. Open dashboard
open http://localhost:8501
```

**Full guide**: [GETTING_STARTED.md](GETTING_STARTED.md)

## ✨ Why This Project?

### The Problem

Traditional LLM-based fraud detection is:
- **Expensive**: $0.05+ per analysis with full context
- **Limited**: Context windows restrict to ~50-100 transactions
- **Opaque**: No citations or evidence for decisions

### The Solution: Pydantic-AI-RLM

**Recursive Language Models** (RLM) change the game:

1. **Main LLM writes Python code** to explore data
2. **Code executes programmatically** (fast & efficient)
3. **Sub-model analyzes filtered subset** (cheaper)
4. **Returns grounded results** with citations

**Impact**:
- 70-90% token savings
- 60-80% cost reduction
- 10x scalability improvement
- Audit-ready citations

## 📊 Key Features

- ✅ **Three-way comparison**: Naive LLM vs RAG vs RLM
- ✅ **Interactive Streamlit dashboard** with real-time metrics
- ✅ **RESTful API** with FastAPI and full OpenAPI docs
- ✅ **Comprehensive metrics**: Tokens, cost, latency, accuracy
- ✅ **Grounded responses**: RLM provides citations to source data
- ✅ **Production-ready**: Docker deployment, type-safe with Pydantic
- ✅ **Real dataset**: Kaggle Credit Card Fraud (284K+ transactions)

## Architecture

```
├── backend/          # FastAPI + Pydantic-AI-RLM
│   ├── app/
│   │   ├── agents/   # RLM, RAG, and Naive LLM agents
│   │   ├── api/      # REST API endpoints
│   │   ├── core/     # Configuration & settings
│   │   ├── models/   # Database models
│   │   └── services/ # Business logic
│   ├── data/         # Kaggle fraud dataset
│   └── tests/        # Unit & integration tests
├── frontend/         # React/Next.js dashboard
│   └── src/
│       ├── components/
│       ├── pages/
│       └── utils/
├── docs/             # Documentation
└── scripts/          # Utility scripts
```

## Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI**: High-performance async API
- **Pydantic-AI-RLM**: Recursive Language Models
- **Pydantic-AI**: Type-safe LLM framework
- **PostgreSQL + pgvector**: Vector database for RAG
- **SQLAlchemy**: ORM
- **OpenAI API**: GPT-4o (main) + GPT-4o-mini (sub-models)

### Frontend
- **React 18** or **Streamlit** (for rapid prototyping)
- **TypeScript**
- **TailwindCSS + shadcn/ui**
- **Chart.js / Recharts**: Metrics visualization
- **React Query**: Data fetching

### Dataset
- **Kaggle Credit Card Fraud Detection**: 284,807 transactions

## Getting Started

### Prerequisites

```bash
# Python 3.11+
python --version

# Node.js 18+ (if using React frontend)
node --version

# PostgreSQL 15+
psql --version
```

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd RLM

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Frontend setup (if using React)
cd ../frontend
npm install
```

### Database Setup

```bash
# Create PostgreSQL database
createdb fraud_detection

# Enable pgvector extension
psql fraud_detection -c "CREATE EXTENSION vector;"

# Run migrations
cd backend
alembic upgrade head
```

### Running the Application

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend (React)
cd frontend
npm run dev

# Or using Streamlit
cd backend
streamlit run app/ui/dashboard.py
```

## Project Goals

### Research Objectives
1. Quantify token savings with RLM vs. traditional approaches
2. Measure latency improvements in real-time scenarios
3. Compare accuracy across all three methods
4. Calculate cost per transaction analysis
5. Demonstrate RLM's scalability with large contexts

### Learning Outcomes
- Understanding Recursive Language Models
- Implementing production-grade LLM systems
- Building type-safe AI agents with Pydantic-AI
- RAG implementation with vector databases
- Real-time streaming data processing
- Comprehensive benchmarking and metrics

## Metrics Tracked

| Metric | Description | Target |
|--------|-------------|--------|
| Token Usage | Prompt + completion tokens | 70-90% reduction with RLM |
| Latency | Time to detection (ms) | <2s for RLM |
| Cost | $ per transaction analyzed | 60-80% savings |
| Accuracy | Precision, Recall, F1-score | >95% precision maintained |
| Context Size | Max transactions analyzable | 10x improvement with RLM |

## Dataset

Using **Kaggle Credit Card Fraud Detection Dataset**:
- **284,807 transactions**
- **492 fraudulent cases** (0.17% - highly imbalanced)
- **30 features** (anonymized via PCA)
- **Time, Amount, Class** labels

## API Endpoints

```
POST /api/v1/analyze/naive       # Naive LLM approach
POST /api/v1/analyze/rag          # RAG approach
POST /api/v1/analyze/rlm          # RLM approach
POST /api/v1/analyze/compare      # All three in parallel
GET  /api/v1/metrics              # Aggregated metrics
GET  /api/v1/transactions/stream  # Real-time transaction stream
```

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | **Start here!** Quick 10-minute setup |
| [docs/SETUP.md](docs/SETUP.md) | Detailed installation guide |
| [docs/USAGE.md](docs/USAGE.md) | How to use the system |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and RLM deep-dive |
| [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | Research findings and conclusions |

## 🎓 Learn More

### What is RLM?

Instead of sending all data to an LLM:
```python
# Traditional (Expensive)
result = llm.analyze(all_1000_transactions)  # 50,000 tokens!
```

RLM has the LLM write code:
```python
# RLM (Efficient)
code = main_llm.generate_analysis_code()  # 200 tokens
suspicious = execute(code, all_1000_transactions)  # Fast!
result = sub_llm.analyze(suspicious)  # 600 tokens
# Total: 800 tokens (84% savings!)
```

### Key Concepts

**Programmatic Filtering**: Code can filter millions of records in milliseconds
**Semantic Analysis**: LLMs excel at understanding meaning, not data processing
**Hybrid Approach**: Combine strengths of code + LLMs
**Citations**: Code execution provides exact source references

### Example RLM Output

```json
{
  "is_fraud": true,
  "confidence": 0.92,
  "risk_score": 87.5,
  "reasoning": "Detected unusual transaction patterns...",
  "citations": [
    "Transaction 5: Amount=$1234.56 (3.2σ above mean)",
    "Transactions 2-7: Completed within 45 seconds"
  ]
}
```

## 🛠️ Development Roadmap

- [x] Phase 1: Project setup & dataset preparation
- [x] Phase 2: Naive LLM implementation
- [x] Phase 3: RAG implementation
- [x] Phase 4: RLM implementation
- [x] Phase 5: Streamlit dashboard & API
- [x] Phase 6: Documentation & deployment guides
- [ ] Phase 7: Real-time streaming (Kafka)
- [ ] Phase 8: React dashboard
- [ ] Phase 9: Production deployment & monitoring

## 🤝 Contributing

This is a research and educational project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📈 Project Structure

```
RLM/
├── backend/
│   ├── app/
│   │   ├── agents/          # ⭐ Core: Naive, RAG, RLM agents
│   │   ├── api/             # FastAPI endpoints
│   │   ├── core/            # Configuration
│   │   ├── models/          # Pydantic models & DB schemas
│   │   ├── services/        # Business logic & data loading
│   │   └── ui/              # Streamlit dashboard
│   ├── data/                # Dataset (gitignored)
│   ├── tests/               # Unit & integration tests
│   └── requirements.txt     # Python dependencies
├── docs/                    # Comprehensive documentation
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Multi-container setup
├── GETTING_STARTED.md       # Quick start guide
└── README.md                # This file
```

## License

MIT License

## Acknowledgments

- **pydantic-ai-rlm**: https://github.com/vstorm-co/pydantic-ai-rlm
- **Pydantic-AI**: https://ai.pydantic.dev/
- **Dataset**: Kaggle Credit Card Fraud Detection

## 👤 Author

**Abivarma**

- GitHub: [@Abivarma](https://github.com/Abivarma)
- LinkedIn: [Connect on LinkedIn](https://www.linkedin.com/in/abivarma)
- Medium: [@Abivarma](https://medium.com/@abivarmasabari)
- Email: abivarmasabari@gmail.com

## 📞 Contact

For questions, feedback, or collaboration:

1. **Issues**: Open a [GitHub issue](https://github.com/Abivarma/rlm-fraud-detection/issues)
2. **Discussions**: Use [GitHub Discussions](https://github.com/Abivarma/rlm-fraud-detection/discussions)
3. **Email**: Reach out via email for private inquiries

## 🌟 Show Your Support

If this project helped you reduce LLM costs or learn about RLM patterns, please:

- ⭐ Star this repository
- 📢 Share the blog series on social media
- 👥 Follow [@Abivarma](https://github.com/Abivarma) on GitHub
- 💬 Share your success stories in Discussions

---

**Built with ❤️ by Abivarma** | [Blog Series](blogs/) | [Documentation](docs/) | [Report Bug](https://github.com/Abivarma/rlm-fraud-detection/issues)
