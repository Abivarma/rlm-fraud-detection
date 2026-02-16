"""RAG (Retrieval Augmented Generation) agent for fraud detection."""

import time
from typing import Any, Dict, List

import numpy as np
from loguru import logger
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from app.core.config import settings
from app.models.schemas import ApproachType, FraudAnalysisResult, Transaction

from .base_agent import BaseFraudAgent


class RAGFraudAgent(BaseFraudAgent):
    """
    RAG (Retrieval Augmented Generation) approach for fraud detection.

    How it works:
    1. Embed all historical transactions
    2. Given new transactions, find similar past cases via vector search
    3. Retrieve relevant fraud patterns
    4. Send only relevant context + current transactions to LLM

    Advantages over naive:
    - More efficient than naive (retrieves only relevant context)
    - Can reference historical patterns

    Limitations vs RLM:
    - Still limited by context window
    - No programmatic filtering
    - Embedding + retrieval adds latency
    - Requires pre-built knowledge base
    """

    def __init__(self):
        """Initialize RAG agent."""
        import os
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key

        super().__init__(ApproachType.RAG)
        self.model = OpenAIModel(settings.main_model.replace("openai:", ""))
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Create agent with retrieval tool
        self.agent = Agent(
            model=self.model,
            output_type=FraudAnalysisResult,
            system_prompt=self._get_system_prompt(),
        )

        # In-memory fraud pattern knowledge base (simplified)
        # In production, this would use pgvector for real vector search
        self.fraud_patterns = self._initialize_fraud_patterns()

    def _get_system_prompt(self) -> str:
        """Get system prompt for RAG-based fraud detection."""
        return """You are an expert fraud detection analyst with access to historical fraud patterns.

You will be provided with:
1. Current transactions to analyze
2. Similar historical fraud patterns (retrieved via semantic search)

Your task is to:
- Analyze current transactions in context of known fraud patterns
- Identify similarities to historical fraud cases
- Assess fraud risk based on pattern matching

Respond with:
- is_fraud: Boolean indicating fraud detection
- confidence: Confidence score (0-1)
- risk_score: Risk score (0-100)
- reasoning: Explanation referencing similar patterns
- suspicious_patterns: Detected patterns
- citations: References to similar historical cases
- flagged_transactions: Indices of suspicious transactions

Leverage the retrieved context to make informed decisions."""

    def _initialize_fraud_patterns(self) -> List[Dict[str, Any]]:
        """
        Initialize fraud pattern knowledge base.

        In production, this would be loaded from database with embeddings.

        Returns:
            List[Dict]: Fraud patterns
        """
        return [
            {
                "pattern_id": "rapid_small_transactions",
                "name": "Rapid Small Transactions",
                "description": "Multiple small transactions in quick succession, often testing card limits",
                "indicators": ["low_amount", "high_frequency", "short_time_span"],
                "severity": "medium",
            },
            {
                "pattern_id": "large_unusual_purchase",
                "name": "Large Unusual Purchase",
                "description": "Single large transaction significantly higher than normal",
                "indicators": ["high_amount", "statistical_outlier"],
                "severity": "high",
            },
            {
                "pattern_id": "foreign_transaction_pattern",
                "name": "Foreign Transaction Pattern",
                "description": "Unusual geographic patterns detected via feature analysis",
                "indicators": ["anomalous_v_features", "location_pattern"],
                "severity": "medium",
            },
            {
                "pattern_id": "time_based_anomaly",
                "name": "Time-Based Anomaly",
                "description": "Transactions at unusual times or intervals",
                "indicators": ["unusual_timing", "rapid_succession"],
                "severity": "low",
            },
            {
                "pattern_id": "feature_outlier_cluster",
                "name": "Feature Outlier Cluster",
                "description": "Multiple PCA features showing extreme values simultaneously",
                "indicators": ["multi_feature_outlier", "anomalous_v_features"],
                "severity": "high",
            },
        ]

    async def analyze(self, transactions: List[Transaction]) -> FraudAnalysisResult:
        """
        Analyze transactions using RAG approach.

        Steps:
        1. Create embedding of transaction summary
        2. Retrieve relevant fraud patterns via similarity search
        3. Provide transactions + retrieved patterns to LLM
        4. Get fraud assessment

        Args:
            transactions: List of transactions to analyze

        Returns:
            FraudAnalysisResult: Analysis result
        """
        start_time = time.time()

        # Limit transactions
        max_txns = min(len(transactions), settings.max_transactions_rag)
        transactions = transactions[:max_txns]

        logger.info(f"RAG agent analyzing {len(transactions)} transactions")

        # Step 1: Create transaction summary for retrieval
        txn_summary = self._create_transaction_summary(transactions)

        # Step 2: Retrieve relevant fraud patterns (simplified semantic search)
        retrieved_patterns = await self._retrieve_relevant_patterns(txn_summary)

        # Step 3: Build context with transactions + retrieved patterns
        context = self._build_rag_context(transactions, retrieved_patterns)
        context_size = len(context)

        # Step 4: Run LLM analysis
        user_prompt = f"""{context}

Analyze the {len(transactions)} current transactions above for fraud, considering the similar historical patterns provided.

Provide a comprehensive assessment."""

        try:
            result = await self.agent.run(user_prompt)

            latency_ms = (time.time() - start_time) * 1000

            # Extract usage
            try:
                usage = result.usage()
                prompt_tokens = usage.request_tokens if usage else 0
                completion_tokens = usage.response_tokens if usage else 0
            except Exception as e:
                logger.warning(f"Could not extract token usage: {e}. Using defaults.")
                prompt_tokens = 3000
                completion_tokens = 500

            logger.info(
                f"RAG analysis complete: Fraud={result.output.is_fraud}, "
                f"Tokens={prompt_tokens + completion_tokens}, "
                f"Patterns retrieved={len(retrieved_patterns)}, "
                f"Latency={latency_ms:.0f}ms"
            )

            return result.output

        except Exception as e:
            logger.error(f"RAG agent error: {e}")
            return FraudAnalysisResult(
                is_fraud=False,
                confidence=0.0,
                risk_score=0.0,
                reasoning=f"RAG analysis failed: {str(e)}",
                suspicious_patterns=[],
                citations=[],
                flagged_transactions=[],
            )

    def _create_transaction_summary(self, transactions: List[Transaction]) -> str:
        """
        Create a text summary of transactions for embedding.

        Args:
            transactions: Transactions to summarize

        Returns:
            str: Summary text
        """
        amounts = [txn.amount for txn in transactions]
        times = [txn.time for txn in transactions]

        summary = f"""Transaction batch summary:
- Count: {len(transactions)}
- Amount range: ${min(amounts):.2f} - ${max(amounts):.2f}
- Average amount: ${np.mean(amounts):.2f}
- Time span: {min(times):.0f}s - {max(times):.0f}s
- Time range: {max(times) - min(times):.0f}s
"""
        return summary

    async def _retrieve_relevant_patterns(
        self, query: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant fraud patterns via semantic search.

        Simplified version: Just returns top patterns.
        In production, would use pgvector for real similarity search.

        Args:
            query: Query text
            top_k: Number of patterns to retrieve

        Returns:
            List[Dict]: Retrieved patterns
        """
        # Simplified: Return top patterns
        # In production, would:
        # 1. Embed query
        # 2. Perform vector similarity search in pgvector
        # 3. Return top-k most similar patterns

        return self.fraud_patterns[:top_k]

    def _build_rag_context(
        self, transactions: List[Transaction], patterns: List[Dict[str, Any]]
    ) -> str:
        """
        Build context combining transactions and retrieved patterns.

        Args:
            transactions: Current transactions
            patterns: Retrieved fraud patterns

        Returns:
            str: Combined context
        """
        lines = ["=== CURRENT TRANSACTIONS ==="]
        for idx, txn in enumerate(transactions):
            lines.append(
                f"Transaction {idx}: Time={txn.time:.0f}s, Amount=${txn.amount:.2f}, "
                f"V1={txn.v1:.2f}, V2={txn.v2:.2f}, V3={txn.v3:.2f}"
            )

        lines.append("\n=== SIMILAR FRAUD PATTERNS (Retrieved from Knowledge Base) ===")
        for pattern in patterns:
            lines.append(
                f"\nPattern: {pattern['name']}\n"
                f"Description: {pattern['description']}\n"
                f"Indicators: {', '.join(pattern['indicators'])}\n"
                f"Severity: {pattern['severity']}"
            )

        return "\n".join(lines)
