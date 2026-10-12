"""Data package for Smart Crop Advisor."""
from .loader import load_crop_dataset, DATASET_PATH
from .economics import load_crop_economics

__all__ = ['load_crop_dataset', 'DATASET_PATH', 'load_crop_economics']
