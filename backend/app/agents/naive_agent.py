"""Naive LLM agent for fraud detection."""

import time
from typing import List

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.core.config import settings
from app.models.schemas import ApproachType, FraudAnalysisResult, Transaction

from .base_agent import BaseFraudAgent


class NaiveFraudAgent(BaseFraudAgent):
    """
    Naive LLM approach: Send all transactions directly in the prompt.

    Limitations:
    - Limited by context window
    - Expensive (processes all data through main model)
    - No programmatic filtering
    - Can only handle ~50-100 transactions
    """

    def __init__(self):
        """Initialize naive agent."""
        import os
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key

        super().__init__(ApproachType.NAIVE)
        self.model = OpenAIModel(settings.main_model.replace("openai:", ""))
        self.agent = Agent(
            model=self.model,
            output_type=FraudAnalysisResult,
            system_prompt=self._get_system_prompt(),
        )

    def _get_system_prompt(self) -> str:
        """Get system prompt for fraud detection."""
        return """You are an expert fraud detection analyst specializing in credit card transactions.

Your task is to analyze transactions and identify potential fraud based on patterns and anomalies.

Transaction features:
- Time: Seconds elapsed since first transaction
- Amount: Transaction amount in USD
- V1-V28: PCA-transformed features (anonymized behavioral/transactional characteristics)

Common fraud indicators:
- Unusual transaction amounts (very high or very low)
- Rapid succession of transactions
- Anomalous feature patterns compared to typical behavior
- Statistical outliers in V1-V28 features

You must respond with:
- is_fraud: Boolean indicating fraud detection
- confidence: Confidence score (0-1)
- risk_score: Risk score (0-100)
- reasoning: Clear explanation of your decision
- suspicious_patterns: List of detected patterns
- flagged_transactions: Indices of suspicious transactions (0-indexed)

Be thorough but concise in your analysis."""

    async def analyze(self, transactions: List[Transaction]) -> FraudAnalysisResult:
        """
        Analyze transactions using naive LLM approach.

        Args:
            transactions: List of transactions to analyze

        Returns:
            FraudAnalysisResult: Analysis result with metrics
        """
        start_time = time.time()

        # Limit transactions to avoid context overflow
        max_txns = min(len(transactions), settings.max_transactions_naive)
        transactions = transactions[:max_txns]

        logger.info(f"Naive agent analyzing {len(transactions)} transactions")

        # Format transactions for prompt
        context = self._format_detailed_transactions(transactions)
        context_size = len(context)

        # Create user prompt
        user_prompt = f"""Analyze the following {len(transactions)} credit card transactions for potential fraud.

{context}

Provide a comprehensive fraud analysis with your assessment, confidence level, risk score, reasoning, suspicious patterns, and indices of flagged transactions."""

        try:
            # Run agent
            result = await self.agent.run(user_prompt)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Extract token usage (if available)
            try:
                usage = result.usage()
                prompt_tokens = usage.request_tokens if usage else 0
                completion_tokens = usage.response_tokens if usage else 0
            except Exception as e:
                logger.warning(f"Could not extract token usage: {e}. Using defaults.")
                prompt_tokens = 4500
                completion_tokens = 500

            logger.info(
                f"Naive analysis complete: Fraud={result.output.is_fraud}, "
                f"Tokens={prompt_tokens + completion_tokens}, "
                f"Latency={latency_ms:.0f}ms"
            )

            return result.output

        except Exception as e:
            logger.error(f"Naive agent error: {e}")
            # Return safe default
            return FraudAnalysisResult(
                is_fraud=False,
                confidence=0.0,
                risk_score=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                suspicious_patterns=[],
                citations=[],
                flagged_transactions=[],
            )

    def _format_detailed_transactions(self, transactions: List[Transaction]) -> str:
        """
        Format transactions with full detail for LLM context.

        Args:
            transactions: List of transactions

        Returns:
            str: Formatted detailed transaction context
        """
        lines = []
        for idx, txn in enumerate(transactions):
            features = ", ".join([f"V{i}={getattr(txn, f'v{i}'):.3f}" for i in range(1, 29)])
            lines.append(
                f"Transaction {idx}:\n"
                f"  Time: {txn.time:.0f}s\n"
                f"  Amount: ${txn.amount:.2f}\n"
                f"  Features: {features}\n"
            )
        return "\n".join(lines)
