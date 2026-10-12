# Smart Crop Advisor — AI Precision Agriculture & Profit Advisory

**Smart Crop Advisor** is a farmer-focused agronomic decision-support platform that combines multi-model machine learning, explainable AI (SHAP), live meteorological telemetry (Open-Meteo), and economic optimization (CACP MSP rates) into an intuitive, multilingual Streamlit web application.

---

## 🌟 Key Upgrades & Architectural Capabilities

### 1. Empirical Foundation & Multi-Model Benchmarking
- **22-Crop Empirical Dataset:** Replaced synthetic generation with the real Kaggle Crop Recommendation Dataset (2,200 rows across 22 crops: *Rice, Maize, Chickpea, Kidneybeans, Pigeonpeas, Mothbeans, Mungbean, Blackgram, Lentil, Pomegranate, Banana, Mango, Grapes, Watermelon, Muskmelon, Apple, Orange, Papaya, Coconut, Cotton, Jute, Coffee*).
- **5-Algorithm Comparison:** Trains and benchmarks **Random Forest**, **XGBoost**, **Decision Tree**, **Gaussian Naive Bayes**, and **K-Nearest Neighbors**.
- **5-Fold Cross-Validation:** Full 5-fold stratified cross-validation, confusion matrix, and macro Precision/Recall/F1 reporting across all 22 classes.
- **Trained Yield Regressor:** Continuous `RandomForestRegressor` estimating realistic crop yield (Quintals/Hectare) calibrated with ICAR/NHB agronomic baselines.

### 2. Intelligent Farmer Decision Support
1. **Top-3 Recommendations:** Uses `predict_proba()` to compute probabilistic confidence rankings across top-3 alternatives.
2. **Explainable AI (SHAP):** Computes Shapley feature attributions to provide interactive impact bar charts and plain-language driver summaries (e.g., *"Abundant rainfall of 202.9 mm and Nitrogen level of 90 kg/ha were the strongest natural factors driving Rice"*).
3. **Profit-Based Ranking:** Incorporates cultivation cost, MSP/market rates, and yield to rank candidates by estimated net profit (₹/Hectare).
4. **Smart Fertilizer Plan:** Translates N-P-K soil gaps into commercial fertilizer doses (Urea 46% N, SSP 16% P₂O₅, MOP 60% K₂O in kg/acre), phased split schedules, and organic alternatives (FYM, Vermicompost, Green Manure, Neem Cake).
5. **Crop Rotation & Calendar:** Identifies exhaustive cereal crops and recommends restorative leguminous rotations (Kharif → Rabi → Zaid) with a 12-month calendar.
6. **Real 30-Day Rainfall:** Fetches empirical 30-day cumulative precipitation and current weather telemetry directly from the Open-Meteo API.
7. **What-If Climate Simulator:** Real-time sensitivity sliders to evaluate how temperature, rainfall, and pH shifts alter crop viability.
8. **Disease & Pest Alerts:** Early warnings triggered by temperature and relative humidity thresholds with organic/IPM preventive protocols.
9. **Multilingual Interface & Voice Output:** English, தமிழ் (Tamil), and हिन्दी (Hindi) with text-to-speech voice narration.
10. **Branded PDF Export:** Single-click comprehensive advisory PDF download generated via ReportLab.

---

## 📁 Project Structure

```text
Codebind technologies project/
├── .gitignore                    # Git ignore file for venv, cache & temporary files
├── requirements.txt              # Pinned compatible dependencies
├── README.md                     # Documentation and usage guide
├── app.py                        # Streamlit web application (entrypoint)
├── app_tkinter.py                # Legacy Tkinter desktop application (preserved)
│
├── data/
│   ├── loader.py                 # Kaggle 22-crop dataset loader with auto-download
│   ├── fallback_generator.py     # 22-crop agronomic fallback generator
│   ├── crop_recommendation.csv   # Kaggle dataset (2200 rows, 22 crops)
│   └── economics.py              # CACP MSP pricing & crop taxonomy catalog
│
├── models/
│   ├── train.py                  # 5-algorithm trainer & 5-fold cross-validation
│   ├── predictor.py              # Top-3 probabilistic predictor
│   ├── explainer.py              # SHAP TreeExplainer & natural language generator
│   ├── yield_model.py            # RandomForestRegressor for crop yield
│   └── saved_models/             # Persisted joblib models & JSON benchmark metrics
│
├── services/
│   ├── weather.py                # Open-Meteo live & 30-day historical precipitation
│   ├── fertilizer.py             # NPK deficit to Urea/SSP/MOP (kg/acre) & organics
│   ├── rotation.py               # Kharif/Rabi/Zaid succession & 12-month calendar
│   ├── disease_alert.py          # Weather-triggered pathogen risk matrix
│   └── pdf_report.py             # Branded PDF report generator (ReportLab)
│
├── ui/
│   ├── translations.py           # Multilingual dictionary: English, தமிழ், हिन्दी
│   ├── styles.py                 # Dark and Light theme styling
│   └── charts.py                 # Interactive Plotly charts (SHAP, benchmarks, CM)
│
├── utils/
│   ├── validator.py              # Input threshold validator & soil warnings
│   └── speech.py                 # Multi-language text-to-speech (TTS) engine
│
└── tests/
    ├── test_models.py            # Pytest tests for data loader, predictor, and SHAP
    └── test_fertilizer.py        # Pytest tests for fertilizer math, rotation & disease
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup
```bash
# Navigate to project directory
cd "d:\projects\Codebind technologies project\Codebind technologies project"

# Create virtual environment using uv or python
uv venv --python 3.11 .venv

# Install dependencies
uv pip install -r requirements.txt
```

### 2. Model Training & Benchmarking (Optional — Pre-trained)
```bash
.\.venv\Scripts\python.exe models/train.py
```
*Evaluates Random Forest, XGBoost, Decision Tree, Naive Bayes, and KNN across 5-Fold Stratified Cross-Validation and persists champion models to `models/saved_models/`.*

### 3. Run Automated Tests
```bash
.\.venv\Scripts\python.exe -m pytest tests
```

### 4. Launch Web Application
```bash
.\.venv\Scripts\python.exe -m streamlit run app.py
```
Open **`http://localhost:8501`** in any desktop or mobile browser.

### 5. Run Legacy Desktop Tkinter App (Optional)
```bash
.\.venv\Scripts\python.exe app_tkinter.py
```
