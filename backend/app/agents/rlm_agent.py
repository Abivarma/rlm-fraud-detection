"""RLM (Recursive Language Model) agent - Simplified implementation."""

import json
import statistics
import time
from typing import Any, Dict, List

from loguru import logger
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from app.core.config import settings
from app.models.schemas import ApproachType, FraudAnalysisResult, Transaction

from .base_agent import BaseFraudAgent


class RLMFraudAgent(BaseFraudAgent):
    """
    RLM (Recursive Language Model) approach - Simplified.

    This implements the RLM pattern manually:
    1. Programmatically filter suspicious transactions
    2. Use LLM only for semantic analysis of filtered subset
    3. Dramatically reduce token usage
    """

    def __init__(self):
        """Initialize RLM agent."""
        import os
        os.environ["OPENAI_API_KEY"] = settings.openai_api_key

        super().__init__(ApproachType.RLM)
        self.model = OpenAIModel(settings.sub_model.replace("openai:", ""))  # Use cheaper model!
        self.agent = Agent(
            model=self.model,
            output_type=FraudAnalysisResult,
            system_prompt=self._get_system_prompt(),
        )

    def _get_system_prompt(self) -> str:
        """Get system prompt for RLM analysis."""
        return """You are an expert fraud analyst performing final semantic analysis on PRE-FILTERED suspicious transactions.

The transactions you're analyzing have ALREADY been filtered programmatically as suspicious.
Your job is to provide the final fraud assessment.

Provide:
- is_fraud: Boolean fraud detection
- confidence: Confidence score (0-1)
- risk_score: Risk score (0-100)
- reasoning: Clear explanation
- suspicious_patterns: List of patterns found
- citations: Reference the specific evidence
- flagged_transactions: Indices of most suspicious

Be thorough but concise."""

    async def analyze(self, transactions: List[Transaction]) -> FraudAnalysisResult:
        """
        Analyze transactions using RLM approach.

        RLM Process:
        1. Programmatically filter suspicious transactions (code-based, fast)
        2. Analyze only the suspicious subset with LLM (semantic)
        3. Return result with citations

        This is much more token-efficient than sending all transactions to LLM!
        """
        start_time = time.time()

        logger.info(f"RLM agent analyzing {len(transactions)} transactions")

        # Step 1: Programmatic filtering (RLM's key innovation!)
        suspicious_txns = self._filter_suspicious_transactions(transactions)

        logger.info(
            f"RLM filtered {len(transactions)} → {len(suspicious_txns)} suspicious transactions"
        )

        # Step 2: Semantic analysis on filtered subset only
        if not suspicious_txns:
            # No suspicious transactions found
            return FraudAnalysisResult(
                is_fraud=False,
                confidence=0.95,
                risk_score=5.0,
                reasoning="Programmatic analysis found no anomalies. All transactions within normal parameters.",
                suspicious_patterns=[],
                citations=["Analyzed all {} transactions programmatically".format(len(transactions))],
                flagged_transactions=[],
            )

        # Format only suspicious transactions for LLM
        context = self._format_suspicious_for_llm(suspicious_txns, len(transactions))

        prompt = f"""Analyze these {len(suspicious_txns)} suspicious transactions (filtered from {len(transactions)} total).

{context}

Provide comprehensive fraud assessment with specific citations to the transactions above."""

        try:
            result = await self.agent.run(prompt)

            latency_ms = (time.time() - start_time) * 1000

            # Get token usage
            try:
                usage = result.usage()
                tokens_used = (usage.request_tokens + usage.response_tokens) if usage else 800
            except Exception as e:
                logger.warning(f"Could not extract token usage: {e}. Using default.")
                tokens_used = 800

            logger.info(
                f"RLM analysis complete: Fraud={result.output.is_fraud}, "
                f"Filtered {len(transactions)}→{len(suspicious_txns)}, "
                f"Tokens={tokens_used}, Latency={latency_ms:.0f}ms"
            )

            # Add citation about filtering
            result.output.citations.insert(
                0,
                f"Programmatically filtered {len(transactions)} transactions → {len(suspicious_txns)} suspicious"
            )

            return result.output

        except Exception as e:
            logger.error(f"RLM agent error: {e}")
            return FraudAnalysisResult(
                is_fraud=False,
                confidence=0.0,
                risk_score=0.0,
                reasoning=f"RLM analysis failed: {str(e)}",
                suspicious_patterns=[],
                citations=[],
                flagged_transactions=[],
            )

    def _filter_suspicious_transactions(
        self, transactions: List[Transaction]
    ) -> List[Dict[str, Any]]:
        """
        Programmatically filter suspicious transactions.

        This is the RLM magic: Code-based filtering is 1000x faster and cheaper than LLM!

        Returns:
            List of suspicious transaction dictionaries with metadata
        """
        suspicious = []

        # Calculate statistics for anomaly detection
        amounts = [t.amount for t in transactions]
        if not amounts:
            return suspicious

        mean_amount = statistics.mean(amounts)
        try:
            std_amount = statistics.stdev(amounts) if len(amounts) > 1 else mean_amount * 0.3
        except:
            std_amount = mean_amount * 0.3

        # Anomaly thresholds
        high_amount_threshold = mean_amount + (3 * std_amount)
        low_amount_threshold = max(0, mean_amount - (2 * std_amount))

        for idx, txn in enumerate(transactions):
            reasons = []

            # Check 1: Unusual amount (statistical outlier)
            if txn.amount > high_amount_threshold:
                reasons.append(f"Amount ${txn.amount:.2f} is {(txn.amount - mean_amount) / std_amount:.1f}σ above mean")
            elif txn.amount < 1.0 and txn.amount < low_amount_threshold:
                reasons.append(f"Unusually low amount ${txn.amount:.2f}")

            # Check 2: Extreme V-feature values (PCA anomalies)
            extreme_features = []
            for i in range(1, 29):
                v_val = getattr(txn, f"v{i}")
                if abs(v_val) > 3:  # Beyond 3 standard deviations
                    extreme_features.append(f"V{i}={v_val:.2f}")

            if len(extreme_features) >= 3:
                reasons.append(f"Multiple extreme features: {', '.join(extreme_features[:3])}")

            # Check 3: Rapid succession (if we have time data)
            if idx > 0:
                time_diff = txn.time - transactions[idx-1].time
                if time_diff < 60:  # Less than 1 minute
                    reasons.append(f"Rapid succession: {time_diff:.0f}s after previous")

            # Add to suspicious list if any reasons found
            if reasons:
                suspicious.append({
                    "index": idx,
                    "transaction": txn,
                    "reasons": reasons,
                    "risk_score": min(100, len(reasons) * 30 + (50 if txn.amount > high_amount_threshold else 0)),
                })

        # Sort by risk score (highest first) and limit to top suspicious
        suspicious.sort(key=lambda x: x["risk_score"], reverse=True)
        return suspicious[:20]  # Limit to top 20 for token efficiency

    def _format_suspicious_for_llm(
        self, suspicious_txns: List[Dict], total_count: int
    ) -> str:
        """
        Format suspicious transactions for LLM analysis.

        Much smaller context than sending all transactions!
        """
        lines = [
            f"=== SUSPICIOUS TRANSACTIONS (Filtered from {total_count} total) ===\n"
        ]

        for item in suspicious_txns:
            idx = item["index"]
            txn = item["transaction"]
            reasons = item["reasons"]
            risk = item["risk_score"]

            lines.append(
                f"\nTransaction #{idx}:\n"
                f"  Time: {txn.time:.0f}s, Amount: ${txn.amount:.2f}\n"
                f"  Risk Score: {risk}/100\n"
                f"  Flags: {'; '.join(reasons)}\n"
                f"  Key Features: V1={txn.v1:.2f}, V2={txn.v2:.2f}, V3={txn.v3:.2f}"
            )

        return "\n".join(lines)
