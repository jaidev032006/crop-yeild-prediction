from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Prediction, Order, Feedback, Product
import requests
import logging

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Dashboard home"""
    # Recent predictions
    recent_predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).limit(3).all()
    latest_prediction = recent_predictions[0] if recent_predictions else None
    
    # Active orders
    active_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).limit(3).all()
    
    # Stats
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    total_orders = Order.query.filter_by(user_id=current_user.id).count()
    total_feedback = Feedback.query.filter_by(user_id=current_user.id).count()
    
    featured_products = Product.query.filter_by(is_active=True).limit(4).all()
    
    return render_template(
        'dashboard/index.html',
        user=current_user,
        latest_prediction=latest_prediction,
        recent_predictions=recent_predictions,
        active_orders=active_orders,
        total_predictions=total_predictions,
        total_orders=total_orders,
        total_feedback=total_feedback,
        featured_products=featured_products
    )

@dashboard_bp.route('/api/weather')
@login_required
def get_weather():
    """
    Fetches real-time weather parameters from Open-Meteo API.
    Supports either (lat, lon) coordinates for the user's live browser location
    or query by city name.
    """
    lat_arg = request.args.get('lat')
    lon_arg = request.args.get('lon')
    city = request.args.get('city', '').strip()
    
    city_name = city or getattr(current_user, 'location', 'Pune') or 'Pune'
    state_name = ''
    country = 'India'
    lat = None
    lon = None
    
    try:
        if lat_arg and lon_arg:
            lat = float(lat_arg)
            lon = float(lon_arg)
            
            # Reverse geocode to find exact locality & state name
            try:
                rev_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
                rev_res = requests.get(rev_url, timeout=4).json()
                city_name = rev_res.get('locality') or rev_res.get('city') or rev_res.get('localityInfo', {}).get('administrative', [{}])[0].get('name', 'My Location')
                state_name = rev_res.get('principalSubdivision', '')
                country = rev_res.get('countryName', 'India')
            except Exception:
                city_name = city or 'Current Location'
                state_name = ''
        else:
            if not city_name:
                city_name = 'Pune'
            # 1. Geocoding
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
            geo_res = requests.get(geo_url, timeout=5).json()
            
            if "results" in geo_res and geo_res["results"]:
                location = geo_res["results"][0]
                lat = location["latitude"]
                lon = location["longitude"]
                city_name = location.get("name", city_name)
                state_name = location.get("admin1", "")
                country = location.get("country", "India")
            else:
                lat = 18.5204
                lon = 73.8567
                state_name = 'Maharashtra'
        
        # 2. Detailed current forecast
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m&daily=precipitation_sum,temperature_2m_max,temperature_2m_min&timezone=auto"
        w_res = requests.get(weather_url, timeout=6).json()
        
        curr = w_res.get("current", {})
        temp = curr.get("temperature_2m", 27.1)
        humidity = curr.get("relative_humidity_2m", 65.0)
        daily_rain = curr.get("precipitation", 0.0)
        wind_speed = curr.get("wind_speed_10m", 12.0)
        weather_code = curr.get("weather_code", 1)
        
        if daily_rain <= 0:
            daily_sum = w_res.get("daily", {}).get("precipitation_sum", [0.0])
            daily_rain = sum(daily_sum) / len(daily_sum) if daily_sum else 1.5
            
        estimated_monthly_rainfall = round(daily_rain * 30 + 40, 1)
        if estimated_monthly_rainfall < 30:
            estimated_monthly_rainfall = 55.0
            
        # Map weather code to condition
        weather_conditions = {
            0: ('Clear Sky', 'sun'),
            1: ('Mainly Clear', 'sun'),
            2: ('Partly Cloudy', 'cloud-sun'),
            3: ('Overcast', 'cloud'),
            45: ('Foggy', 'cloud-fog'),
            51: ('Light Drizzle', 'cloud-drizzle'),
            61: ('Slight Rain', 'cloud-rain'),
            63: ('Moderate Rain', 'cloud-rain'),
            65: ('Heavy Rain', 'cloud-rain-heavy'),
            80: ('Rain Showers', 'cloud-rain'),
            95: ('Thunderstorm', 'cloud-lightning')
        }
        condition, icon = weather_conditions.get(weather_code, ('Mainly Clear', 'sun'))
        location_display = f"{city_name}, {state_name}" if state_name else city_name
        
        return jsonify({
            'success': True,
            'city': city_name,
            'state': state_name,
            'location_display': location_display,
            'country': country,
            'latitude': lat,
            'longitude': lon,
            'temperature': round(temp, 1),
            'humidity': round(humidity, 1),
            'rainfall': round(estimated_monthly_rainfall, 1),
            'wind_speed': wind_speed,
            'condition': condition,
            'icon': icon
        })
        
    except Exception as e:
        logging.error(f"Weather fetch error: {e}")
        return jsonify({
            'success': False,
            'message': 'Unable to connect to live meteorological service. Showing simulated data.',
            'city': city_name or 'My Farm Location',
            'state': state_name or '',
            'location_display': location_display if 'location_display' in locals() else (city_name or 'Local Station'),
            'country': country,
            'temperature': 27.1,
            'humidity': 65.0,
            'rainfall': 43.0,
            'wind_speed': 18.4,
            'condition': 'Mainly Clear',
            'icon': 'sun'
        })


