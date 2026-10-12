"""
Crop Classification Training & 5-Model Benchmark Suite.
Compares:
1. Random Forest Classifier
2. XGBoost Classifier
3. Decision Tree Classifier
4. Gaussian Naive Bayes
5. K-Nearest Neighbors (with StandardScaler Pipeline)

Performs 5-Fold Stratified Cross-Validation, generates full Confusion Matrix
and Classification Reports, and saves champion artifacts using joblib.
"""
import os
import sys
import json
import logging
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier

from data.loader import load_crop_dataset, EXPECTED_FEATURES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

MODEL_OUTPUT_PATH = os.path.join(MODELS_DIR, 'crop_model.joblib')
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, 'label_encoder.joblib')
METRICS_OUTPUT_PATH = os.path.join(MODELS_DIR, 'crop_model_metrics.json')
CONFUSION_MATRIX_PATH = os.path.join(MODELS_DIR, 'confusion_matrix.json')

def build_model_zoo() -> Dict[str, Any]:
    """Return dictionary of the 5 candidate classification models."""
    return {
        'Random Forest': RandomForestClassifier(
            n_estimators=120, max_depth=15, random_state=42, n_jobs=-1
        ),
        'XGBoost': XGBClassifier(
            n_estimators=100, learning_rate=0.1, max_depth=6,
            random_state=42, eval_metric='mlogloss', n_jobs=-1
        ),
        'Decision Tree': DecisionTreeClassifier(
            max_depth=12, random_state=42
        ),
        'Naive Bayes': GaussianNB(),
        'KNN': Pipeline([
            ('scaler', StandardScaler()),
            ('knn', KNeighborsClassifier(n_neighbors=5, metric='minkowski'))
        ])
    }

def run_training_pipeline() -> Dict[str, Any]:
    """Execute complete training, 5-fold CV benchmarking, and artifact serialization."""
    logger.info("Loading Kaggle 22-Crop dataset...")
    df = load_crop_dataset()
    
    X = df[EXPECTED_FEATURES]
    y_raw = df['label']
    
    # Target encoding
    encoder = LabelEncoder()
    y = encoder.fit_transform(y_raw)
    class_names = list(encoder.classes_)
    
    # 80-20 Stratified Split for holdout evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    models = build_model_zoo()
    
    metrics_summary = {}
    best_model_name = None
    best_cv_score = -1.0
    best_model_instance = None
    best_cm = None
    best_classification_rep = None

    logger.info("Beginning 5-Fold Stratified Cross-Validation on all 5 architectures...")
    
    for name, model in models.items():
        logger.info(f"-> Benchmarking {name}...")
        
        # 5-Fold CV
        cv_scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy', n_jobs=-1)
        mean_cv = float(np.mean(cv_scores))
        std_cv = float(np.std(cv_scores))
        
        # Train on 80% train set
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        test_acc = float(accuracy_score(y_test, y_pred))
        precision_macro = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
        recall_macro = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
        f1_macro = float(f1_score(y_test, y_pred, average='macro', zero_division=0))
        
        metrics_summary[name] = {
            'cv_mean_accuracy': round(mean_cv * 100, 2),
            'cv_std': round(std_cv * 100, 2),
            'test_accuracy': round(test_acc * 100, 2),
            'precision_macro': round(precision_macro * 100, 2),
            'recall_macro': round(recall_macro * 100, 2),
            'f1_macro': round(f1_macro * 100, 2),
            'is_champion': False
        }
        
        logger.info(f"   {name} | CV: {mean_cv*100:.2f}% (±{std_cv*100:.2f}%) | Test: {test_acc*100:.2f}% | F1: {f1_macro*100:.2f}%")
        
        if mean_cv > best_cv_score:
            best_cv_score = mean_cv
            best_model_name = name
            best_model_instance = model
            best_cm = confusion_matrix(y_test, y_pred).tolist()
            best_classification_rep = classification_report(y_test, y_pred, target_names=class_names, output_dict=True)

    metrics_summary[best_model_name]['is_champion'] = True
    logger.info(f"Champion Architecture Selected: {best_model_name} with {best_cv_score*100:.2f}% CV Accuracy")
    
    # Re-train champion model on 100% of data for production deployment
    best_model_instance.fit(X, y)
    
    # Persist model and encoder
    joblib.dump(best_model_instance, MODEL_OUTPUT_PATH)
    joblib.dump(encoder, LABEL_ENCODER_PATH)
    logger.info(f"Saved production model to {MODEL_OUTPUT_PATH}")
    
    # Persist metrics and reports
    benchmark_payload = {
        'champion_model': best_model_name,
        'features': EXPECTED_FEATURES,
        'classes': class_names,
        'total_samples': len(df),
        'total_classes': len(class_names),
        'models': metrics_summary,
        'classification_report': best_classification_rep
    }
    with open(METRICS_OUTPUT_PATH, 'w') as f:
        json.dump(benchmark_payload, f, indent=2)
        
    cm_payload = {
        'model_name': best_model_name,
        'classes': class_names,
        'matrix': best_cm
    }
    with open(CONFUSION_MATRIX_PATH, 'w') as f:
        json.dump(cm_payload, f, indent=2)
        
    logger.info("Crop model training and benchmarking completed successfully.")
    return benchmark_payload

if __name__ == '__main__':
    run_training_pipeline()
