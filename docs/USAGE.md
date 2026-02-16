

# Usage Guide

Learn how to use the Fraud Detection RLM system to analyze transactions and compare different approaches.

## Table of Contents

1. [Streamlit Dashboard](#streamlit-dashboard)
2. [REST API](#rest-api)
3. [Python SDK](#python-sdk)
4. [Understanding Results](#understanding-results)
5. [Best Practices](#best-practices)

---

## Streamlit Dashboard

The easiest way to interact with the system is through the Streamlit dashboard.

### Accessing the Dashboard

```bash
# If using Docker:
open http://localhost:8501

# Or directly:
streamlit run backend/app/ui/streamlit_dashboard.py
```

### Using the Dashboard

1. **Check Dataset Status** (sidebar):
   - Verify the dataset is loaded
   - View dataset statistics

2. **Configure Analysis** (sidebar):
   - **Sample Type**: Choose how to select transactions
     - `Random Mix`: Mix of fraud and legitimate transactions
     - `Known Fraud`: Only known fraudulent transactions
     - `Legitimate Only`: Only legitimate transactions
     - `Consecutive Batch`: Sequential transactions from dataset

   - **Number of Transactions**: 5-100 transactions
   - **Fraud Ratio** (for Random Mix): Proportion of fraud cases

3. **Run Analysis**:
   - Click "🚀 Run Analysis"
   - Wait for all three approaches to complete
   - View comparative results

4. **Interpret Results**:
   - Each approach shows:
     - Fraud detection decision
     - Confidence score
     - Risk score
     - Token usage
     - Cost
     - Latency
     - Reasoning
     - Suspicious patterns
     - Citations (RLM only)

---

## REST API

### Base URL

```
http://localhost:8000/api/v1
```

### Endpoints

#### 1. Analyze with Naive LLM

```bash
POST /api/v1/analyze/naive
```

**Request Body**:
```json
{
  "transactions": [
    {
      "time": 0.0,
      "amount": 149.62,
      "v1": -1.359807,
      "v2": -0.072781,
      "v3": 2.536347,
      ...
      "v28": -0.021053
    }
  ],
  "include_metrics": true
}
```

**Response**:
```json
{
  "result": {
    "is_fraud": false,
    "confidence": 0.85,
    "risk_score": 25.0,
    "reasoning": "Transaction patterns appear normal...",
    "suspicious_patterns": [],
    "citations": [],
    "flagged_transactions": []
  },
  "metrics": {
    "approach": "naive",
    "total_tokens": 5000,
    "prompt_tokens": 4500,
    "completion_tokens": 500,
    "latency_ms": 2500,
    "cost_usd": 0.05,
    "transactions_analyzed": 1
  },
  "approach": "naive"
}
```

#### 2. Analyze with RAG

```bash
POST /api/v1/analyze/rag
```

Similar request/response format as Naive.

#### 3. Analyze with RLM

```bash
POST /api/v1/analyze/rlm
```

**Response includes citations**:
```json
{
  "result": {
    "is_fraud": true,
    "confidence": 0.92,
    "risk_score": 87.5,
    "reasoning": "Code analysis revealed suspicious patterns...",
    "suspicious_patterns": [
      "Unusual transaction amount (3+ std dev)",
      "Rapid succession detected"
    ],
    "citations": [
      "Transaction 5: Amount=$1234.56 (outlier)",
      "Transactions 2-7: Completed within 45 seconds"
    ],
    "flagged_transactions": [2, 5, 7]
  },
  "metrics": {
    "approach": "rlm",
    "total_tokens": 800,
    "prompt_tokens": 600,
    "completion_tokens": 200,
    "latency_ms": 1800,
    "cost_usd": 0.008,
    "transactions_analyzed": 10
  }
}
```

#### 4. Compare All Approaches

```bash
POST /api/v1/analyze/compare
```

**Response**:
```json
{
  "naive": { /* AnalysisResponse */ },
  "rag": { /* AnalysisResponse */ },
  "rlm": { /* AnalysisResponse */ },
  "summary": {
    "token_usage": {
      "naive": 5000,
      "rag": 3500,
      "rlm": 800
    },
    "token_savings_pct": 84.0,
    "latency_ms": { ... },
    "cost_usd": { ... },
    "consensus": true,
    "agreement_count": 3
  }
}
```

### cURL Examples

**Naive Analysis**:
```bash
curl -X POST http://localhost:8000/api/v1/analyze/naive \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

**Comparison**:
```bash
curl -X POST http://localhost:8000/api/v1/analyze/compare \
  -H "Content-Type: application/json" \
  -d @sample_request.json | jq .
```

---

## Python SDK

### Direct Usage

```python
import asyncio
from app.services.fraud_service import fraud_service
from app.services.data_loader import data_loader

# Load sample transactions
transactions = data_loader.get_sample_transactions(n=20, fraud_ratio=0.2)

# Analyze with RLM
async def analyze():
    result, metrics = await fraud_service.analyze_rlm(transactions)
    print(f"Fraud detected: {result.is_fraud}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Tokens used: {metrics.total_tokens}")
    print(f"Cost: ${metrics.cost_usd:.4f}")

asyncio.run(analyze())
```

### Comparison Analysis

```python
async def compare():
    comparison = await fraud_service.compare_all(transactions)

    print(f"Token savings: {comparison.summary['token_savings_pct']:.1f}%")
    print(f"Consensus: {comparison.summary['consensus']}")

    # Access individual results
    print(f"Naive decision: {comparison.naive.result.is_fraud}")
    print(f"RAG decision: {comparison.rag.result.is_fraud}")
    print(f"RLM decision: {comparison.rlm.result.is_fraud}")

asyncio.run(compare())
```

---

## Understanding Results

### Fraud Detection Result

- **is_fraud**: Boolean indicating fraud detection
- **confidence**: Confidence score (0-1)
  - 0.0-0.3: Low confidence
  - 0.3-0.7: Medium confidence
  - 0.7-1.0: High confidence
- **risk_score**: Risk score (0-100)
  - 0-30: Low risk
  - 30-70: Medium risk
  - 70-100: High risk

### Metrics Interpretation

#### Token Usage
- **Naive**: Highest usage (~5,000 tokens)
  - Sends all transaction data to main model
  - Limited to ~50-100 transactions
- **RAG**: Medium usage (~3,500 tokens)
  - Retrieves relevant patterns
  - Can handle ~100-200 transactions
- **RLM**: Lowest usage (~800 tokens)
  - Programmatic filtering
  - Can handle 10,000+ transactions
  - **70-90% savings vs Naive**

#### Cost Analysis
- Based on GPT-4o pricing:
  - Input: $2.50 per 1M tokens
  - Output: $10.00 per 1M tokens
- RLM typically 60-80% cheaper than Naive

#### Latency
- **Naive**: 2-4 seconds (depends on transaction count)
- **RAG**: 2-3 seconds (includes retrieval overhead)
- **RLM**: 1.5-3 seconds (code execution + LLM calls)

### Suspicious Patterns

Common patterns detected:
- **Unusual amounts**: Statistical outliers (>3 std dev)
- **Rapid succession**: Multiple transactions in short time
- **Feature anomalies**: Unusual V1-V28 PCA feature values
- **Amount clustering**: Similar amounts in sequence
- **Time-based patterns**: Unusual timing patterns

### Citations (RLM Only)

RLM provides grounded responses with citations:
```
"Transaction 5: Amount=$1234.56 (3.2σ above mean)"
"Transactions 2-7: Completed within 45 seconds"
```

This shows *exactly* what the analysis found.

---

## Best Practices

### Choosing the Right Approach

**Use Naive when**:
- Very small transaction sets (<20)
- Highest accuracy is critical
- Cost/tokens not a concern

**Use RAG when**:
- Medium transaction sets (50-100)
- Need historical pattern matching
- Want balanced performance/cost

**Use RLM when** (Recommended!):
- Large transaction sets (100+)
- Cost optimization is important
- Need explainable results with citations
- Want scalable solution

### Optimizing Performance

1. **Batch Size**:
   - Naive: Max 50 transactions
   - RAG: Max 100 transactions
   - RLM: Up to 10,000 transactions

2. **Fraud Ratio**:
   - For testing: Use 20-30% fraud ratio
   - Real-world: Expect ~0.17% fraud rate

3. **API Usage**:
   - Use `/analyze/compare` sparingly (3x the cost)
   - Cache results for similar transaction patterns
   - Use `/analyze/rlm` for production workloads

4. **Cost Management**:
   - Monitor token usage in metrics
   - Set transaction limits based on budget
   - Consider using sub_model (gpt-4o-mini) for RLM

### Testing Strategies

**Test with Known Fraud**:
```python
fraud_cases = data_loader.get_fraud_cases(n=10)
result, metrics = await fraud_service.analyze_rlm(fraud_cases)
# Should detect fraud with high confidence
```

**Test with Legitimate Transactions**:
```python
legit_cases = data_loader.get_legitimate_cases(n=10)
result, metrics = await fraud_service.analyze_rlm(legit_cases)
# Should NOT detect fraud
```

**Test Mixed Scenarios**:
```python
mixed = data_loader.get_sample_transactions(n=50, fraud_ratio=0.3)
result, metrics = await fraud_service.analyze_rlm(mixed)
# Check flagged_transactions list
```

---

## Example Workflows

### Workflow 1: Quick Test

```bash
# 1. Start dashboard
streamlit run backend/app/ui/streamlit_dashboard.py

# 2. Select "Known Fraud" sample type
# 3. Set 10 transactions
# 4. Click "Run Analysis"
# 5. Observe all three approaches detect fraud
```

### Workflow 2: Performance Comparison

```python
import asyncio
from app.services.fraud_service import fraud_service
from app.services.data_loader import data_loader

async def benchmark():
    # Test with increasing transaction counts
    for n in [10, 25, 50, 100]:
        transactions = data_loader.get_sample_transactions(n=n)
        comparison = await fraud_service.compare_all(transactions)

        print(f"\n=== {n} Transactions ===")
        print(f"Token savings: {comparison.summary['token_savings_pct']:.1f}%")
        print(f"Cost - Naive: ${comparison.naive.metrics.cost_usd:.4f}")
        print(f"Cost - RLM: ${comparison.rlm.metrics.cost_usd:.4f}")

asyncio.run(benchmark())
```

### Workflow 3: Production Deployment

```python
# In production, use RLM for all analyses
async def production_analysis(user_transactions):
    try:
        result, metrics = await fraud_service.analyze_rlm(user_transactions)

        # Log metrics for monitoring
        logger.info(f"Analysis complete: tokens={metrics.total_tokens}, "
                   f"cost=${metrics.cost_usd:.4f}, "
                   f"latency={metrics.latency_ms:.0f}ms")

        # Alert if fraud detected
        if result.is_fraud and result.confidence > 0.8:
            send_fraud_alert(result)

        return result
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise
```

---

## Next Steps

- [Architecture Overview](ARCHITECTURE.md) - Understand the system
- [API Documentation](http://localhost:8000/docs) - Full API reference
- [Deployment Guide](DEPLOYMENT.md) - Deploy to production
