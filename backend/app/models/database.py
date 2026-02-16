"""SQLAlchemy database models."""

from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class TransactionDB(Base):
    """Transaction database model."""

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)

    # Transaction data
    time: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)

    # PCA features (V1-V28)
    features: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Label
    class_label: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_fraud: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Embedding for RAG (1536 dimensions for text-embedding-3-small)
    embedding: Mapped[Optional[list]] = mapped_column(Vector(1536), nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Transaction {self.transaction_id} - ${self.amount:.2f}>"


class AnalysisResultDB(Base):
    """Analysis result database model."""

    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Approach used
    approach: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Results
    is_fraud: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    suspicious_patterns: Mapped[list] = mapped_column(JSONB, default=list)
    citations: Mapped[list] = mapped_column(JSONB, default=list)
    flagged_transactions: Mapped[list] = mapped_column(JSONB, default=list)

    # Metrics
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Float, nullable=False)
    transactions_analyzed: Mapped[int] = mapped_column(Integer, nullable=False)
    context_size_chars: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Metadata
    user_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return (
            f"<AnalysisResult {self.analysis_id} - {self.approach} - "
            f"Fraud: {self.is_fraud}>"
        )


class FraudPatternDB(Base):
    """Known fraud pattern database model (for RAG)."""

    __tablename__ = "fraud_patterns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pattern_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # Pattern description
    pattern_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Pattern characteristics
    characteristics: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Example transactions
    example_transactions: Mapped[list] = mapped_column(JSONB, default=list)

    # Embedding for similarity search
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=False)

    # Metadata
    severity: Mapped[str] = mapped_column(String(50), default="medium")
    frequency: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<FraudPattern {self.pattern_name} - Severity: {self.severity}>"
