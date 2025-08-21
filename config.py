import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///emergency_routes.db')
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    
    # Model Parameters
    TRAFFIC_PREDICTION_WINDOW = 30  # minutes
    MODEL_UPDATE_INTERVAL = 3600    # seconds (1 hour)
    ROUTE_CACHE_TTL = 300          # seconds (5 minutes)
    
    # Geographic Bounds (Configure for your city)
    # Example: Bengaluru, India
    CITY_BOUNDS = {
        'north': 13.1986,
        'south': 12.7340,
        'east': 77.8431,
        'west': 77.3910
    }
    
    # Emergency Response Parameters
    MAX_RESPONSE_TIME = 20          # minutes
    AMBULANCE_SPEED_FACTOR = 1.3    # 30% faster than normal traffic
    CRITICAL_THRESHOLD = 5          # minutes for critical cases
    
    # Model Training Parameters
    TRAIN_TEST_SPLIT = 0.2
    RANDOM_STATE = 42
    N_JOBS = -1
    
    # File Paths
    DATA_DIR = 'data'
    MODEL_DIR = 'models/trained_models'
    LOG_DIR = 'logs'