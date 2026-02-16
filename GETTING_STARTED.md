# Getting Started with Fraud Detection RLM

Welcome! This guide will get you up and running in **under 10 minutes**.

## 🎯 Quick Start (Docker - Recommended)

### Step 1: Prerequisites

Install Docker:
- **Mac**: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

### Step 2: Get an OpenAI API Key

1. Visit https://platform.openai.com/api-keys
2. Create a new API key
3. Save it (you'll need it in Step 4)

### Step 3: Download the Dataset

**Option A - Manual (Easiest)**:
1. Visit https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
2. Click "Download" (requires free Kaggle account)
3. Extract `creditcard.csv` from the ZIP
4. Place it in `backend/data/creditcard.csv`

**Option B - Kaggle API**:
```bash
# Install Kaggle CLI
pip install kaggle

# Configure API (see https://www.kaggle.com/docs/api)
# Download kaggle.json to ~/.kaggle/kaggle.json

# Run download script
python scripts/download_dataset.py --auto
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit backend/.env and add your API key:
# OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Step 5: Run Quick Start Script

```bash
./scripts/quickstart.sh
```

That's it! The script will:
- ✅ Build Docker images
- ✅ Start PostgreSQL + pgvector
- ✅ Launch FastAPI backend
- ✅ Start Streamlit dashboard

### Step 6: Access the Dashboard

Open your browser to **http://localhost:8501**

🎉 You're ready to go!

---

## 📊 Using the Dashboard

### 1. Configure Analysis (Sidebar)

**Sample Type**:
- `Random Mix`: Mix of fraud + legitimate (recommended for first try)
- `Known Fraud`: Test with known fraudulent transactions
- `Legitimate Only`: Test with legitimate transactions
- `Consecutive Batch`: Sequential transactions from dataset

**Number of Transactions**:
- Start with **20 transactions**
- Try up to 100 to see RLM's advantage

**Fraud Ratio** (Random Mix only):
- Set to **0.2** (20% fraud) for realistic testing

### 2. Run Analysis

Click **"🚀 Run Analysis"**

Watch as all three approaches analyze the transactions in parallel!

### 3. Compare Results

You'll see:

**Approach Results**:
- Fraud detection decision (✓ or 🚨)
- Confidence score
- Risk score
- Tokens used
- Cost
- Latency
- Reasoning
- Suspicious patterns
- Citations (RLM only!)

**Performance Charts**:
- Token usage comparison
- Cost comparison
- Latency comparison

**Key Metrics**:
- Token savings (RLM vs Naive)
- Cost savings
- Agreement between approaches

---

## 🔬 Understanding the Results

### What to Look For

1. **Token Savings**:
   - RLM should use **70-90% fewer tokens** than Naive
   - Watch this increase as you add more transactions!

2. **Cost Savings**:
   - RLM should be **60-80% cheaper** than Naive
   - This adds up fast at scale

3. **Scalability**:
   - Try increasing transactions:
     - 20 → All work fine
     - 50 → Naive starts struggling
     - 100+ → Only RLM scales

4. **Citations (RLM)**:
   - RLM provides **grounded responses**
   - Click "Citations" expander to see evidence
   - Example: "Transaction 5: Amount=$1234.56 (3.2σ outlier)"

### Example Results (20 transactions, 20% fraud)

| Metric | Naive | RAG | RLM |
|--------|-------|-----|-----|
| Tokens | 5,000 | 3,500 | 800 |
| Cost | $0.016 | $0.012 | $0.003 |
| Latency | 2.5s | 2.8s | 1.8s |
| Savings | - | 30% | **84%** |

---

## 🚀 Next Steps

### For Learning

1. **Try Different Scenarios**:
   - Known fraud (should detect 100%)
   - Legitimate only (should NOT detect fraud)
   - Large batches (100+ transactions)

2. **Explore the Code**:
   ```bash
   # Look at the three agents
   backend/app/agents/naive_agent.py
   backend/app/agents/rag_agent.py
   backend/app/agents/rlm_agent.py  # The magic happens here!
   ```

3. **Read the Documentation**:
   - [Architecture Overview](docs/ARCHITECTURE.md)
   - [Usage Guide](docs/USAGE.md)
   - [Project Summary](docs/PROJECT_SUMMARY.md)

### For Research

1. **Experiment with Prompts**:
   - Modify system prompts in agents
   - Test different fraud detection strategies
   - Measure accuracy improvements

2. **Add New Patterns**:
   - Extend RAG knowledge base
   - Add custom fraud indicators
   - Implement new detection logic

3. **Benchmark Different Models**:
   - Try GPT-4o vs GPT-4o-mini
   - Test Anthropic Claude
   - Compare accuracy/cost tradeoffs

### For Production

1. **Deploy to Cloud**:
   - AWS/GCP/Azure
   - Kubernetes deployment
   - Horizontal scaling

2. **Integrate with Your System**:
   - Use REST API
   - Stream real transactions
   - Build custom UI

3. **Monitor Performance**:
   - Track token usage
   - Monitor costs
   - Measure accuracy

---

## 🛠️ Troubleshooting

### Dashboard Won't Load

**Problem**: "Connection refused" at http://localhost:8501

**Solution**:
```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs streamlit

# Restart services
docker-compose restart
```

### API Key Error

**Problem**: "AuthenticationError: Invalid API key"

**Solution**:
1. Verify key in `backend/.env`
2. Check key starts with `sk-`
3. Test key at https://platform.openai.com/playground
4. Restart containers: `docker-compose restart`

### Dataset Not Found

**Problem**: "Dataset not found at ./data/creditcard.csv"

**Solution**:
```bash
# Check file exists
ls -lh backend/data/creditcard.csv

# If not, download from Kaggle
# See Step 3 above
```

### Out of Memory

**Problem**: Docker runs out of memory with large datasets

**Solution**:
1. Increase Docker memory (Docker Desktop → Settings → Resources)
2. Limit transaction count in dashboard
3. Use smaller batches

### Slow Performance

**Problem**: Analysis takes >30 seconds

**Solution**:
1. Reduce number of transactions
2. Check internet connection (API calls)
3. Verify Docker has enough CPU (Docker Desktop → Settings)

---

## 📚 Resources

### Documentation

- [Setup Guide](docs/SETUP.md) - Detailed setup instructions
- [Usage Guide](docs/USAGE.md) - How to use the system
- [Architecture](docs/ARCHITECTURE.md) - System design
- [Project Summary](docs/PROJECT_SUMMARY.md) - Research findings

### API Documentation

- FastAPI Docs: http://localhost:8000/docs
- Interactive API Explorer: http://localhost:8000/redoc

### External Resources

- [Pydantic-AI-RLM](https://github.com/vstorm-co/pydantic-ai-rlm)
- [Pydantic AI](https://ai.pydantic.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://docs.streamlit.io/)

---

## 🤝 Getting Help

### Common Issues

Check [Troubleshooting](#troubleshooting) section above

### Questions?

- Review documentation in `docs/` folder
- Check API docs at http://localhost:8000/docs
- Look at code examples in `backend/app/agents/`

### Found a Bug?

- Check logs: `docker-compose logs`
- Review error messages
- Check configuration in `backend/.env`

---

## 🎉 Success Checklist

- [ ] Docker containers running
- [ ] Dashboard accessible at http://localhost:8501
- [ ] API docs at http://localhost:8000/docs
- [ ] Dataset loaded successfully
- [ ] First analysis complete
- [ ] Token savings observed
- [ ] RLM citations visible

**All checked?** Congratulations! You're now running a production-grade fraud detection system with Pydantic-AI-RLM!

---

## What's Next?

### Immediate Actions

1. **Run Your First Analysis**:
   - Use "Random Mix" with 20 transactions
   - Observe the 3-way comparison
   - Check token savings

2. **Scale Up**:
   - Try 50 transactions
   - Then 100 transactions
   - See RLM's advantage grow!

3. **Explore RLM**:
   - Click "Citations" in RLM results
   - See grounded evidence
   - Understand the magic

### Next Hour

1. **Read the Architecture**:
   - Understand how RLM works
   - Learn about code generation
   - See token savings calculation

2. **Try the API**:
   - Visit http://localhost:8000/docs
   - Test endpoints directly
   - Make your own API calls

3. **Explore the Code**:
   - Read `backend/app/agents/rlm_agent.py`
   - Understand the implementation
   - See Pydantic-AI-RLM in action

### This Week

1. **Customize the System**:
   - Add your own fraud patterns
   - Modify detection logic
   - Experiment with prompts

2. **Run Benchmarks**:
   - Test different transaction counts
   - Measure accuracy
   - Calculate ROI

3. **Plan Production Deployment**:
   - Review deployment docs
   - Plan integration
   - Estimate costs

---

**Ready to revolutionize fraud detection with RLM? Let's go! 🚀**
