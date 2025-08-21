import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        
    def create_training_features(self, data_dict):
        """Convert collected data dictionary to feature vector"""
        features = {}
        
        # Weather features
        if 'weather' in data_dict:
            weather = data_dict['weather']
            features.update({
                'temperature': weather['temperature'],
                'humidity': weather['humidity'],
                'pressure': weather['pressure'],
                'visibility': weather['visibility'],
                'wind_speed': weather['wind_speed'],
                'is_raining': weather['is_raining'],
                'is_snowing': weather['is_snowing'],
                'rain_intensity': weather['rain_intensity'],
                'temp_trend': weather.get('temp_trend', 0),
                'rain_forecast_6h': int(weather.get('rain_forecast_6h', False))
            })
        
        # Contextual features
        if 'contextual' in data_dict:
            contextual = data_dict['contextual']
            features.update({
                'hour': contextual['hour'],
                'day_of_week': contextual['day_of_week'],
                'is_weekend': contextual['is_weekend'],
                'is_rush_hour': contextual['is_rush_hour'],
                'is_night': contextual['is_night'],
                'month': contextual['month'],
                'is_holiday': contextual['is_holiday'],
                'is_school_time': contextual['is_school_time']
            })
        
        # Traffic features (from historical data or current conditions)
        if 'traffic' in data_dict and data_dict['traffic']:
            traffic = data_dict['traffic'][0]  # Take first route
            features.update({
                'distance_km': traffic['distance_km'],
                'duration_normal_min': traffic['duration_normal_min'],
                'historical_traffic_ratio': traffic.get('traffic_ratio', 1.0)
            })
        
        # Incident features
        if 'incidents' in data_dict:
            incidents = data_dict['incidents']
            features.update({
                'num_accidents': len([i for i in incidents if i['type'] == 'accident']),
                'num_construction': len([i for i in incidents if i['type'] == 'construction']),
                'major_incident_nearby': int(any([i['severity'] == 'major' for i in incidents]))
            })
        
        # Time-based features
        features.update({
            'sin_hour': np.sin(2 * np.pi * features.get('hour', 0) / 24),
            'cos_hour': np.cos(2 * np.pi * features.get('hour', 0) / 24),
            'sin_day': np.sin(2 * np.pi * features.get('day_of_week', 0) / 7),
            'cos_day': np.cos(2 * np.pi * features.get('day_of_week', 0) / 7),
            'sin_month': np.sin(2 * np.pi * features.get('month', 1) / 12),
            'cos_month': np.cos(2 * np.pi * features.get('month', 1) / 12)
        })
        
        return features
    
    def generate_synthetic_training_data(self, n_samples=10000):
        """Generate synthetic training data for initial model training"""
        np.random.seed(42)
        
        data = []
        for i in range(n_samples):
            # Random time
            hour = np.random.randint(0, 24)
            day_of_week = np.random.randint(0, 7)
            month = np.random.randint(1, 13)
            
            # Weather conditions
            temperature = np.random.normal(25, 8)  # Celsius
            humidity = np.random.uniform(40, 90)
            is_raining = np.random.choice([0, 1], p=[0.8, 0.2])
            rain_intensity = np.random.exponential(2) if is_raining else 0
            visibility = np.random.uniform(5, 10) if is_raining else 10
            wind_speed = np.random.exponential(3)
            
            # Contextual features
            is_weekend = 1 if day_of_week >= 5 else 0
            is_rush_hour = 1 if (7 <= hour <= 10) or (17 <= hour <= 20) else 0
            is_night = 1 if (22 <= hour or hour <= 6) else 0
            is_holiday = np.random.choice([0, 1], p=[0.95, 0.05])
            is_school_time = 1 if (not is_weekend and 7 <= hour <= 17 and not is_holiday) else 0
            
            # Route features
            distance_km = np.random.uniform(2, 25)
            base_duration = distance_km * np.random.uniform(2, 4)  # 2-4 min per km base
            
            # Incidents
            num_accidents = np.random.poisson(0.1)
            num_construction = np.random.poisson(0.05)
            major_incident_nearby = 1 if (num_accidents > 0 and np.random.random() < 0.3) else 0
            
            # Calculate traffic multiplier based on conditions
            traffic_multiplier = 1.0
            
            # Time-based effects
            if is_rush_hour:
                traffic_multiplier *= np.random.uniform(1.5, 2.5)
            elif is_night:
                traffic_multiplier *= np.random.uniform(0.7, 0.9)
            
            # Weather effects
            if is_raining:
                traffic_multiplier *= np.random.uniform(1.2, 1.8)
                if rain_intensity > 5:
                    traffic_multiplier *= np.random.uniform(1.3, 2.0)
            
            # Weekend effects
            if is_weekend and not is_rush_hour:
                traffic_multiplier *= np.random.uniform(0.8, 1.1)
            
            # Holiday effects
            if is_holiday:
                traffic_multiplier *= np.random.uniform(0.6, 0.9)
            
            # Incident effects
            if major_incident_nearby:
                traffic_multiplier *= np.random.uniform(1.5, 2.5)
            elif num_accidents > 0:
                traffic_multiplier *= np.random.uniform(1.2, 1.6)
            if num_construction > 0:
                traffic_multiplier *= np.random.uniform(1.1, 1.4)
            
            # Add noise
            traffic_multiplier *= np.random.uniform(0.9, 1.1)
            
            # Calculate final duration
            duration_with_traffic = base_duration * traffic_multiplier
            
            # Create feature vector
            sample = {
                'hour': hour,
                'day_of_week': day_of_week,
                'month': month,
                'temperature': temperature,
                'humidity': humidity,
                'pressure': np.random.normal(1013, 10),
                'visibility': visibility,
                'wind_speed': wind_speed,
                'is_raining': is_raining,
                'is_snowing': 0,  # Rare in most Indian cities
                'rain_intensity': rain_intensity,
                'temp_trend': np.random.normal(0, 1),
                'rain_forecast_6h': int(is_raining or np.random.random() < 0.1),
                'is_weekend': is_weekend,
                'is_rush_hour': is_rush_hour,
                'is_night': is_night,
                'is_holiday': is_holiday,
                'is_school_time': is_school_time,
                'distance_km': distance_km,
                'duration_normal_min': base_duration,
                'historical_traffic_ratio': traffic_multiplier,
                'num_accidents': num_accidents,
                'num_construction': num_construction,
                'major_incident_nearby': major_incident_nearby,
                'sin_hour': np.sin(2 * np.pi * hour / 24),
                'cos_hour': np.cos(2 * np.pi * hour / 24),
                'sin_day': np.sin(2 * np.pi * day_of_week / 7),
                'cos_day': np.cos(2 * np.pi * day_of_week / 7),
                'sin_month': np.sin(2 * np.pi * month / 12),
                'cos_month': np.cos(2 * np.pi * month / 12),
                # Target variables
                'traffic_multiplier': traffic_multiplier,
                'duration_with_traffic': duration_with_traffic,
                'delay_minutes': duration_with_traffic - base_duration
            }
            
            data.append(sample)
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df, target_column='traffic_multiplier', fit_scalers=True):
        """Prepare features for training"""
        # Define feature columns
        feature_columns = [
            'hour', 'day_of_week', 'month',
            'temperature', 'humidity', 'pressure', 'visibility', 'wind_speed',
            'is_raining', 'is_snowing', 'rain_intensity', 'temp_trend', 'rain_forecast_6h',
            'is_weekend', 'is_rush_hour', 'is_night', 'is_holiday', 'is_school_time',
            'distance_km', 'duration_normal_min', 'historical_traffic_ratio',
            'num_accidents', 'num_construction', 'major_incident_nearby',
            'sin_hour', 'cos_hour', 'sin_day', 'cos_day', 'sin_month', 'cos_month'
        ]
        
        # Filter available columns
        available_columns = [col for col in feature_columns if col in df.columns]
        self.feature_columns = available_columns
        
        X = df[available_columns].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Scale numerical features
        numerical_features = [
            'temperature', 'humidity', 'pressure', 'visibility', 'wind_speed',
            'rain_intensity', 'temp_trend', 'distance_km', 'duration_normal_min'
        ]
        
        numerical_features = [col for col in numerical_features if col in X.columns]
        
        if fit_scalers:
            self.scalers['numerical'] = StandardScaler()
            X[numerical_features] = self.scalers['numerical'].fit_transform(X[numerical_features])
        elif 'numerical' in self.scalers:
            X[numerical_features] = self.scalers['numerical'].transform(X[numerical_features])
        
        if target_column in df.columns:
            y = df[target_column].values
            return X, y
        
        return X
    
    def split_data(self, X, y, test_size=0.2):
        """Split data into train/test sets"""
        return train_test_split(X, y, test_size=test_size, random_state=42, stratify=None)
    
    def save_preprocessors(self, filepath_base):
        """Save scalers and encoders"""
        joblib.dump(self.scalers, f"{filepath_base}_scalers.pkl")
        joblib.dump(self.encoders, f"{filepath_base}_encoders.pkl")
        joblib.dump(self.feature_columns, f"{filepath_base}_features.pkl")
    
    def load_preprocessors(self, filepath_base):
        """Load scalers and encoders"""
        self.scalers = joblib.load(f"{filepath_base}_scalers.pkl")
        self.encoders = joblib.load(f"{filepath_base}_encoders.pkl")
        self.feature_columns = joblib.load(f"{filepath_base}_features.pkl")
    
    def preprocess_single_sample(self, data_dict):
        """Preprocess a single sample for prediction"""
        features = self.create_training_features(data_dict)
        
        # Create dataframe with single row
        df = pd.DataFrame([features])
        
        # Add missing columns with default values
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        
        # Prepare features (without fitting scalers)
        X = self.prepare_features(df, target_column=None, fit_scalers=False)
        
        return X

# Example usage
if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    
    # Generate synthetic training data
    print("Generating synthetic training data...")
    df = preprocessor.generate_synthetic_training_data(n_samples=5000)
    
    # Prepare features
    print("Preparing features...")
    X, y = preprocessor.prepare_features(df, target_column='traffic_multiplier')
    
    # Split data
    X_train, X_test, y_train, y_test = preprocessor.split_data(X, y)
    
    print(f"Training set shape: {X_train.shape}")
    print(f"Test set shape: {X_test.shape}")
    print(f"Feature columns: {len(preprocessor.feature_columns)}")
    
    # Save preprocessors
    preprocessor.save_preprocessors("models/trained_models/preprocessor")
    print("Preprocessors saved!")