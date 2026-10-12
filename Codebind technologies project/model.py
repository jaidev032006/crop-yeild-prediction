import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score

# Crop Information Metadata
CROP_INFO = {
    'Rice': {
        'temp_range': '20°C - 27°C',
        'soil_type': 'Clayey/Loamy Soil',
        'season': 'Kharif (Monsoon)',
        'target_n': 90, 'target_p': 42, 'target_k': 43,
        'base_yield': 4.0, # tons per hectare
        'desc': 'Rice is a tropical crop that requires high rainfall, clayey/loamy soil, and standing water to grow successfully.'
    },
    'Maize': {
        'temp_range': '18°C - 27°C',
        'soil_type': 'Well-drained Fertile Loam',
        'season': 'Kharif / Spring',
        'target_n': 70, 'target_p': 42, 'target_k': 20,
        'base_yield': 4.8,
        'desc': 'Maize (Corn) is a versatile cereal crop requiring warm climates and well-drained loamy soils.'
    },
    'Chickpea': {
        'temp_range': '17°C - 23°C',
        'soil_type': 'Sandy Clay or Loamy Soil',
        'season': 'Rabi (Winter)',
        'target_n': 30, 'target_p': 65, 'target_k': 80,
        'base_yield': 1.8,
        'desc': 'Chickpea is a pulse crop that thrives in cool weather and requires moderate moisture and clay-loam soils.'
    },
    'Cotton': {
        'temp_range': '22°C - 28°C',
        'soil_type': 'Black Cotton Soil (Regur)',
        'season': 'Kharif',
        'target_n': 110, 'target_p': 42, 'target_k': 20,
        'base_yield': 2.2,
        'desc': 'Cotton is a major cash crop requiring high temperature, moderate rainfall, and deep clayey black soils.'
    },
    'Coffee': {
        'temp_range': '22°C - 28°C',
        'soil_type': 'Volcanic red earth or deep sandy loam',
        'season': 'Year-round / Monsoon',
        'target_n': 100, 'target_p': 22, 'target_k': 30,
        'base_yield': 1.2,
        'desc': 'Coffee requires a hot and humid climate with heavy rainfall, usually grown in hilly slopes under shade.'
    },
    'Mango': {
        'temp_range': '27°C - 35°C',
        'soil_type': 'Deep, well-drained alluvial/loamy soil',
        'season': 'Summer / Spring',
        'target_n': 30, 'target_p': 27, 'target_k': 30,
        'base_yield': 8.5,
        'desc': 'Mango is the king of fruits, thriving in tropical/subtropical climates with warm, dry periods for flowering.'
    },
    'Banana': {
        'temp_range': '25°C - 30°C',
        'soil_type': 'Rich, well-drained clay loam',
        'season': 'Year-round',
        'target_n': 100, 'target_p': 80, 'target_k': 50,
        'base_yield': 15.0,
        'desc': 'Banana is a moisture-loving plant requiring a warm tropical climate, fertile soil, and continuous irrigation.'
    },
    'Grapes': {
        'temp_range': '20°C - 42°C',
        'soil_type': 'Well-drained gravelly or sandy loam',
        'season': 'Spring / Summer',
        'target_n': 30, 'target_p': 132, 'target_k': 197,
        'base_yield': 12.0,
        'desc': 'Grapes require sunny, warm conditions for ripening and extremely well-drained soils, often grown on trellises.'
    },
    'Watermelon': {
        'temp_range': '24°C - 27°C',
        'soil_type': 'Sandy loam with good organic matter',
        'season': 'Zaid (Summer)',
        'target_n': 90, 'target_p': 15, 'target_k': 50,
        'base_yield': 25.0,
        'desc': 'Watermelons require hot, dry weather and sandy, fast-draining soils with deep root space.'
    },
    'Coconut': {
        'temp_range': '25°C - 30°C',
        'soil_type': 'Alluvial, sandy, or laterite soil',
        'season': 'Year-round',
        'target_n': 10, 'target_p': 12, 'target_k': 30,
        'base_yield': 5.5,
        'desc': 'Coconuts are coastal crops that need highly humid environments, warm temperatures, and sandy soils.'
    }
}

