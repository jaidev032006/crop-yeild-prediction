"""
Dataset Loader for Smart Crop Advisor.
Loads the Kaggle 22-Crop Recommendation Dataset (2200 rows).
Downloads from remote repository if missing or falls back to synthetic generator.
"""
import os
import urllib.request
import logging
import pandas as pd
from typing import Optional
from .fallback_generator import generate_fallback_dataset

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, 'crop_recommendation.csv')

# Reliable raw mirrors for the 22-crop Kaggle dataset
PRIMARY_URL = "https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv"
BACKUP_URL = "https://raw.githubusercontent.com/priyanshuuu510/Crop-Recommendation-System/main/Crop_recommendation.csv"

EXPECTED_FEATURES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
EXPECTED_COLUMNS = EXPECTED_FEATURES + ['label']

def download_dataset(target_path: str = DATASET_PATH) -> bool:
    """Download Kaggle dataset from reliable GitHub mirrors."""
    for url in [PRIMARY_URL, BACKUP_URL]:
        try:
            logger.info(f"Attempting to download dataset from: {url}")
            urllib.request.urlretrieve(url, target_path)
            if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
                logger.info(f"Successfully downloaded dataset to {target_path}")
                return True
        except Exception as e:
            logger.warning(f"Download from {url} failed: {e}")
    return False

def validate_dataset(df: pd.DataFrame) -> bool:
    """Validate that dataframe has required columns and at least 20 crops."""
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            logger.error(f"Missing expected column: {col}")
            return False
    # Check numeric types
    for col in EXPECTED_FEATURES:
        if not pd.api.types.is_numeric_dtype(df[col]):
            return False
    # Check minimum crops
    if df['label'].nunique() < 20 or len(df) < 1500:
        logger.warning(f"Dataset has only {df['label'].nunique()} crops and {len(df)} rows.")
        return False
    return True

def load_crop_dataset(csv_path: Optional[str] = None, force_reload: bool = False) -> pd.DataFrame:
    """
    Load the crop dataset.
    1. Reads from csv_path if provided, else DATASET_PATH.
    2. If missing or invalid, downloads Kaggle dataset.
    3. If download fails, generates 22-crop fallback.
    """
    target_path = csv_path or DATASET_PATH
    
    # 1. Check if valid dataset exists on disk
    if os.path.exists(target_path) and not force_reload:
        try:
            df = pd.read_csv(target_path)
            # Normalize column names & label strings
            df.columns = [c.strip() for c in df.columns]
            df['label'] = df['label'].astype(str).str.strip().str.lower()
            if validate_dataset(df):
                logger.info(f"Loaded existing dataset from {target_path} ({len(df)} rows, {df['label'].nunique()} crops)")
                return df
            else:
                logger.warning(f"Existing file at {target_path} failed validation. Will re-fetch.")
        except Exception as e:
            logger.warning(f"Failed reading {target_path}: {e}")

    # 2. Attempt remote download
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if download_dataset(target_path):
        try:
            df = pd.read_csv(target_path)
            df.columns = [c.strip() for c in df.columns]
            df['label'] = df['label'].astype(str).str.strip().str.lower()
            if validate_dataset(df):
                logger.info(f"Loaded newly downloaded dataset ({len(df)} rows, {df['label'].nunique()} crops)")
                return df
        except Exception as e:
            logger.error(f"Error parsing downloaded dataset: {e}")

    # 3. Fallback to synthetic generator
    logger.warning("Falling back to synthetic 22-crop generator.")
    df = generate_fallback_dataset(samples_per_crop=100)
    df.to_csv(target_path, index=False)
    return df

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    df = load_crop_dataset()
    print(f"Dataset loaded: {len(df)} rows, {df['label'].nunique()} crops.")
    print("Crops:", sorted(df['label'].unique()))
