"""
Smart Crop Advisor — Streamlit Web Application.
Next-Gen AI Precision Agriculture, Climate Intelligence & Profit Advisory.
"""
import os
import sys
import json
import logging
import datetime
import pandas as pd
import numpy as np
import streamlit as st

# Configure sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ui.translations import t, TRANSLATIONS
from ui.styles import get_theme_css
from ui.charts import (
    create_shap_bar_chart,
    create_model_comparison_chart,
    create_confusion_matrix_heatmap,
    create_confidence_donut,
    create_profit_comparison_chart
)
from models.predictor import CropPredictor
from models.explainer import CropExplainer
from services.weather import WeatherService, AGRICULTURAL_HUBS
from services.fertilizer import FertilizerService
from services.rotation import RotationPlanner
from services.disease_alert import DiseaseAlertService
from services.pdf_report import PDFReportGenerator
from utils.validator import validate_inputs
from utils.speech import synthesize_speech

logger = logging.getLogger(__name__)

# Page Configuration
st.set_page_config(
    page_title="Smart Crop Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if 'history' not in st.session_state:
    history_file = os.path.join(PROJECT_ROOT, 'prediction_history.csv')
    if os.path.exists(history_file):
        try:
            st.session_state.history = pd.read_csv(history_file).to_dict('records')
        except Exception:
            st.session_state.history = []
    else:
        st.session_state.history = []

if 'last_prediction' not in st.session_state:
    st.session_state.last_prediction = None

@st.cache_resource
def get_ml_engine():
    """Cache and load ML predictor and SHAP explainer."""
    predictor = CropPredictor()
    explainer = CropExplainer(predictor)
    return predictor, explainer

predictor, explainer = get_ml_engine()

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.markdown("### ⚙️ **Settings & Language**")
    
    col_lang, col_theme = st.columns(2)
    with col_lang:
        lang_choice = st.selectbox(
            "Language",
            options=['en', 'ta', 'hi'],
            format_func=lambda x: {'en': 'English', 'ta': 'தமிழ்', 'hi': 'हिन्दी'}[x],
            index=0
        )
    with col_theme:
        theme_mode = st.selectbox(
            "Theme",
            options=['dark', 'light'],
            format_func=lambda x: t('dark_mode' if x == 'dark' else 'light_mode', lang_choice),
            index=0
        )

    st.markdown("---")
    st.markdown("### 🧭 **Navigation**")
    nav_option = st.radio(
        "Go to",
        options=[
            t('nav_predict', lang_choice),
            t('nav_analysis', lang_choice),
            t('nav_whatif', lang_choice),
            t('nav_history', lang_choice),
            t('nav_about', lang_choice)
        ],
        index=0
    )
    
    st.markdown("---")
    st.caption("🌾 **Smart Crop Advisor v2.0**")
    st.caption("22 Crops • 5 ML Architectures • Open-Meteo • SHAP XAI")

# Inject Theme CSS
st.markdown(get_theme_css(theme_mode), unsafe_allow_html=True)

# Main Banner
st.markdown(f"""
<div class="advisor-header-card">
    <div class="advisor-title">🌾 {t('app_title', lang_choice)}</div>
    <div class="advisor-subtitle">{t('app_subtitle', lang_choice)}</div>
</div>
""", unsafe_allow_html=True)

# ----------------- 1. CROP RECOMMENDATION TAB -----------------
if nav_option == t('nav_predict', lang_choice):
    st.markdown(f"<div class='section-headline'>🧪 {t('soil_climate_params', lang_choice)}</div>", unsafe_allow_html=True)
    
    # Regional Preset Selector
    preset_col1, preset_col2 = st.columns([2, 1])
    with preset_col1:
        selected_region = st.selectbox(
            f"📍 {t('select_preset', lang_choice)}",
            options=["-- Manual Input --"] + list(AGRICULTURAL_HUBS.keys()),
            index=0
        )
    with preset_col2:
        st.write("")
        st.write("")
        fetch_weather_btn = st.button(t('fetch_live_weather', lang_choice), use_container_width=True)

    # State variables for inputs
    default_vals = {
        'N': 85.0, 'P': 42.0, 'K': 40.0,
        'temperature': 24.5, 'humidity': 75.0,
        'ph': 6.5, 'rainfall': 140.0
    }

    if selected_region != "-- Manual Input --":
        lat, lon = AGRICULTURAL_HUBS[selected_region]
        if fetch_weather_btn or 'last_region' not in st.session_state or st.session_state.last_region != selected_region:
            st.session_state.last_region = selected_region
            with st.spinner("Fetching live weather and 30-day rainfall from Open-Meteo..."):
                weather_res = WeatherService.fetch_weather_and_30d_rainfall(lat, lon)
                st.session_state.fetched_temp = weather_res['temperature']
                st.session_state.fetched_humid = weather_res['humidity']
                st.session_state.fetched_rain = weather_res['rainfall_30d_mm']
                st.success(f"Loaded live weather for {selected_region}: {weather_res['temperature']}°C, {weather_res['humidity']}%, {weather_res['rainfall_30d_mm']} mm rainfall ({weather_res['source']})")

    cur_temp = st.session_state.get('fetched_temp', default_vals['temperature'])
    cur_humid = st.session_state.get('fetched_humid', default_vals['humidity'])
    cur_rain = st.session_state.get('fetched_rain', default_vals['rainfall'])

    # Sliders Grid
    col_n, col_p, col_k = st.columns(3)
    with col_n:
        input_n = st.slider(t('n_label', lang_choice), min_value=0.0, max_value=140.0, value=float(default_vals['N']), step=1.0)
    with col_p:
        input_p = st.slider(t('p_label', lang_choice), min_value=5.0, max_value=145.0, value=float(default_vals['P']), step=1.0)
    with col_k:
        input_k = st.slider(t('k_label', lang_choice), min_value=5.0, max_value=205.0, value=float(default_vals['K']), step=1.0)

    col_t, col_h, col_ph, col_r = st.columns(4)
    with col_t:
        input_temp = st.slider(t('temp_label', lang_choice), min_value=5.0, max_value=45.0, value=float(cur_temp), step=0.5)
    with col_h:
        input_humid = st.slider(t('humid_label', lang_choice), min_value=10.0, max_value=100.0, value=float(cur_humid), step=1.0)
    with col_ph:
        input_ph = st.slider(t('ph_label', lang_choice), min_value=3.5, max_value=9.5, value=float(default_vals['ph']), step=0.1)
    with col_r:
        input_rain = st.slider(t('rain_label', lang_choice), min_value=10.0, max_value=350.0, value=float(cur_rain), step=5.0)

    current_features = {
        'N': input_n, 'P': input_p, 'K': input_k,
        'temperature': input_temp, 'humidity': input_humid,
        'ph': input_ph, 'rainfall': input_rain
    }

    # Validate inputs
    is_valid, validation_warnings = validate_inputs(current_features)
    for warn in validation_warnings:
        st.warning(f"⚠️ {warn}")

    st.write("")
    predict_btn = st.button(t('btn_predict', lang_choice), type="primary", use_container_width=True)

    if predict_btn or st.session_state.last_prediction is not None:
        if predict_btn:
            with st.spinner("Analyzing soil nutrients, meteorological telemetry and multi-model probability curves..."):
                top_crops = predictor.predict_top_k(current_features, k=3)
                top_crop_name = top_crops[0]['crop']
                
                # Generate explainability
                xai_res = explainer.explain_prediction(current_features, top_crop_name)
                
                # Generate fertilizer plan
                fert_plan = FertilizerService.calculate_fertilizer_plan(current_features, top_crop_name)
                
                # Generate crop rotation
                rot_plan = RotationPlanner.get_rotation_plan(top_crop_name)
                
                # Generate disease alerts
                disease_alerts = DiseaseAlertService.get_alerts(top_crop_name, input_temp, input_humid)
                
                # Cache prediction state
                st.session_state.last_prediction = {
                    'features': current_features,
                    'top_crops': top_crops,
                    'xai': xai_res,
                    'fert_plan': fert_plan,
                    'rot_plan': rot_plan,
                    'disease_alerts': disease_alerts,
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Append to persistent history
                history_entry = {
                    'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'crop_1': top_crops[0]['display_name'],
                    'conf_1': f"{top_crops[0]['confidence_pct']}%",
                    'yield_1': f"{top_crops[0]['estimated_yield_q_ha']} Q/Ha",
                    'profit_1': f"₹{top_crops[0]['expected_profit_ha']:,}",
                    'crop_2': top_crops[1]['display_name'],
                    'conf_2': f"{top_crops[1]['confidence_pct']}%",
                    'crop_3': top_crops[2]['display_name'],
                    'conf_3': f"{top_crops[2]['confidence_pct']}%",
                    'N': input_n, 'P': input_p, 'K': input_k,
                    'temp': input_temp, 'humidity': input_humid, 'ph': input_ph, 'rainfall': input_rain
                }
                st.session_state.history.insert(0, history_entry)
                pd.DataFrame(st.session_state.history).to_csv(os.path.join(PROJECT_ROOT, 'prediction_history.csv'), index=False)

        pred_data = st.session_state.last_prediction
        top_crops = pred_data['top_crops']
        xai_res = pred_data['xai']
        fert_plan = pred_data['fert_plan']
        rot_plan = pred_data['rot_plan']
        disease_alerts = pred_data['disease_alerts']

        st.markdown("---")
        st.markdown(f"<div class='section-headline'>🏆 {t('top_crops_header', lang_choice)}</div>", unsafe_allow_html=True)

        # Top-3 Cards
        card_cols = st.columns(3)
        for idx, (col, crop_item) in enumerate(zip(card_cols, top_crops), start=1):
            with col:
                rank_class = f"crop-rank-{idx}"
                legume_tag = "🌿 Legume (Nitrogen Fixing)" if crop_item['is_legume'] else f"🌾 {crop_item['category'].title()}"
                
                st.markdown(f"""
                <div class="crop-card {rank_class}">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span class="badge-chip">#{crop_item['rank']} Choice</span>
                        <span style="font-weight: 700; color: #10b981; font-size: 1.1rem;">{crop_item['confidence_pct']}%</span>
                    </div>
                    <h3 style="margin: 4px 0 8px 0; color: #f9fafb;">{crop_item['display_name']}</h3>
                    <p style="margin: 0 0 12px 0; font-size: 0.85rem; color: #9ca3af;">{crop_item['season']} Season • {legume_tag}</p>
                    <hr style="border-color: rgba(75, 85, 99, 0.3); margin: 8px 0;">
                    <div style="margin-bottom: 6px;">
                        <span style="font-size: 0.85rem; color: #9ca3af;">{t('estimated_yield', lang_choice)}:</span><br>
                        <span class="metric-value-highlight">{crop_item['estimated_yield_q_ha']} Q/Ha</span>
                        <span style="font-size: 0.85rem; color: #9ca3af;">({crop_item['estimated_yield_tonnes_ha']} t/ha)</span>
                    </div>
                    <div style="margin-top: 10px;">
                        <span style="font-size: 0.85rem; color: #9ca3af;">{t('expected_profit', lang_choice)}:</span><br>
                        <span class="profit-pill">₹{crop_item['expected_profit_ha']:,} / Ha</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Economic Breakdown Chart & Confidence Donut
        chart_col1, chart_col2 = st.columns([2, 1])
        with chart_col1:
            fig_profit = create_profit_comparison_chart(top_crops, theme_mode)
            st.plotly_chart(fig_profit, use_container_width=True)
        with chart_col2:
            fig_donut = create_confidence_donut(top_crops, theme_mode)
            st.plotly_chart(fig_donut, use_container_width=True)

        # Explainable AI (SHAP)
        st.markdown(f"<div class='section-headline'>🧠 {t('shap_header', lang_choice)}</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="shap-callout">
            <b>Agronomic Driver Insight:</b><br>
            {xai_res['explanation_sentence']}
        </div>
        """, unsafe_allow_html=True)
        
        fig_shap = create_shap_bar_chart(xai_res['feature_impacts'], theme_mode)
        st.plotly_chart(fig_shap, use_container_width=True)

        # Smart Fertilizer Plan
        st.markdown(f"<div class='section-headline'>🧪 {t('fertilizer_header', lang_choice)}</div>", unsafe_allow_html=True)
        fert_cols = st.columns(3)
        com_fert = fert_plan['commercial_fertilizers_kg_acre']
        with fert_cols[0]:
            st.metric("Urea (46% N)", f"{com_fert['urea']} kg / acre", delta=f"Deficit: {fert_plan['deficits_kg_acre']['N']} kg N")
        with fert_cols[1]:
            st.metric("SSP (16% P₂O₅)", f"{com_fert['ssp']} kg / acre", delta=f"Deficit: {fert_plan['deficits_kg_acre']['P']} kg P")
        with fert_cols[2]:
            st.metric("MOP (60% K₂O)", f"{com_fert['mop']} kg / acre", delta=f"Deficit: {fert_plan['deficits_kg_acre']['K']} kg K")

        with st.expander("📅 Split Application Schedule & Organic Alternatives", expanded=True):
            st.markdown("#### Phased Field Application Timeline")
            split_df = pd.DataFrame(fert_plan['split_schedule'])[['stage', 'urea_kg', 'ssp_kg', 'mop_kg', 'timing', 'instructions']]
            split_df.columns = ['Crop Stage', 'Urea (kg/ac)', 'SSP (kg/ac)', 'MOP (kg/ac)', 'Timing Window', 'Field Application Guidelines']
            st.dataframe(split_df, use_container_width=True, hide_index=True)
            
            st.markdown("#### Recommended Organic Amendments")
            for org in fert_plan['organic_alternatives']:
                st.markdown(f"- **{org['name']}** ({org['quantity']}): {org['benefit']} *({org['application']})*")

        # Crop Rotation & Season Planner
        st.markdown(f"<div class='section-headline'>🔄 {t('rotation_header', lang_choice)}</div>", unsafe_allow_html=True)
        st.info(f"🌾 **Rotation Rationale:** {rot_plan['agronomic_rationale']}")
        
        rot_cols = st.columns(3)
        for idx, (col, next_c) in enumerate(zip(rot_cols, rot_plan['recommended_next_crops'])):
            with col:
                st.markdown(f"""
                <div style="background: rgba(31, 41, 55, 0.6); padding: 14px; border-radius: 10px; border: 1px solid rgba(75, 85, 99, 0.4);">
                    <span style="font-weight: 700; color: #10b981;">Option #{idx+1} ({rot_plan['next_season']} Season)</span>
                    <h4 style="margin: 4px 0;">{next_c['display_name']}</h4>
                    <p style="font-size: 0.85rem; color: #9ca3af; margin: 0;">Category: {next_c['category'].title()} • Sowing: {', '.join(next_c['sowing_months'])}</p>
                </div>
                """, unsafe_allow_html=True)

        # Disease & Pest Alerts
        st.markdown(f"<div class='section-headline'>⚠️ {t('disease_header', lang_choice)}</div>", unsafe_allow_html=True)
        for d in disease_alerts:
            badge_color = d['status_color']
            st.markdown(f"""
            <div style="border-left: 4px solid {badge_color}; background: rgba(31, 41, 55, 0.5); padding: 14px; border-radius: 8px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 1.05rem; font-weight: 700;">{d['name']} ({d['type']})</span>
                    <span style="background: {badge_color}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: 600;">{d['risk_level']}</span>
                </div>
                <p style="margin: 6px 0 4px 0; font-size: 0.9rem; color: #cbd5e1;"><b>Trigger Condition:</b> {d['trigger_reason']}</p>
                <p style="margin: 0 0 4px 0; font-size: 0.85rem; color: #9ca3af;"><b>Symptoms:</b> {d['symptoms']}</p>
                <p style="margin: 0; font-size: 0.85rem; color: #34d399;"><b>Preventive Control:</b> {d['prevention']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Action Buttons (PDF Report & TTS Voice Narration)
        st.markdown("---")
        action_col1, action_col2 = st.columns(2)
        
        with action_col1:
            pdf_bytes = PDFReportGenerator.generate_advisory_pdf(
                inputs=current_features,
                top_crops=top_crops,
                explanation=xai_res,
                fertilizer_plan=fert_plan,
                rotation_plan=rot_plan
            )
            st.download_button(
                label=f"📄 {t('download_pdf', lang_choice)}",
                data=pdf_bytes,
                file_name=f"Smart_Crop_Advisory_{top_crops[0]['crop']}_{datetime.date.today()}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with action_col2:
            if st.button(f"🔊 {t('generate_audio', lang_choice)}", use_container_width=True):
                with st.spinner(t('audio_generating', lang_choice)):
                    # Formulate concise speech text
                    speech_text = (
                        f"Recommended primary crop is {top_crops[0]['display_name']} with {top_crops[0]['confidence_pct']} percent suitability. "
                        f"Estimated yield is {top_crops[0]['estimated_yield_q_ha']} quintals per hectare, with expected net profit of {top_crops[0]['expected_profit_ha']} rupees. "
                        f"{xai_res['explanation_sentence']}"
                    )
                    audio_bytes = synthesize_speech(speech_text, lang=lang_choice)
                    if audio_bytes:
                        st.audio(audio_bytes, format='audio/mp3')
                        st.success("Voice narration synthesized successfully.")
                    else:
                        st.warning("Audio synthesis unavailable in offline mode.")

# ----------------- 2. MODEL BENCHMARKS & ANALYSIS TAB -----------------
elif nav_option == t('nav_analysis', lang_choice):
    st.markdown(f"<div class='section-headline'>📊 {t('analysis_header', lang_choice)}</div>", unsafe_allow_html=True)
    
    metrics_file = os.path.join(PROJECT_ROOT, 'models', 'saved_models', 'classification_metrics.json')
    cm_file = os.path.join(PROJECT_ROOT, 'models', 'saved_models', 'confusion_matrix.json')
    
    if os.path.exists(metrics_file):
        with open(metrics_file, 'r') as f:
            metrics_data = json.load(f)
            
        st.markdown(f"**Dataset Scale:** {metrics_data['num_samples']} rows across {metrics_data['num_classes']} unique crops. **Production Champion:** `{metrics_data['best_model']}`.")
        
        # Plotly Model Comparison
        fig_bench = create_model_comparison_chart(metrics_data['models'], theme_mode)
        st.plotly_chart(fig_bench, use_container_width=True)
        
        # Summary Table
        table_rows = []
        for m_name, vals in metrics_data['models'].items():
            table_rows.append({
                'Algorithm': m_name + (" ⭐ (Best)" if vals.get('is_best') else ""),
                '5-Fold CV Accuracy (%)': f"{vals['cv_mean_accuracy']}% ± {vals['cv_std']}%",
                'Test Set Accuracy (%)': f"{vals['test_accuracy']}%",
                'Precision Macro (%)': f"{vals['precision_macro']}%",
                'Recall Macro (%)': f"{vals['recall_macro']}%",
                'F1 Score Macro (%)': f"{vals['f1_macro']}%"
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
        
        # Confusion Matrix Heatmap
        if os.path.exists(cm_file):
            with open(cm_file, 'r') as f:
                cm_data = json.load(f)
            st.markdown(f"<div class='section-headline'>🎯 {t('confusion_matrix', lang_choice)}</div>", unsafe_allow_html=True)
            fig_cm = create_confusion_matrix_heatmap(cm_data, theme_mode)
            st.plotly_chart(fig_cm, use_container_width=True)
    else:
        st.warning("No benchmark metrics found. Run models/train.py to generate benchmarks.")

# ----------------- 3. WHAT-IF CLIMATE SIMULATOR TAB -----------------
elif nav_option == t('nav_whatif', lang_choice):
    st.markdown(f"<div class='section-headline'>🔮 {t('whatif_header', lang_choice)}</div>", unsafe_allow_html=True)
    st.caption(t('whatif_sub', lang_choice))
    
    sim_col1, sim_col2, sim_col3 = st.columns(3)
    with sim_col1:
        sim_rain = st.slider("Simulated Rainfall (mm)", min_value=15.0, max_value=350.0, value=150.0, step=5.0)
    with sim_col2:
        sim_temp = st.slider("Simulated Temperature (°C)", min_value=10.0, max_value=45.0, value=25.0, step=0.5)
    with sim_col3:
        sim_ph = st.slider("Simulated Soil pH", min_value=4.0, max_value=9.0, value=6.5, step=0.1)

    # Fixed representative soil nutrients for simulation
    sim_features = {
        'N': 80.0, 'P': 40.0, 'K': 40.0,
        'temperature': sim_temp, 'humidity': 75.0,
        'ph': sim_ph, 'rainfall': sim_rain
    }
    
    sim_top = predictor.predict_top_k(sim_features, k=3)
    
    st.markdown("#### Live Simulated Crop Response")
    sim_cols = st.columns(3)
    for idx, (col, c) in enumerate(zip(sim_cols, sim_top)):
        with col:
            st.markdown(f"""
            <div class="crop-card crop-rank-{idx+1}">
                <span class="badge-chip">Rank #{idx+1} Choice</span>
                <h3>{c['display_name']}</h3>
                <p style="color: #10b981; font-weight: 700; font-size: 1.2rem; margin: 4px 0;">{c['confidence_pct']}% Suitability</p>
                <p style="margin: 0; color: #9ca3af;">Est. Yield: <b>{c['estimated_yield_q_ha']} Q/Ha</b></p>
                <p style="margin: 4px 0 0 0; color: #34d399;">Profit: <b>₹{c['expected_profit_ha']:,} / Ha</b></p>
            </div>
            """, unsafe_allow_html=True)

# ----------------- 4. PREDICTION HISTORY TAB -----------------
elif nav_option == t('nav_history', lang_choice):
    st.markdown(f"<div class='section-headline'>📜 {t('history_header', lang_choice)}</div>", unsafe_allow_html=True)
    
    if st.session_state.history:
        hist_df = pd.DataFrame(st.session_state.history)
        
        hist_action_col1, hist_action_col2 = st.columns([1, 4])
        with hist_action_col1:
            if st.button(f"🗑️ {t('clear_history', lang_choice)}"):
                st.session_state.history = []
                csv_path = os.path.join(PROJECT_ROOT, 'prediction_history.csv')
                if os.path.exists(csv_path):
                    os.remove(csv_path)
                st.rerun()
        with hist_action_col2:
            csv_data = hist_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                f"📥 {t('export_csv', lang_choice)}",
                data=csv_data,
                file_name=f"crop_predictions_history_{datetime.date.today()}.csv",
                mime="text/csv"
            )

        st.dataframe(hist_df, use_container_width=True)
    else:
        st.info(t('no_history', lang_choice))

# ----------------- 5. ABOUT TAB -----------------
elif nav_option == t('nav_about', lang_choice):
    st.markdown(f"<div class='section-headline'>ℹ️ {t('about_header', lang_choice)}</div>", unsafe_allow_html=True)
    st.markdown(f"""
    **Smart Crop Advisor** upgrades traditional rule-based agricultural tools into a comprehensive, farmer-centric intelligence suite.
    
    ### 🔬 Architectural Pillars
    1. **Empirical Kaggle Benchmark Dataset:** 2,200 verified observation points across 22 crops (Rice, Maize, Chickpea, Cotton, Coffee, Mango, Banana, Grapes, Watermelon, etc.).
    2. **5-Model Benchmark Suite:** Rigorously evaluates Random Forest, XGBoost, Decision Tree, Gaussian Naive Bayes, and K-Nearest Neighbors via 5-Fold Stratified Cross Validation.
    3. **Live Meteorological Telemetry:** Open-Meteo API integration replaces synthetic rainfall formulas with empirical 30-day cumulative rainfall.
    4. **Explainable AI (SHAP):** TreeExplainer computes exact Shapley attributions, giving farmers transparent insight into why a crop is recommended.
    5. **Agronomic Economics & Crop Rotation:** CACP MSP rates and National Horticulture Board price indices dynamically rank crops by estimated net profitability (₹/Hectare) and design restorative leguminous crop rotations.
    """)
