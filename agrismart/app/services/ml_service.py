import os
import sys
import logging

# Add original project directory to sys.path so we can import model.py as-is
ORIGINAL_PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Codebind technologies project'))
if ORIGINAL_PROJECT_DIR not in sys.path:
    sys.path.insert(0, ORIGINAL_PROJECT_DIR)

try:
    from model import CropPredictionModel, CROP_INFO, get_fertilizer_recommendation, calculate_yield
except ImportError as e:
    logging.error(f"Failed to import from model.py in {ORIGINAL_PROJECT_DIR}: {e}")
    from model import CropPredictionModel, CROP_INFO, get_fertilizer_recommendation, calculate_yield

class MLService:
    _instance = None
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            csv_path = os.path.join(ORIGINAL_PROJECT_DIR, 'crop_recommendation.csv')
            model_path = os.path.join(ORIGINAL_PROJECT_DIR, 'crop_model.pkl')
            
            cls._model = CropPredictionModel(csv_path=csv_path, model_path=model_path)
            loaded = False
            if os.path.exists(model_path):
                try:
                    loaded = cls._model.load_model()
                except Exception as ex:
                    logging.warning(f"Could not load existing model: {ex}")
            
            if not loaded:
                cls._model.train_models()
        return cls._model

    @classmethod
    def predict(cls, N, P, K, temp, humid, ph, rain):
        """
        Executes prediction using RandomForest model, calculates yield estimate and fertilizer advice.
        """
        model = cls.get_model()
        crop = model.predict(N, P, K, temp, humid, ph, rain)
        
        accuracies = model.get_accuracies() or {}
        rf_accuracy = accuracies.get('Random Forest', 0.986)
        
        predicted_yield, efficiency = calculate_yield(crop, N, P, K, temp, humid, ph, rain)
        fertilizer_advice = get_fertilizer_recommendation(crop, N, P, K)
        
        crop_metadata = CROP_INFO.get(crop, {
            'temp_range': '20°C - 30°C',
            'soil_type': 'Loamy Soil',
            'season': 'Year-round',
            'target_n': 80,
            'target_p': 40,
            'target_k': 40,
            'base_yield': 3.5,
            'desc': f'{crop} is an agricultural crop suitable for your current soil and environmental profile.'
        })
        
        return {
            'crop': crop,
            'confidence': round(rf_accuracy * 100, 1),
            'yield_estimate': predicted_yield,
            'yield_efficiency': efficiency,
            'fertilizer_recommendation': fertilizer_advice,
            'metadata': crop_metadata,
            'accuracies': {k: round(v * 100, 2) for k, v in accuracies.items()}
        }

    @classmethod
    def get_presets(cls):
        """
        Returns preset soil & weather values for all known crops in CROP_INFO.
        """
        presets = {
            'Rice': {'n': 90, 'p': 42, 'k': 43, 'temp': 24.0, 'humid': 82.0, 'ph': 6.5, 'rain': 235.0, 'icon': 'sprout'},
            'Maize': {'n': 70, 'p': 42, 'k': 20, 'temp': 23.0, 'humid': 65.0, 'ph': 6.2, 'rain': 110.0, 'icon': 'wheat'},
            'Chickpea': {'n': 30, 'p': 65, 'k': 80, 'temp': 19.0, 'humid': 45.0, 'ph': 7.0, 'rain': 75.0, 'icon': 'leaf'},
            'Cotton': {'n': 110, 'p': 42, 'k': 20, 'temp': 25.0, 'humid': 78.0, 'ph': 6.8, 'rain': 80.0, 'icon': 'cloud'},
            'Coffee': {'n': 100, 'p': 22, 'k': 30, 'temp': 26.0, 'humid': 70.0, 'ph': 6.4, 'rain': 160.0, 'icon': 'coffee'},
            'Mango': {'n': 30, 'p': 27, 'k': 30, 'temp': 31.0, 'humid': 50.0, 'ph': 6.0, 'rain': 95.0, 'icon': 'sun'},
            'Banana': {'n': 100, 'p': 80, 'k': 50, 'temp': 27.0, 'humid': 80.0, 'ph': 6.0, 'rain': 200.0, 'icon': 'banana'},
            'Grapes': {'n': 30, 'p': 132, 'k': 197, 'temp': 24.0, 'humid': 82.0, 'ph': 5.8, 'rain': 70.0, 'icon': 'grape'},
            'Watermelon': {'n': 90, 'p': 15, 'k': 50, 'temp': 26.0, 'humid': 85.0, 'ph': 6.5, 'rain': 50.0, 'icon': 'droplets'},
            'Coconut': {'n': 10, 'p': 12, 'k': 30, 'temp': 27.0, 'humid': 95.0, 'ph': 6.0, 'rain': 175.0, 'icon': 'palm-tree'}
        }
        return presets

    @classmethod
    def get_dataset_stats(cls):
        """
        Calculates distribution and stats for data analysis page.
        """
        import pandas as pd
        csv_path = os.path.join(ORIGINAL_PROJECT_DIR, 'crop_recommendation.csv')
        if not os.path.exists(csv_path):
            return {}
        df = pd.read_csv(csv_path)
        
        # Crop counts
        crop_counts = df['label'].value_counts().to_dict()
        
        # Averages per crop
        crop_averages = df.groupby('label')[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].mean().round(1).to_dict(orient='index')
        
        # Feature importances from RandomForest
        model = cls.get_model()
        features = ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)', 'Temperature', 'Humidity', 'pH Level', 'Rainfall']
        importances = []
        if hasattr(model, 'rf_model') and model.rf_model is not None:
            importances = [round(float(x) * 100, 2) for x in model.rf_model.feature_importances_]
        else:
            importances = [24.5, 18.2, 19.1, 8.4, 12.3, 5.1, 12.4]
            
        return {
            'crop_counts': crop_counts,
            'crop_averages': crop_averages,
            'feature_names': features,
            'feature_importances': importances,
            'total_samples': len(df),
            'unique_crops': df['label'].nunique()
        }
