"""Fraud analysis API endpoints."""

from typing import List

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.models.schemas import AnalysisRequest, AnalysisResponse, ApproachType, ComparisonResponse
from app.services.fraud_service import fraud_service

router = APIRouter()


@router.post("/analyze/naive", response_model=AnalysisResponse)
async def analyze_naive(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze transactions using Naive LLM approach.

    Limitations:
    - Max ~50 transactions
    - Expensive (all data through main model)
    - No programmatic filtering
    """
    try:
        logger.info(f"Naive analysis request: {len(request.transactions)} transactions")

        result, metrics = await fraud_service.analyze_naive(request.transactions)

        return AnalysisResponse(
            result=result, metrics=metrics if request.include_metrics else None, approach=ApproachType.NAIVE
        )

    except Exception as e:
        logger.error(f"Naive analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/rag", response_model=AnalysisResponse)
async def analyze_rag(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze transactions using RAG approach.

    Features:
    - Retrieval of similar fraud patterns
    - More efficient than naive
    - Max ~100 transactions
    """
    try:
        logger.info(f"RAG analysis request: {len(request.transactions)} transactions")

        result, metrics = await fraud_service.analyze_rag(request.transactions)

        return AnalysisResponse(
            result=result, metrics=metrics if request.include_metrics else None, approach=ApproachType.RAG
        )

    except Exception as e:
        logger.error(f"RAG analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/rlm", response_model=AnalysisResponse)
async def analyze_rlm(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze transactions using RLM approach.

    Advantages:
    - Handles 10,000+ transactions
    - 70-90% token savings
    - Programmatic filtering via code generation
    - Grounded responses with citations
    """
    try:
        logger.info(f"RLM analysis request: {len(request.transactions)} transactions")

        result, metrics = await fraud_service.analyze_rlm(request.transactions)

        return AnalysisResponse(
            result=result, metrics=metrics if request.include_metrics else None, approach=ApproachType.RLM
        )

    except Exception as e:
        logger.error(f"RLM analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analyze/compare", response_model=ComparisonResponse)
async def compare_all_approaches(request: AnalysisRequest) -> ComparisonResponse:
    """
    Run all three approaches in parallel and compare results.

    Returns comprehensive comparison showing:
    - Token usage for each approach
    - Token savings with RLM
    - Latency comparison
    - Cost comparison
    - Consensus analysis
    """
    try:
        logger.info(f"Comparison analysis request: {len(request.transactions)} transactions")

        comparison = await fraud_service.compare_all(request.transactions)

        return comparison

    except Exception as e:
        logger.error(f"Comparison analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")
