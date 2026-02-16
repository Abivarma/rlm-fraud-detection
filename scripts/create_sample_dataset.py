#!/usr/bin/env python3
"""Create a sample dataset for testing without Kaggle download."""

import numpy as np
import pandas as pd
from pathlib import Path

print("Creating sample fraud detection dataset...")

# Set random seed for reproducibility
np.random.seed(42)

# Number of transactions
n_transactions = 1000
n_fraud = 20  # 2% fraud rate

print(f"Generating {n_transactions} transactions ({n_fraud} fraudulent)...")

# Create time values (seconds)
time = np.sort(np.random.uniform(0, 172800, n_transactions))  # 48 hours

# Create amount values
legitimate_amounts = np.random.lognormal(mean=3.5, sigma=1.2, size=n_transactions - n_fraud)

# Fraudulent amounts - mix of small test transactions and large amounts
fraud_small = np.random.uniform(0.01, 5, n_fraud // 2)
fraud_large = np.random.uniform(500, 2000, n_fraud - n_fraud // 2)
fraud_amounts = np.concatenate([fraud_small, fraud_large])

amounts = np.concatenate([legitimate_amounts, fraud_amounts])

# Create V1-V28 (PCA features)
# Legitimate transactions - normal distribution
v_features_legit = np.random.randn(n_transactions - n_fraud, 28)

# Fraudulent transactions - anomalous patterns
v_features_fraud = np.random.randn(n_fraud, 28) * 3  # Higher variance
# Add specific outliers
v_features_fraud[:, 0] += np.random.choice([-5, 5], n_fraud)
v_features_fraud[:, 1] += np.random.choice([-4, 4], n_fraud)

v_features = np.vstack([v_features_legit, v_features_fraud])

# Create labels (0 = legitimate, 1 = fraud)
labels = np.array([0] * (n_transactions - n_fraud) + [1] * n_fraud)

# Shuffle all data together
indices = np.random.permutation(n_transactions)
time = time[indices]
amounts = amounts[indices]
v_features = v_features[indices]
labels = labels[indices]

# Create DataFrame
data = {
    'Time': time,
    'Amount': amounts,
}

# Add V1-V28 features
for i in range(1, 29):
    data[f'V{i}'] = v_features[:, i-1]

data['Class'] = labels

df = pd.DataFrame(data)

# Save to CSV
output_dir = Path(__file__).parent.parent / 'backend' / 'data'
output_dir.mkdir(exist_ok=True)
output_file = output_dir / 'creditcard.csv'

df.to_csv(output_file, index=False)

print(f"✓ Sample dataset created: {output_file}")
print(f"  Total transactions: {len(df):,}")
print(f"  Fraudulent: {df['Class'].sum()} ({df['Class'].sum() / len(df) * 100:.2f}%)")
print(f"  Legitimate: {(df['Class'] == 0).sum()} ({(df['Class'] == 0).sum() / len(df) * 100:.2f}%)")
print(f"  File size: {output_file.stat().st_size / 1024:.1f} KB")
print()
print("Note: This is a SAMPLE dataset for testing.")
print("For production use, download the full Kaggle dataset:")
print("https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud")