class CropPredictionModel:
    def __init__(self, csv_path='crop_recommendation.csv', model_path='crop_model.pkl'):
        self.csv_path = csv_path
        self.model_path = model_path
        self.rf_model = None
        self.accuracies = {}
        self.is_trained = False
        
    def train_models(self):
        """Trains RandomForest, DecisionTree, NaiveBayes and saves the best model (RF)."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Dataset file '{self.csv_path}' not found! Run dataset.py first.")
            
        # Load dataset
        df = pd.read_csv(self.csv_path)
        X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']].values
        y = df['label'].values
        
        # Train-Test Split (80% Train, 20% Test)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 1. Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        rf_acc = accuracy_score(y_test, rf.predict(X_test))
        self.accuracies['Random Forest'] = rf_acc
        self.rf_model = rf
        
        # 2. Decision Tree
        dt = DecisionTreeClassifier(random_state=42)
        dt.fit(X_train, y_train)
        dt_acc = accuracy_score(y_test, dt.predict(X_test))
        self.accuracies['Decision Tree'] = dt_acc
        
        # 3. Naive Bayes
        nb = GaussianNB()
        nb.fit(X_train, y_train)
        nb_acc = accuracy_score(y_test, nb.predict(X_test))
        self.accuracies['Naive Bayes'] = nb_acc
        
        # Save RandomForest model using pickle
        with open(self.model_path, 'wb') as f:
            pickle.dump((self.rf_model, self.accuracies), f)
            
        self.is_trained = True
        print("Models trained successfully!")
        for name, acc in self.accuracies.items():
            print(f"- {name} Accuracy: {acc*100:.2f}%")
            
    def load_model(self):
        """Loads the saved RF model and accuracies."""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.rf_model, self.accuracies = pickle.load(f)
            self.is_trained = True
            return True
        return False
        
    def predict(self, N, P, K, temp, humid, ph, rain):
        """Predicts the best crop based on given inputs."""
        if not self.is_trained:
            if not self.load_model():
                self.train_models()
                
        # Make prediction
        input_data = [[N, P, K, temp, humid, ph, rain]]
        crop = self.rf_model.predict(input_data)[0]
        return crop

    def get_accuracies(self):
        """Returns the dictionary of classifier accuracies."""
        if not self.is_trained:
            self.load_model()
        return self.accuracies

def get_fertilizer_recommendation(crop, N, P, K):
    """Compares actual inputs with optimal values for the predicted crop and suggests adjustments."""
    if crop not in CROP_INFO:
        return "No recommendation available for this crop."
        
    info = CROP_INFO[crop]
    opt_n = info['target_n']
    opt_p = info['target_p']
    opt_k = info['target_k']
    
    recs = []
    
    # Nitrogen adjustments
    n_diff = opt_n - N
    if n_diff > 10:
        recs.append(f"• **Nitrogen (N) is LOW** by {n_diff} mg/kg. Add a nitrogenous fertilizer like **Urea** (apply in splits) or organic compost.")
    elif n_diff < -15:
        recs.append(f"• **Nitrogen (N) is HIGH** by {abs(n_diff)} mg/kg. Avoid nitrogen fertilizers. Flush the soil with water or grow leafy cover crops to absorb excess nitrogen.")
    else:
        recs.append("• **Nitrogen (N) is OPTIMAL** for this crop.")
        
    # Phosphorus adjustments
    p_diff = opt_p - P
    if p_diff > 8:
        recs.append(f"• **Phosphorus (P) is LOW** by {p_diff} mg/kg. Apply **Single Superphosphate (SSP)** or Bone Meal near the root zone.")
    elif p_diff < -12:
        recs.append(f"• **Phosphorus (P) is HIGH** by {abs(p_diff)} mg/kg. Avoid phosphate fertilizers. High P can limit zinc and iron absorption.")
    else:
        recs.append("• **Phosphorus (P) is OPTIMAL** for this crop.")
        
    # Potassium adjustments
    k_diff = opt_k - K
    if k_diff > 8:
        recs.append(f"• **Potassium (K) is LOW** by {k_diff} mg/kg. Add **Muriate of Potash (MOP)** or Wood Ash to improve crop quality and disease resistance.")
    elif k_diff < -12:
        recs.append(f"• **Potassium (K) is HIGH** by {abs(k_diff)} mg/kg. Avoid potash fertilizers. Excessive K can lead to calcium deficiency.")
    else:
        recs.append("• **Potassium (K) is OPTIMAL** for this crop.")
        
    return "\n".join(recs)

def calculate_yield(crop, N, P, K, temp, humid, ph, rain):
    """
    Predicts expected crop yield in tons/hectare.
    Yield is calculated based on deviation of input parameters from the crop's ideal conditions.
    """
    if crop not in CROP_INFO:
        return 0.0, 0
        
    info = CROP_INFO[crop]
    base = info['base_yield']
    
    # Extract approximate target boundaries
    # Temperature target range (split by -)
    t_min, t_max = map(float, info['temp_range'].replace('°C', '').split('-'))
    # pH target range
    ph_min, ph_max = 5.5, 7.0 # generic optimal if not parsed
    if crop == 'Chickpea': ph_min, ph_max = 6.0, 8.0
    elif crop == 'Grapes': ph_min, ph_max = 5.5, 6.0
    elif crop == 'Cotton': ph_min, ph_max = 6.0, 7.5
    
    # Calculate penalty scores (0 to 1 scaling for deviation)
    def penalty(val, min_val, max_val, weight=1.0):
        if val < min_val:
            dev = (min_val - val) / min_val
            return min(0.35, dev * weight)
        elif val > max_val:
            dev = (val - max_val) / max_val
            return min(0.35, dev * weight)
        return 0.0

    # Soil NPK penalty relative to target values
    n_penalty = min(0.15, abs(info['target_n'] - N) / (info['target_n'] + 1) * 0.5)
    p_penalty = min(0.15, abs(info['target_p'] - P) / (info['target_p'] + 1) * 0.5)
    k_penalty = min(0.15, abs(info['target_k'] - K) / (info['target_k'] + 1) * 0.5)
    
    t_penalty = penalty(temp, t_min, t_max, weight=0.8)
    ph_penalty = penalty(ph, ph_min, ph_max, weight=1.2)
    
    total_penalty = n_penalty + p_penalty + k_penalty + t_penalty + ph_penalty
    efficiency = max(0.40, 1.0 - total_penalty)
    
    predicted_yield = base * efficiency
    return round(predicted_yield, 2), round(efficiency * 100, 1)

if __name__ == '__main__':
    # Train the models and output statistics
    model = CropPredictionModel()
    model.train_models()
