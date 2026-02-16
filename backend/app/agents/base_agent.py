"""Base agent class for fraud detection."""

import time
from abc import ABC, abstractmethod
from typing import List

from app.core.config import settings
from app.models.schemas import AnalysisMetrics, ApproachType, FraudAnalysisResult, Transaction


class BaseFraudAgent(ABC):
    """Base class for fraud detection agents."""

    def __init__(self, approach: ApproachType):
        """Initialize the agent."""
        self.approach = approach
        self.settings = settings

    @abstractmethod
    async def analyze(self, transactions: List[Transaction]) -> FraudAnalysisResult:
        """
        Analyze transactions for fraud.

        Args:
            transactions: List of transactions to analyze

        Returns:
            FraudAnalysisResult: Analysis result
        """
        pass

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate cost in USD based on token usage.

        GPT-4o pricing (as of 2024):
        - Input: $2.50 per 1M tokens
        - Output: $10.00 per 1M tokens

        GPT-4o-mini pricing:
        - Input: $0.15 per 1M tokens
        - Output: $0.60 per 1M tokens

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            float: Estimated cost in USD
        """
        # Using GPT-4o pricing for main model
        input_cost_per_token = 2.50 / 1_000_000
        output_cost_per_token = 10.00 / 1_000_000

        cost = (prompt_tokens * input_cost_per_token) + (
            completion_tokens * output_cost_per_token
        )
        return round(cost, 6)

    def create_metrics(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: float,
        transactions_count: int,
        context_size: int | None = None,
    ) -> AnalysisMetrics:
        """
        Create metrics object.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            latency_ms: Latency in milliseconds
            transactions_count: Number of transactions analyzed
            context_size: Size of context in characters

        Returns:
            AnalysisMetrics: Metrics object
        """
        total_tokens = prompt_tokens + completion_tokens
        cost = self.calculate_cost(prompt_tokens, completion_tokens)

        return AnalysisMetrics(
            approach=self.approach,
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            cost_usd=cost,
            transactions_analyzed=transactions_count,
            context_size_chars=context_size,
        )

    def format_transactions_for_context(self, transactions: List[Transaction]) -> str:
        """
        Format transactions for LLM context.

        Args:
            transactions: List of transactions

        Returns:
            str: Formatted transaction context
        """
        lines = ["Recent transactions:"]
        for idx, txn in enumerate(transactions, 1):
            lines.append(
                f"{idx}. Time: {txn.time:.0f}s, Amount: ${txn.amount:.2f}, "
                f"Features: V1={txn.v1:.2f}, V2={txn.v2:.2f}, V3={txn.v3:.2f}... "
                f"(28 features total)"
            )
        return "\n".join(lines)
