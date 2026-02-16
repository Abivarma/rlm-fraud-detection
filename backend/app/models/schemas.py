"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class ApproachType(str, Enum):
    """Analysis approach types."""

    NAIVE = "naive"
    RAG = "rag"
    RLM = "rlm"


class Transaction(BaseModel):
    """Single credit card transaction."""

    time: float = Field(..., description="Time elapsed since first transaction (seconds)")
    amount: float = Field(..., ge=0, description="Transaction amount")
    v1: float = Field(..., description="PCA feature 1")
    v2: float = Field(..., description="PCA feature 2")
    v3: float = Field(..., description="PCA feature 3")
    v4: float = Field(..., description="PCA feature 4")
    v5: float = Field(..., description="PCA feature 5")
    v6: float = Field(..., description="PCA feature 6")
    v7: float = Field(..., description="PCA feature 7")
    v8: float = Field(..., description="PCA feature 8")
    v9: float = Field(..., description="PCA feature 9")
    v10: float = Field(..., description="PCA feature 10")
    v11: float = Field(..., description="PCA feature 11")
    v12: float = Field(..., description="PCA feature 12")
    v13: float = Field(..., description="PCA feature 13")
    v14: float = Field(..., description="PCA feature 14")
    v15: float = Field(..., description="PCA feature 15")
    v16: float = Field(..., description="PCA feature 16")
    v17: float = Field(..., description="PCA feature 17")
    v18: float = Field(..., description="PCA feature 18")
    v19: float = Field(..., description="PCA feature 19")
    v20: float = Field(..., description="PCA feature 20")
    v21: float = Field(..., description="PCA feature 21")
    v22: float = Field(..., description="PCA feature 22")
    v23: float = Field(..., description="PCA feature 23")
    v24: float = Field(..., description="PCA feature 24")
    v25: float = Field(..., description="PCA feature 25")
    v26: float = Field(..., description="PCA feature 26")
    v27: float = Field(..., description="PCA feature 27")
    v28: float = Field(..., description="PCA feature 28")
    class_label: Optional[int] = Field(
        None, description="Actual label: 0=legitimate, 1=fraud (for evaluation)"
    )

    # Optional metadata
    transaction_id: Optional[str] = Field(None, description="Unique transaction identifier")
    user_id: Optional[str] = Field(None, description="User/card identifier")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for analysis."""
        return self.model_dump(exclude={"class_label", "transaction_id", "user_id"})

    def to_analysis_context(self) -> str:
        """Convert to string format for LLM context."""
        features = {f"V{i}": getattr(self, f"v{i}") for i in range(1, 29)}
        return f"Time: {self.time}s, Amount: ${self.amount:.2f}, Features: {features}"


class TransactionBatch(BaseModel):
    """Batch of transactions for analysis."""

    transactions: List[Transaction] = Field(..., min_length=1)
    user_id: Optional[str] = Field(None, description="User/card identifier")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("transactions")
    @classmethod
    def validate_batch_size(cls, v: List[Transaction]) -> List[Transaction]:
        """Validate batch size is reasonable."""
        if len(v) > 10000:
            raise ValueError("Batch size cannot exceed 10,000 transactions")
        return v


class FraudAnalysisResult(BaseModel):
    """Result of fraud analysis."""

    is_fraud: bool = Field(..., description="Whether fraud was detected")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")
    risk_score: float = Field(..., ge=0.0, le=100.0, description="Risk score (0-100)")
    reasoning: str = Field(..., description="Explanation of the decision")
    suspicious_patterns: List[str] = Field(
        default_factory=list, description="Detected suspicious patterns"
    )
    citations: List[str] = Field(
        default_factory=list, description="Citations/evidence (for RLM/RAG)"
    )
    flagged_transactions: List[int] = Field(
        default_factory=list, description="Indices of flagged transactions"
    )


class AnalysisMetrics(BaseModel):
    """Metrics tracked during analysis."""

    approach: ApproachType
    total_tokens: int = Field(..., description="Total tokens used (prompt + completion)")
    prompt_tokens: int = Field(..., description="Tokens in prompt")
    completion_tokens: int = Field(..., description="Tokens in completion")
    latency_ms: float = Field(..., description="Analysis latency in milliseconds")
    cost_usd: float = Field(..., description="Estimated cost in USD")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Additional context
    transactions_analyzed: int = Field(..., description="Number of transactions analyzed")
    context_size_chars: Optional[int] = Field(None, description="Size of context in characters")


class AnalysisRequest(BaseModel):
    """Request for fraud analysis."""

    transactions: List[Transaction] = Field(..., min_length=1)
    user_id: Optional[str] = Field(None, description="User/card identifier for context")
    approach: Optional[ApproachType] = Field(None, description="Specific approach to use")
    include_metrics: bool = Field(default=True, description="Include performance metrics")


class AnalysisResponse(BaseModel):
    """Response from fraud analysis."""

    result: FraudAnalysisResult
    metrics: Optional[AnalysisMetrics] = None
    approach: ApproachType
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ComparisonResponse(BaseModel):
    """Comparison of all three approaches."""

    naive: AnalysisResponse
    rag: AnalysisResponse
    rlm: AnalysisResponse
    summary: Dict[str, Any] = Field(
        default_factory=dict, description="Comparative summary statistics"
    )

    def calculate_summary(self) -> None:
        """Calculate summary statistics."""
        responses = [self.naive, self.rag, self.rlm]

        # Token comparison
        self.summary["token_usage"] = {
            "naive": self.naive.metrics.total_tokens if self.naive.metrics else 0,
            "rag": self.rag.metrics.total_tokens if self.rag.metrics else 0,
            "rlm": self.rlm.metrics.total_tokens if self.rlm.metrics else 0,
        }

        # Calculate savings
        naive_tokens = self.naive.metrics.total_tokens if self.naive.metrics else 1
        rlm_tokens = self.rlm.metrics.total_tokens if self.rlm.metrics else 0
        self.summary["token_savings_pct"] = (
            ((naive_tokens - rlm_tokens) / naive_tokens * 100) if naive_tokens > 0 else 0
        )

        # Latency comparison
        self.summary["latency_ms"] = {
            "naive": self.naive.metrics.latency_ms if self.naive.metrics else 0,
            "rag": self.rag.metrics.latency_ms if self.rag.metrics else 0,
            "rlm": self.rlm.metrics.latency_ms if self.rlm.metrics else 0,
        }

        # Cost comparison
        self.summary["cost_usd"] = {
            "naive": self.naive.metrics.cost_usd if self.naive.metrics else 0,
            "rag": self.rag.metrics.cost_usd if self.rag.metrics else 0,
            "rlm": self.rlm.metrics.cost_usd if self.rlm.metrics else 0,
        }

        # Agreement analysis
        fraud_detections = [r.result.is_fraud for r in responses]
        self.summary["consensus"] = all(fraud_detections) or not any(fraud_detections)
        self.summary["agreement_count"] = sum(fraud_detections)
