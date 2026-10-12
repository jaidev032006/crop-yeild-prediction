from flask import Blueprint, render_template, request, jsonify, send_file, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Prediction
from app.services.ml_service import MLService
from app.services.pdf_service import PDFReportService
from app.services.location_service import LocationCropService
import os

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/')
@login_required
def index():
    """Prediction page with location selector, sliders, quick presets, and interactive result card"""
    presets = MLService.get_presets()
    states = LocationCropService.get_states()
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).limit(5).all()
    return render_template('predict/index.html', presets=presets, states=states, recent_predictions=recent_predictions)

@predict_bp.route('/api/states', methods=['GET'])
@login_required
def get_states():
    """Returns available Indian states/regions from the 730+ location dataset"""
    return jsonify({'success': True, 'states': LocationCropService.get_states()})

@predict_bp.route('/api/locations', methods=['GET'])
@login_required
def get_locations():
    """Returns locations filtered by state or search query"""
    state = request.args.get('state', '').strip()
    search = request.args.get('search', '').strip()
    locations = LocationCropService.get_locations(state=state, search=search)
    return jsonify({'success': True, 'locations': locations})

@predict_bp.route('/api/location-profile', methods=['GET'])
@login_required
def get_location_profile():
    """Returns full soil chemistry, traditional crops, and live weather for a location"""
    loc_id = request.args.get('id')
    name = request.args.get('name', '').strip()
    profile_data = LocationCropService.recommend_for_location(location_id=loc_id, address_name=name)
    if not profile_data:
        return jsonify({'success': False, 'message': 'Location not found in the regional dataset.'}), 404
    return jsonify({'success': True, 'data': profile_data})

@predict_bp.route('/api/location-predict', methods=['POST'])
@login_required
def api_location_predict():
    """
    Unified Endpoint: Takes a selected location (or coordinates),
    analyzes soil chemistry from the 730+ location dataset, fetches live weather,
    and runs the AI crop recommendation model.
    """
    try:
        data = request.get_json() or {}
        loc_id = data.get('location_id')
        name = data.get('location_name', '').strip()

        # Step 1: Run Location Analysis
        loc_res = LocationCropService.recommend_for_location(location_id=loc_id, address_name=name)
        if not loc_res:
            return jsonify({'success': False, 'message': 'Could not retrieve location profile.'}), 404

        inputs = loc_res['inputs']
        loc_info = loc_res['location']

        # Allow optional manual overrides from sliders if supplied
        N = float(data.get('n', inputs['n']))
        P = float(data.get('p', inputs['p']))
        K = float(data.get('k', inputs['k']))
        temp = float(data.get('temp', inputs['temp']))
        humid = float(data.get('humid', inputs['humid']))
        ph = float(data.get('ph', inputs['ph']))
        rain = float(data.get('rain', inputs['rain']))

        # Step 2: Run Random Forest precision prediction
        result = MLService.predict(N, P, K, temp, humid, ph, rain)

        # Step 3: Attach location context & traditional suitability
        loc_display = f"{loc_info['address']}, {loc_info['region']}"
        result['location'] = {
            'id': loc_info['id'],
            'address': loc_info['address'],
            'formatted': loc_info['formatted_address'],
            'region': loc_info['region'],
            'latitude': loc_info['latitude'],
            'longitude': loc_info['longitude'],
            'traditional_crops': loc_info['traditional_crops'],
            'soil_distributions': loc_info['soil_distributions'],
            'archive_model_crops': loc_res.get('archive_model_crops', []),
            'weather_source': loc_res['weather'].get('source', 'Live Weather')
        }

        # Step 4: Persist in Database
        prediction = Prediction(
            user_id=current_user.id,
            location=loc_display,
            nitrogen=N,
            phosphorus=P,
            potassium=K,
            temperature=temp,
            humidity=humid,
            ph=ph,
            rainfall=rain,
            predicted_crop=result['crop'],
            confidence=result['confidence'],
            yield_estimate=result['yield_estimate'],
            yield_efficiency=result['yield_efficiency'],
            fertilizer_recommendation=result['fertilizer_recommendation']
        )
        db.session.add(prediction)
        db.session.commit()

        result['prediction_id'] = prediction.id
        result['success'] = True
        return jsonify(result)

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@predict_bp.route('/api/presets', methods=['GET'])
@login_required
def get_presets():
    """Returns presets for chips"""
    return jsonify({'success': True, 'presets': MLService.get_presets()})

@predict_bp.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    """
    Executes prediction, calculates yield and fertilizer advice, stores to DB.
    """
    try:
        data = request.get_json() or {}
        
        N = float(data.get('n', 90))
        P = float(data.get('p', 42))
        K = float(data.get('k', 43))
        temp = float(data.get('temp', 24.0))
        humid = float(data.get('humid', 82.0))
        ph = float(data.get('ph', 6.5))
        rain = float(data.get('rain', 200.0))
        loc_name = data.get('location', '').strip() or 'Custom Soil Lab'
        
        # Validation checks
        if not (0 <= N <= 250 and 0 <= P <= 250 and 0 <= K <= 300):
            return jsonify({'success': False, 'message': 'Nutrient values are outside standard limits (N: 0-250, P: 0-250, K: 0-300).'}), 400
        if not (0 <= temp <= 60 and 0 <= humid <= 100 and 0 <= ph <= 14 and 0 <= rain <= 1000):
            return jsonify({'success': False, 'message': 'Environmental inputs must be within valid physical ranges.'}), 400
        
        # Run ML model
        result = MLService.predict(N, P, K, temp, humid, ph, rain)
        
        # Store in database
        prediction = Prediction(
            user_id=current_user.id,
            location=loc_name,
            nitrogen=N,
            phosphorus=P,
            potassium=K,
            temperature=temp,
            humidity=humid,
            ph=ph,
            rainfall=rain,
            predicted_crop=result['crop'],
            confidence=result['confidence'],
            yield_estimate=result['yield_estimate'],
            yield_efficiency=result['yield_efficiency'],
            fertilizer_recommendation=result['fertilizer_recommendation']
        )
        db.session.add(prediction)
        db.session.commit()
        
        result['prediction_id'] = prediction.id
        result['success'] = True
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@predict_bp.route('/report/<int:prediction_id>')
@login_required
def download_report(prediction_id):
    """Generates and downloads branded PDF report"""
    prediction = Prediction.query.get_or_404(prediction_id)
    if prediction.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        flash('Unauthorized to download this report.', 'error')
        return redirect(url_for('predict.index'))
        
    pdf_buffer = PDFReportService.generate_prediction_report(prediction, current_user)
    filename = f"AgriSmart_Report_{prediction.predicted_crop}_{prediction.id}.pdf"
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )

@predict_bp.route('/api/history')
@login_required
def get_history():
    """Returns past prediction records for current user"""
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    return jsonify({
        'success': True,
        'predictions': [p.to_dict() for p in predictions]
    })
