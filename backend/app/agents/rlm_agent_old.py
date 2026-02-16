"""RLM (Recursive Language Model) agent for fraud detection."""

import json
import time
from typing import Any, Dict, List

from loguru import logger
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from app.core.config import settings
from app.models.schemas import ApproachType, FraudAnalysisResult, Transaction

from .base_agent import BaseFraudAgent


class RLMFraudAgent(BaseFraudAgent):
    """
    RLM (Recursive Language Model) approach for fraud detection.

    Key advantages:
    - Handles massive context (10,000+ transactions)
    - LLM writes Python code to filter/analyze data programmatically
    - Delegates semantic analysis to cheaper sub-models
    - Token-efficient: 70-90% reduction vs naive
    - Grounded responses with citations
    """

    def __init__(self):
        """Initialize RLM agent."""
        super().__init__(ApproachType.RLM)
        self.main_model = OpenAIModel(settings.main_model.replace("openai:", ""))
        self.sub_model = OpenAIModel(settings.sub_model.replace("openai:", ""))

        # Create agent with system prompt explaining RLM approach
        self.agent = Agent(
            model=self.main_model,
            result_type=FraudAnalysisResult,
            system_prompt=self._get_system_prompt(),
        )

    async def analyze(self, transactions: List[Transaction]) -> FraudAnalysisResult:
        """
        Analyze transactions using RLM approach.

        The RLM approach:
        1. Main LLM writes Python code to explore transaction data
        2. Code executes to filter/aggregate data programmatically
        3. Sub-model performs semantic analysis on filtered subset
        4. Returns grounded result with citations

        Args:
            transactions: List of transactions to analyze (can be very large!)

        Returns:
            FraudAnalysisResult: Analysis result with citations
        """
        start_time = time.time()

        # RLM can handle much larger contexts
        max_txns = min(len(transactions), settings.max_transactions_rlm)
        transactions = transactions[:max_txns]

        logger.info(f"RLM agent analyzing {len(transactions)} transactions")

        # Prepare context: Convert transactions to analyzable format
        context = self._prepare_rlm_context(transactions)
        context_size = len(str(context))

        # Query for fraud detection
        query = f"""Analyze {len(transactions)} credit card transactions for fraud.

Instructions:
1. Write Python code to explore the transaction data programmatically
2. Filter for suspicious patterns:
   - Unusual amounts (statistical outliers)
   - Rapid transaction sequences
   - Anomalous feature patterns (V1-V28 PCA features)
   - High-risk combinations
3. For suspicious transactions, use llm_query() to perform semantic analysis
4. Provide comprehensive fraud assessment

The context variable contains a list of transaction dictionaries with keys:
- 'time': seconds since first transaction
- 'amount': transaction amount (USD)
- 'v1' through 'v28': PCA-transformed features
- 'index': transaction index

Return your analysis with:
- is_fraud: Whether fraud was detected
- confidence: Confidence score (0-1)
- risk_score: Risk score (0-100)
- reasoning: Detailed explanation
- suspicious_patterns: List of detected patterns
- citations: Evidence from the data
- flagged_transactions: Indices of suspicious transactions"""

        try:
            # Run RLM analysis
            result = await run_rlm_analysis(
                context=context,
                query=query,
                model=self.main_model,
                sub_model=self.sub_model,
                result_type=FraudAnalysisResult,
            )

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            logger.info(
                f"RLM analysis complete: Fraud={result.is_fraud}, "
                f"Latency={latency_ms:.0f}ms, "
                f"Citations={len(result.citations)}"
            )

            return result

        except Exception as e:
            logger.error(f"RLM agent error: {e}")
            # Return safe default
            return FraudAnalysisResult(
                is_fraud=False,
                confidence=0.0,
                risk_score=0.0,
                reasoning=f"RLM analysis failed: {str(e)}",
                suspicious_patterns=[],
                citations=[],
                flagged_transactions=[],
            )

    def _prepare_rlm_context(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        """
        Prepare transaction data for RLM analysis.

        Converts transactions to a list of dictionaries that can be
        programmatically explored by the LLM's generated code.

        Args:
            transactions: List of transactions

        Returns:
            List[Dict[str, Any]]: Transaction data in RLM-compatible format
        """
        context = []
        for idx, txn in enumerate(transactions):
            txn_dict = {
                "index": idx,
                "time": txn.time,
                "amount": txn.amount,
            }
            # Add V1-V28 features
            for i in range(1, 29):
                txn_dict[f"v{i}"] = getattr(txn, f"v{i}")

            context.append(txn_dict)

        return context

    async def analyze_with_agent(
        self, transactions: List[Transaction]
    ) -> FraudAnalysisResult:
        """
        Alternative: Use RLM agent directly instead of run_rlm_analysis.

        This gives more control over the agent configuration.

        Args:
            transactions: List of transactions

        Returns:
            FraudAnalysisResult: Analysis result
        """
        start_time = time.time()

        max_txns = min(len(transactions), settings.max_transactions_rlm)
        transactions = transactions[:max_txns]

        context = self._prepare_rlm_context(transactions)

        query = f"""Analyze these {len(transactions)} transactions for fraud patterns.
Use Python code to filter and analyze the data, then provide a comprehensive assessment."""

        try:
            # Create RLM dependencies
            deps = RLMDependencies(context=context)

            # Run agent
            result = await self.agent.run(query, deps=deps)

            latency_ms = (time.time() - start_time) * 1000

            logger.info(f"RLM agent analysis complete in {latency_ms:.0f}ms")

            return result.data

        except Exception as e:
            logger.error(f"RLM agent error: {e}")
            return FraudAnalysisResult(
                is_fraud=False,
                confidence=0.0,
                risk_score=0.0,
                reasoning=f"Analysis failed: {str(e)}",
                suspicious_patterns=[],
                citations=[],
                flagged_transactions=[],
            )
