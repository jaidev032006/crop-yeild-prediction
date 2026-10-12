"""
Model training and 5-algorithm benchmark pipeline.
Compares Random Forest, Decision Tree, Gaussian Naive Bayes, KNN, and XGBoost.
Computes 5-fold cross-validation, confusion matrices, and classification metrics.
Saves the best model and performance benchmarks to disk.
"""
import os
import sys
import json
import logging
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any

# Ensure project root is on sys.path
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
from models.yield_model import YieldEstimator

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SAVED_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saved_models')
os.makedirs(SAVED_MODELS_DIR, exist_ok=True)

MODEL_OUTPUT_PATH = os.path.join(SAVED_MODELS_DIR, 'best_crop_model.joblib')
LABEL_ENCODER_PATH = os.path.join(SAVED_MODELS_DIR, 'label_encoder.joblib')
METRICS_PATH = os.path.join(SAVED_MODELS_DIR, 'classification_metrics.json')
CONFUSION_MATRIX_PATH = os.path.join(SAVED_MODELS_DIR, 'confusion_matrix.json')

def get_candidate_models() -> Dict[str, Any]:
    """Define the 5 candidate classification pipelines."""
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

def train_and_evaluate_all():
    """Execute complete 5-model training, 5-fold CV, and benchmarking suite."""
    logger.info("Loading crop recommendation dataset...")
    df = load_crop_dataset()
    
    X = df[EXPECTED_FEATURES]
    y_raw = df['label']
    
    # Encode target labels
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    classes = list(le.classes_)
    
    # Train-test split (80-20 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    models = get_candidate_models()
    
    all_metrics = {}
    best_model_name = None
    best_cv_score = -1.0
    best_fitted_model = None
    best_cm = None
    best_class_report = None
    
    logger.info("Evaluating 5 ML architectures across 5-Fold Stratified Cross-Validation...")
    
    for name, model in models.items():
        logger.info(f"--> Training and evaluating {name}...")
        
        # 5-Fold CV on entire dataset
        cv_scores = cross_val_score(model, X, y, cv=skf, scoring='accuracy', n_jobs=-1)
        mean_cv = float(np.mean(cv_scores))
        std_cv = float(np.std(cv_scores))
        
        # Fit on 80% train set for holdout evaluation
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        test_acc = float(accuracy_score(y_test, y_pred))
        precision_macro = float(precision_score(y_test, y_pred, average='macro', zero_division=0))
        recall_macro = float(recall_score(y_test, y_pred, average='macro', zero_division=0))
        f1_macro = float(f1_score(y_test, y_pred, average='macro', zero_division=0))
        
        all_metrics[name] = {
            'cv_mean_accuracy': round(mean_cv * 100, 2),
            'cv_std': round(std_cv * 100, 2),
            'test_accuracy': round(test_acc * 100, 2),
            'precision_macro': round(precision_macro * 100, 2),
            'recall_macro': round(recall_macro * 100, 2),
            'f1_macro': round(f1_macro * 100, 2),
            'is_best': False
        }
        
        logger.info(f"    {name} CV Acc: {mean_cv*100:.2f}% (±{std_cv*100:.2f}%), Test Acc: {test_acc*100:.2f}%, F1: {f1_macro*100:.2f}%")
        
        if mean_cv > best_cv_score:
            best_cv_score = mean_cv
            best_model_name = name
            best_fitted_model = model
            best_cm = confusion_matrix(y_test, y_pred).tolist()
            best_class_report = classification_report(y_test, y_pred, target_names=classes, output_dict=True)

    # Re-fit the best model on the complete dataset for production deployment
    logger.info(f"Best performing architecture: {best_model_name} with {best_cv_score*100:.2f}% CV Accuracy")
    all_metrics[best_model_name]['is_best'] = True
    
    best_fitted_model.fit(X, y)
    
    # Save best model and encoder
    joblib.dump(best_fitted_model, MODEL_OUTPUT_PATH)
    joblib.dump(le, LABEL_ENCODER_PATH)
    logger.info(f"Saved best model to {MODEL_OUTPUT_PATH}")
    
    # Save classification benchmark metrics
    metrics_summary = {
        'best_model': best_model_name,
        'features': EXPECTED_FEATURES,
        'classes': classes,
        'num_samples': len(df),
        'num_classes': len(classes),
        'models': all_metrics,
        'classification_report': best_class_report
    }
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics_summary, f, indent=2)
    logger.info(f"Saved benchmark metrics to {METRICS_PATH}")
    
    # Save confusion matrix payload for Plotly rendering
    cm_payload = {
        'model_name': best_model_name,
        'classes': classes,
        'matrix': best_cm
    }
    with open(CONFUSION_MATRIX_PATH, 'w') as f:
        json.dump(cm_payload, f, indent=2)
        
    # Also train the Yield Regressor
    logger.info("Training Yield Estimation Regressor...")
    yield_est = YieldEstimator()
    yield_est.train_yield_model(df)
    logger.info("Yield Regressor training complete.")
    
    return metrics_summary

if __name__ == '__main__':
    train_and_evaluate_all()
