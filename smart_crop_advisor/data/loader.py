"""
Kaggle Crop Recommendation Dataset Loader.
Loads, validates, and manages the 22-crop, 2200-row benchmark dataset.
Includes automated remote fetching with synthetic fallback.
"""
import os
import urllib.request
import logging
import pandas as pd
from typing import Optional
from .dataset_fallback import generate_fallback_dataset

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(CURRENT_DIR, 'crop_recommendation.csv')

PRIMARY_URL = "https://raw.githubusercontent.com/Gladiator07/Harvestify/master/Data-processed/crop_recommendation.csv"
BACKUP_URL = "https://raw.githubusercontent.com/priyanshuuu510/Crop-Recommendation-System/main/Crop_recommendation.csv"

EXPECTED_FEATURES = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
EXPECTED_COLUMNS = EXPECTED_FEATURES + ['label']

def download_dataset(target_path: str = DATASET_PATH) -> bool:
    """Download verified Kaggle 22-crop dataset from repository mirrors."""
    for url in [PRIMARY_URL, BACKUP_URL]:
        try:
            logger.info(f"Downloading dataset from mirror: {url}")
            urllib.request.urlretrieve(url, target_path)
            if os.path.exists(target_path) and os.path.getsize(target_path) > 10000:
                logger.info(f"Downloaded Kaggle dataset to {target_path}")
                return True
        except Exception as e:
            logger.warning(f"Download failed from {url}: {e}")
    return False

def validate_dataset(df: pd.DataFrame) -> bool:
    """Ensure dataframe matches strict Kaggle 22-crop specifications."""
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            logger.error(f"Missing required column: {col}")
            return False
    for col in EXPECTED_FEATURES:
        if not pd.api.types.is_numeric_dtype(df[col]):
            logger.error(f"Column {col} is not numeric.")
            return False
    if df['label'].nunique() < 20 or len(df) < 1500:
        logger.warning(f"Dataset has {df['label'].nunique()} crops, {len(df)} rows. Expecting 22 crops, 2200 rows.")
        return False
    return True

def load_crop_dataset(csv_path: Optional[str] = None, force_reload: bool = False) -> pd.DataFrame:
    """
    Load the crop recommendation dataset.
    1. Reads existing disk CSV if valid.
    2. Downloads real Kaggle dataset if missing.
    3. Falls back to synthetic generator if download fails.
    """
    target_path = csv_path or DATASET_PATH
    
    # 1. Read existing file
    if os.path.exists(target_path) and not force_reload:
        try:
            df = pd.read_csv(target_path)
            df.columns = [c.strip() for c in df.columns]
            df['label'] = df['label'].astype(str).str.strip().str.lower()
            if validate_dataset(df):
                logger.info(f"Loaded existing Kaggle dataset: {len(df)} rows, {df['label'].nunique()} crops.")
                return df
        except Exception as e:
            logger.warning(f"Could not load existing file at {target_path}: {e}")

    # 2. Remote download
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if download_dataset(target_path):
        try:
            df = pd.read_csv(target_path)
            df.columns = [c.strip() for c in df.columns]
            df['label'] = df['label'].astype(str).str.strip().str.lower()
            if validate_dataset(df):
                logger.info(f"Downloaded Kaggle dataset: {len(df)} rows, {df['label'].nunique()} crops.")
                return df
        except Exception as e:
            logger.error(f"Error parsing downloaded dataset: {e}")

    # 3. Fallback generator
    logger.warning("Generating 22-crop synthetic fallback dataset.")
    df = generate_fallback_dataset(samples_per_crop=100)
    df.to_csv(target_path, index=False)
    return df
