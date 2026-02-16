"""Streamlit dashboard for fraud detection comparison."""

import asyncio
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.models.schemas import ApproachType, Transaction
from app.services.data_loader import data_loader
from app.services.fraud_service import fraud_service

# Page config
st.set_page_config(
    page_title="Fraud Detection RLM Comparison",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .fraud-detected {
        color: #d62728;
        font-weight: bold;
    }
    .no-fraud {
        color: #2ca02c;
        font-weight: bold;
    }
</style>
""",
    unsafe_allow_html=True,
)


def main():
    """Main dashboard function."""
    st.markdown('<p class="main-header">🔍 Fraud Detection: RLM vs RAG vs Naive LLM</p>', unsafe_allow_html=True)

    st.markdown(
        """
    This dashboard demonstrates **three approaches** to fraud detection:
    - **Naive LLM**: Sends all data to the main model (expensive, limited context)
    - **RAG**: Retrieves relevant patterns before analysis (more efficient)
    - **RLM**: Writes code to filter data programmatically (most efficient, 70-90% token savings!)
    """
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Dataset info
        try:
            dataset_info = data_loader.get_dataset_info()
            st.success("✓ Dataset loaded")
            st.metric("Total Transactions", f"{dataset_info['total_transactions']:,}")
            st.metric("Fraud Cases", f"{dataset_info['fraud_transactions']:,}")
            st.metric("Fraud Rate", f"{dataset_info['fraud_percentage']:.2f}%")
        except FileNotFoundError:
            st.error("❌ Dataset not found!")
            st.markdown(
                """
            **Please download the dataset:**
            ```bash
            python scripts/download_dataset.py
            ```
            """
            )
            return

        st.divider()

        # Transaction selection
        st.subheader("Transaction Selection")

        sample_type = st.radio(
            "Sample Type:",
            ["Random Mix", "Known Fraud", "Legitimate Only", "Consecutive Batch"],
        )

        n_transactions = st.slider(
            "Number of Transactions:",
            min_value=5,
            max_value=100,
            value=20,
            step=5,
        )

        if sample_type == "Random Mix":
            fraud_ratio = st.slider(
                "Fraud Ratio:", min_value=0.0, max_value=1.0, value=0.2, step=0.1
            )
        else:
            fraud_ratio = 0.0

        analyze_button = st.button("🚀 Run Analysis", type="primary", use_container_width=True)

    # Main content
    if not analyze_button:
        st.info("👈 Configure settings in the sidebar and click **Run Analysis** to start!")
        show_example_metrics()
        return

    # Load transactions
    with st.spinner("Loading transactions..."):
        if sample_type == "Random Mix":
            transactions = data_loader.get_sample_transactions(
                n=n_transactions, include_fraud=True, fraud_ratio=fraud_ratio
            )
        elif sample_type == "Known Fraud":
            transactions = data_loader.get_fraud_cases(n=n_transactions)
        elif sample_type == "Legitimate Only":
            transactions = data_loader.get_legitimate_cases(n=n_transactions)
        else:  # Consecutive Batch
            transactions = data_loader.get_transaction_batch(batch_size=n_transactions)

    # Display transaction summary
    st.subheader("📊 Transaction Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Transactions", len(transactions))
    with col2:
        amounts = [t.amount for t in transactions]
        st.metric("Avg Amount", f"${sum(amounts)/len(amounts):.2f}")
    with col3:
        fraud_count = sum(1 for t in transactions if t.class_label == 1)
        st.metric("Fraud Cases (Actual)", fraud_count)
    with col4:
        st.metric("Legitimate Cases", len(transactions) - fraud_count)

    # Run comparison analysis
    st.subheader("🔬 Running All Three Approaches...")

    progress_bar = st.progress(0)
    status_text = st.empty()

    with st.spinner("Analyzing with Naive LLM, RAG, and RLM..."):
        # Run async analysis
        comparison = asyncio.run(fraud_service.compare_all(transactions))
        progress_bar.progress(100)
        status_text.success("✓ Analysis complete!")

    # Display results
    st.divider()
    st.header("📈 Comparison Results")

    # Create three columns for results
    col1, col2, col3 = st.columns(3)

    with col1:
        display_approach_results("Naive LLM", comparison.naive, "#ff6b6b")

    with col2:
        display_approach_results("RAG", comparison.rag, "#4ecdc4")

    with col3:
        display_approach_results("RLM", comparison.rlm, "#95e1d3")

    # Metrics comparison
    st.divider()
    st.header("📊 Performance Metrics Comparison")

    metrics_col1, metrics_col2 = st.columns(2)

    with metrics_col1:
        # Token usage comparison
        fig_tokens = create_token_comparison_chart(comparison)
        st.plotly_chart(fig_tokens, use_container_width=True)

    with metrics_col2:
        # Cost and latency comparison
        fig_perf = create_performance_comparison_chart(comparison)
        st.plotly_chart(fig_perf, use_container_width=True)

    # Key metrics
    st.subheader("🎯 Key Metrics")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        token_savings = comparison.summary.get("token_savings_pct", 0)
        st.metric(
            "Token Savings (RLM vs Naive)",
            f"{token_savings:.1f}%",
            delta=f"{token_savings:.1f}%" if token_savings > 0 else None,
        )

    with metric_col2:
        naive_cost = comparison.naive.metrics.cost_usd if comparison.naive.metrics else 0
        rlm_cost = comparison.rlm.metrics.cost_usd if comparison.rlm.metrics else 0
        cost_savings = ((naive_cost - rlm_cost) / naive_cost * 100) if naive_cost > 0 else 0
        st.metric("Cost Savings (RLM)", f"{cost_savings:.1f}%", delta=f"${naive_cost - rlm_cost:.4f}")

    with metric_col3:
        consensus = comparison.summary.get("consensus", False)
        agreement = comparison.summary.get("agreement_count", 0)
        st.metric("Agreement", f"{agreement}/3 approaches", delta="Consensus" if consensus else "Split")

    with metric_col4:
        naive_latency = comparison.naive.metrics.latency_ms if comparison.naive.metrics else 0
        rlm_latency = comparison.rlm.metrics.latency_ms if comparison.rlm.metrics else 0
        latency_diff = naive_latency - rlm_latency
        st.metric("Latency Difference", f"{abs(latency_diff):.0f}ms", delta=f"{latency_diff:.0f}ms")


def display_approach_results(name, response, color):
    """Display results for a single approach."""
    st.markdown(f"### {name}")

    result = response.result
    metrics = response.metrics

    # Fraud detection result
    if result.is_fraud:
        st.markdown(f'<p class="fraud-detected">🚨 FRAUD DETECTED</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="no-fraud">✓ No Fraud Detected</p>', unsafe_allow_html=True)

    # Metrics
    st.metric("Confidence", f"{result.confidence:.1%}")
    st.metric("Risk Score", f"{result.risk_score:.1f}/100")

    if metrics:
        st.metric("Tokens Used", f"{metrics.total_tokens:,}")
        st.metric("Cost", f"${metrics.cost_usd:.4f}")
        st.metric("Latency", f"{metrics.latency_ms:.0f}ms")

    # Reasoning
    with st.expander("💭 Reasoning"):
        st.write(result.reasoning)

    # Patterns
    if result.suspicious_patterns:
        with st.expander("🔍 Suspicious Patterns"):
            for pattern in result.suspicious_patterns:
                st.write(f"- {pattern}")

    # Citations (RLM)
    if result.citations:
        with st.expander("📝 Citations"):
            for citation in result.citations:
                st.write(f"- {citation}")


def create_token_comparison_chart(comparison):
    """Create token usage comparison chart."""
    approaches = ["Naive", "RAG", "RLM"]
    token_counts = [
        comparison.naive.metrics.total_tokens if comparison.naive.metrics else 0,
        comparison.rag.metrics.total_tokens if comparison.rag.metrics else 0,
        comparison.rlm.metrics.total_tokens if comparison.rlm.metrics else 0,
    ]

    fig = go.Figure(
        data=[
            go.Bar(
                x=approaches,
                y=token_counts,
                marker_color=["#ff6b6b", "#4ecdc4", "#95e1d3"],
                text=token_counts,
                textposition="auto",
            )
        ]
    )

    fig.update_layout(
        title="Token Usage Comparison",
        xaxis_title="Approach",
        yaxis_title="Total Tokens",
        height=400,
    )

    return fig


def create_performance_comparison_chart(comparison):
    """Create performance comparison chart."""
    approaches = ["Naive", "RAG", "RLM"]

    costs = [
        comparison.naive.metrics.cost_usd if comparison.naive.metrics else 0,
        comparison.rag.metrics.cost_usd if comparison.rag.metrics else 0,
        comparison.rlm.metrics.cost_usd if comparison.rlm.metrics else 0,
    ]

    latencies = [
        comparison.naive.metrics.latency_ms if comparison.naive.metrics else 0,
        comparison.rag.metrics.latency_ms if comparison.rag.metrics else 0,
        comparison.rlm.metrics.latency_ms if comparison.rlm.metrics else 0,
    ]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Cost (USD)", "Latency (ms)"),
    )

    fig.add_trace(
        go.Bar(x=approaches, y=costs, marker_color=["#ff6b6b", "#4ecdc4", "#95e1d3"], name="Cost"),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Bar(x=approaches, y=latencies, marker_color=["#ff6b6b", "#4ecdc4", "#95e1d3"], name="Latency"),
        row=1,
        col=2,
    )

    fig.update_layout(height=400, showlegend=False)

    return fig


def show_example_metrics():
    """Show example metrics from documentation."""
    st.subheader("📚 Expected Performance")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### Naive LLM")
        st.metric("Token Usage", "~5,000")
        st.metric("Cost", "$0.05")
        st.metric("Max Context", "50-100 txns")

    with col2:
        st.markdown("### RAG")
        st.metric("Token Usage", "~3,500")
        st.metric("Cost", "$0.035")
        st.metric("Max Context", "100-200 txns")

    with col3:
        st.markdown("### RLM 🏆")
        st.metric("Token Usage", "~800")
        st.metric("Cost", "$0.008")
        st.metric("Max Context", "10,000+ txns")


if __name__ == "__main__":
    main()
