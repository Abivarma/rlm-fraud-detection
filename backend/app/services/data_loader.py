"""Service for loading and managing Kaggle fraud dataset."""

import random
from pathlib import Path
from typing import List, Optional

import pandas as pd
from loguru import logger

from app.core.config import settings
from app.models.schemas import Transaction


class DataLoader:
    """Load and manage the Kaggle Credit Card Fraud dataset."""

    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize data loader.

        Args:
            dataset_path: Path to creditcard.csv file
        """
        self.dataset_path = dataset_path or settings.kaggle_dataset_path
        self.df: Optional[pd.DataFrame] = None
        self._loaded = False

    def load_dataset(self) -> pd.DataFrame:
        """
        Load the Kaggle credit card fraud dataset.

        Returns:
            pd.DataFrame: Loaded dataset

        Raises:
            FileNotFoundError: If dataset file not found
        """
        if self._loaded and self.df is not None:
            return self.df

        dataset_file = Path(self.dataset_path)

        if not dataset_file.exists():
            error_msg = f"""
Dataset not found at {self.dataset_path}

Please download the dataset:
1. Visit: {settings.dataset_url}
2. Download creditcard.csv
3. Place it in: {self.dataset_path}

Or run: python scripts/download_dataset.py
"""
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        logger.info(f"Loading dataset from {self.dataset_path}")
        self.df = pd.read_csv(dataset_file)
        self._loaded = True

        logger.info(
            f"Dataset loaded: {len(self.df)} transactions, "
            f"{self.df['Class'].sum()} fraudulent ({self.df['Class'].sum() / len(self.df) * 100:.2f}%)"
        )

        return self.df

    def get_sample_transactions(
        self, n: int = 10, include_fraud: bool = True, fraud_ratio: float = 0.2
    ) -> List[Transaction]:
        """
        Get a sample of transactions.

        Args:
            n: Number of transactions to return
            include_fraud: Whether to include fraudulent transactions
            fraud_ratio: Ratio of fraudulent to legitimate (if include_fraud=True)

        Returns:
            List[Transaction]: Sample transactions
        """
        if self.df is None:
            self.load_dataset()

        if not include_fraud:
            # Only legitimate transactions
            sample_df = self.df[self.df["Class"] == 0].sample(n=n)
        else:
            # Mix of fraud and legitimate
            n_fraud = int(n * fraud_ratio)
            n_legit = n - n_fraud

            fraud_df = self.df[self.df["Class"] == 1].sample(n=min(n_fraud, (self.df["Class"] == 1).sum()))
            legit_df = self.df[self.df["Class"] == 0].sample(n=n_legit)

            sample_df = pd.concat([fraud_df, legit_df]).sample(frac=1).reset_index(drop=True)

        return self._df_to_transactions(sample_df)

    def get_transaction_batch(
        self, start_idx: int = 0, batch_size: int = 100
    ) -> List[Transaction]:
        """
        Get a batch of consecutive transactions.

        Args:
            start_idx: Starting index
            batch_size: Number of transactions

        Returns:
            List[Transaction]: Batch of transactions
        """
        if self.df is None:
            self.load_dataset()

        batch_df = self.df.iloc[start_idx : start_idx + batch_size]
        return self._df_to_transactions(batch_df)

    def get_fraud_cases(self, n: int = 10) -> List[Transaction]:
        """
        Get known fraud cases (for testing).

        Args:
            n: Number of fraud cases

        Returns:
            List[Transaction]: Fraud transactions
        """
        if self.df is None:
            self.load_dataset()

        fraud_df = self.df[self.df["Class"] == 1].sample(n=min(n, (self.df["Class"] == 1).sum()))
        return self._df_to_transactions(fraud_df)

    def get_legitimate_cases(self, n: int = 10) -> List[Transaction]:
        """
        Get legitimate transactions (for testing).

        Args:
            n: Number of legitimate transactions

        Returns:
            List[Transaction]: Legitimate transactions
        """
        if self.df is None:
            self.load_dataset()

        legit_df = self.df[self.df["Class"] == 0].sample(n=n)
        return self._df_to_transactions(legit_df)

    def _df_to_transactions(self, df: pd.DataFrame) -> List[Transaction]:
        """
        Convert DataFrame to list of Transaction objects.

        Args:
            df: DataFrame with transaction data

        Returns:
            List[Transaction]: Converted transactions
        """
        transactions = []

        for idx, row in df.iterrows():
            transaction = Transaction(
                time=row["Time"],
                amount=row["Amount"],
                v1=row["V1"],
                v2=row["V2"],
                v3=row["V3"],
                v4=row["V4"],
                v5=row["V5"],
                v6=row["V6"],
                v7=row["V7"],
                v8=row["V8"],
                v9=row["V9"],
                v10=row["V10"],
                v11=row["V11"],
                v12=row["V12"],
                v13=row["V13"],
                v14=row["V14"],
                v15=row["V15"],
                v16=row["V16"],
                v17=row["V17"],
                v18=row["V18"],
                v19=row["V19"],
                v20=row["V20"],
                v21=row["V21"],
                v22=row["V22"],
                v23=row["V23"],
                v24=row["V24"],
                v25=row["V25"],
                v26=row["V26"],
                v27=row["V27"],
                v28=row["V28"],
                class_label=int(row["Class"]) if "Class" in row else None,
                transaction_id=f"txn_{idx}",
            )
            transactions.append(transaction)

        return transactions

    def get_dataset_info(self) -> dict:
        """
        Get dataset statistics.

        Returns:
            dict: Dataset information
        """
        if self.df is None:
            self.load_dataset()

        fraud_count = int(self.df["Class"].sum())
        total_count = len(self.df)

        return {
            "total_transactions": total_count,
            "fraud_transactions": fraud_count,
            "legitimate_transactions": total_count - fraud_count,
            "fraud_percentage": round(fraud_count / total_count * 100, 2),
            "amount_range": {
                "min": float(self.df["Amount"].min()),
                "max": float(self.df["Amount"].max()),
                "mean": float(self.df["Amount"].mean()),
            },
            "time_range": {
                "min": float(self.df["Time"].min()),
                "max": float(self.df["Time"].max()),
            },
        }


# Singleton instance
data_loader = DataLoader()
