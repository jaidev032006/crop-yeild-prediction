import pandas as pd
import numpy as np
import os

def generate_crop_dataset():
    np.random.seed(42)
    
    crops = {
        'Rice': {
            'N': (80, 100), 'P': (35, 55), 'K': (35, 45),
            'temp': (20, 27), 'humid': (80, 90), 'ph': (5.5, 6.5), 'rain': (180, 250)
        },
        'Maize': {
            'N': (60, 80), 'P': (35, 50), 'K': (15, 25),
            'temp': (18, 27), 'humid': (55, 70), 'ph': (5.5, 7.0), 'rain': (60, 110)
        },
        'Chickpea': {
            'N': (20, 40), 'P': (55, 75), 'K': (75, 85),
            'temp': (17, 23), 'humid': (15, 20), 'ph': (6.0, 8.0), 'rain': (60, 95)
        },
        'Cotton': {
            'N': (100, 120), 'P': (35, 50), 'K': (15, 25),
            'temp': (22, 28), 'humid': (75, 85), 'ph': (6.0, 7.5), 'rain': (60, 90)
        },
        'Coffee': {
            'N': (90, 110), 'P': (15, 30), 'K': (25, 35),
            'temp': (22, 28), 'humid': (50, 60), 'ph': (6.0, 7.0), 'rain': (140, 190)
        },
        'Mango': {
            'N': (20, 40), 'P': (20, 35), 'K': (25, 35),
            'temp': (27, 35), 'humid': (45, 55), 'ph': (5.5, 6.5), 'rain': (90, 100)
        },
        'Banana': {
            'N': (80, 120), 'P': (70, 90), 'K': (45, 55),
            'temp': (25, 30), 'humid': (75, 85), 'ph': (5.5, 6.5), 'rain': (90, 110)
        },
        'Grapes': {
            'N': (20, 40), 'P': (120, 145), 'K': (190, 205),
            'temp': (20, 42), 'humid': (80, 85), 'ph': (5.5, 6.0), 'rain': (65, 75)
        },
        'Watermelon': {
            'N': (80, 100), 'P': (5, 25), 'K': (45, 55),
            'temp': (24, 27), 'humid': (80, 90), 'ph': (6.0, 7.0), 'rain': (40, 60)
        },
        'Coconut': {
            'N': (0, 20), 'P': (5, 20), 'K': (25, 35),
            'temp': (25, 30), 'humid': (90, 99), 'ph': (5.5, 6.5), 'rain': (140, 230)
        }
    }
    
    num_samples_per_crop = 150
    data_list = []
    
    for crop, ranges in crops.items():
        for _ in range(num_samples_per_crop):
            row = {
                'N': round(np.random.uniform(*ranges['N'])),
                'P': round(np.random.uniform(*ranges['P'])),
                'K': round(np.random.uniform(*ranges['K'])),
                'temperature': round(np.random.uniform(*ranges['temp']), 2),
                'humidity': round(np.random.uniform(*ranges['humid']), 2),
                'ph': round(np.random.uniform(*ranges['ph']), 2),
                'rainfall': round(np.random.uniform(*ranges['rain']), 2),
                'label': crop
            }
            data_list.append(row)
            
    df = pd.DataFrame(data_list)
    
    # Shuffle dataset
    df = df.sample(frac=1).reset_index(drop=True)
    
    csv_path = 'crop_recommendation.csv'
    df.to_csv(csv_path, index=False)
    print(f"Dataset generated successfully at {csv_path} with {len(df)} records.")

if __name__ == '__main__':
    generate_crop_dataset()
