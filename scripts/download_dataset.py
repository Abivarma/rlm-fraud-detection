"""Script to download Kaggle Credit Card Fraud dataset."""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

print("""
╔══════════════════════════════════════════════════════════════╗
║  Kaggle Credit Card Fraud Detection Dataset Download        ║
╚══════════════════════════════════════════════════════════════╝

This script will guide you through downloading the dataset.

MANUAL DOWNLOAD INSTRUCTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Visit: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

2. Click "Download" button (requires Kaggle account)

3. Extract creditcard.csv from the downloaded ZIP

4. Place creditcard.csv in: ./backend/data/

Alternative datasets (same format):
- https://www.kaggle.com/datasets/kartik2112/fraud-detection
- https://www.kaggle.com/datasets/nelgiriyewithana/credit-card-fraud-detection-dataset-2023

AUTOMATIC DOWNLOAD (requires Kaggle API):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To use Kaggle API:

1. Install: pip install kaggle

2. Get API credentials:
   - Go to https://www.kaggle.com/settings
   - Click "Create New API Token"
   - Download kaggle.json
   - Place in ~/.kaggle/kaggle.json (Linux/Mac) or C:\\Users\\<user>\\.kaggle\\kaggle.json (Windows)

3. Run this script again with --auto flag:
   python scripts/download_dataset.py --auto

""")


def download_with_kaggle_api():
    """Download dataset using Kaggle API."""
    try:
        import kaggle
        from kaggle.api.kaggle_api_extended import KaggleApi

        print("Initializing Kaggle API...")
        api = KaggleApi()
        api.authenticate()

        dataset = "mlg-ulb/creditcardfraud"
        data_dir = Path(__file__).parent.parent / "backend" / "data"
        data_dir.mkdir(exist_ok=True)

        print(f"Downloading dataset: {dataset}")
        print(f"Destination: {data_dir}")

        api.dataset_download_files(dataset, path=str(data_dir), unzip=True)

        csv_file = data_dir / "creditcard.csv"
        if csv_file.exists():
            print(f"\n✓ Success! Dataset downloaded to: {csv_file}")
            print(f"  File size: {csv_file.stat().st_size / 1024 / 1024:.1f} MB")
            return True
        else:
            print("\n✗ Error: creditcard.csv not found after download")
            return False

    except ImportError:
        print("✗ Kaggle package not installed. Install with: pip install kaggle")
        return False
    except Exception as e:
        print(f"✗ Error downloading dataset: {e}")
        return False


def check_dataset_exists():
    """Check if dataset already exists."""
    csv_file = Path(__file__).parent.parent / "backend" / "data" / "creditcard.csv"
    if csv_file.exists():
        print(f"✓ Dataset already exists: {csv_file}")
        print(f"  File size: {csv_file.stat().st_size / 1024 / 1024:.1f} MB")
        return True
    return False


if __name__ == "__main__":
    if check_dataset_exists():
        print("\nDataset is ready to use!")
        sys.exit(0)

    if "--auto" in sys.argv:
        success = download_with_kaggle_api()
        if success:
            print("\nDataset download complete! You can now start the application.")
        else:
            print("\nAutomatic download failed. Please download manually (see instructions above).")
        sys.exit(0 if success else 1)

    print("Run with --auto flag to attempt automatic download, or download manually as described above.")
