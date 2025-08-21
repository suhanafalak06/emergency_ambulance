import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from config import Config

class DataCollector:
    def __init__(self):
        self.config = Config()
        self.weather_api_key = self.config.OPENWEATHER_API_KEY
        self.maps_api_key = self.config.GOOGLE_MAPS_API_KEY
        
    def get_weather_data(self, lat, lon):
        """Fetch current and forecast weather data"""
        try:
            # Current weather
            current_url = f"http://api.openweathermap.org/data/2.5/weather"
            current_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.weather_api_key,
                'units': 'metric'
            }
            
            current_response = requests.get(current_url, params=current_params)
            current_data = current_response.json()
            
            # Forecast weather
            forecast_url = f"http://api.openweathermap.org/data/2.5/forecast"
            forecast_params = {
                'lat': lat,
                'lon': lon,
                'appid': self.weather_api_key,
                'units': 'metric',
                'cnt': 8  # 24 hours forecast (3-hour intervals)
            }
            
            forecast_response = requests.get(forecast_url, params=forecast_params)
            forecast_data = forecast_response.json()
            
            weather_features = self._extract_weather_features(current_data, forecast_data)
            return weather_features
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self._get_default_weather()
    
    def _extract_weather_features(self, current, forecast):
        """Extract relevant weather features for traffic prediction"""
        features = {
            'temperature': current['main']['temp'],
            'humidity': current['main']['humidity'],
            'pressure': current['main']['pressure'],
            'visibility': current.get('visibility', 10000) / 1000,  # km
            'wind_speed': current['wind']['speed'],
            'wind_direction': current['wind'].get('deg', 0),
            'weather_condition': current['weather'][0]['main'],
            'weather_description': current['weather'][0]['description'],
            'is_raining': 1 if 'rain' in current else 0,
            'is_snowing': 1 if 'snow' in current else 0,
            'rain_intensity': current.get('rain', {}).get('1h', 0),
            'timestamp': datetime.now().timestamp()
        }
        
        # Add forecast features
        if 'list' in forecast:
            forecast_temps = [item['main']['temp'] for item in forecast['list'][:4]]
            features['temp_trend'] = np.mean(np.diff(forecast_temps))
            features['max_temp_6h'] = max([item['main']['temp'] for item in forecast['list'][:2]])
            features['rain_forecast_6h'] = any(['rain' in item for item in forecast['list'][:2]])
            
        return features
    
    def get_traffic_data(self, origin, destination, departure_time=None):
        """Fetch real-time traffic data from Google Maps"""
        try:
            if departure_time is None:
                departure_time = int(time.time())
            
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{origin[0]},{origin[1]}",
                'destination': f"{destination[0]},{destination[1]}",
                'departure_time': departure_time,
                'traffic_model': 'best_guess',
                'alternatives': True,
                'key': self.maps_api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                routes_data = []
                for route in data['routes']:
                    route_info = self._extract_route_features(route)
                    routes_data.append(route_info)
                return routes_data
            else:
                print(f"Traffic API Error: {data['status']}")
                return []
                
        except Exception as e:
            print(f"Error fetching traffic data: {e}")
            return []
    
    def _extract_route_features(self, route):
        """Extract features from Google Maps route data"""
        leg = route['legs'][0]
        
        return {
            'distance_km': leg['distance']['value'] / 1000,
            'duration_traffic_min': leg['duration_in_traffic']['value'] / 60,
            'duration_normal_min': leg['duration']['value'] / 60,
            'traffic_delay_min': (leg['duration_in_traffic']['value'] - leg['duration']['value']) / 60,
            'traffic_ratio': leg['duration_in_traffic']['value'] / leg['duration']['value'],
            'polyline': route['overview_polyline']['points'],
            'summary': route['summary'],
            'warnings': route.get('warnings', []),
            'timestamp': datetime.now().timestamp()
        }
    
    def get_realtime_incidents(self, bounds):
        """Fetch traffic incidents, road closures, construction"""
        # This would integrate with local traffic management APIs
        # For now, return mock data structure
        incidents = []
        try:
            # Mock implementation - replace with actual traffic incident API
            mock_incidents = [
                {
                    'type': 'accident',
                    'severity': 'major',
                    'lat': 12.9716,
                    'lon': 77.5946,
                    'description': 'Vehicle breakdown on outer ring road',
                    'start_time': datetime.now().timestamp(),
                    'estimated_duration': 45  # minutes
                },
                {
                    'type': 'construction',
                    'severity': 'moderate',
                    'lat': 12.9344,
                    'lon': 77.6101,
                    'description': 'Road repair work',
                    'start_time': datetime.now().timestamp(),
                    'estimated_duration': 120  # minutes
                }
            ]
            incidents = mock_incidents
        except Exception as e:
            print(f"Error fetching incidents: {e}")
        
        return incidents
    
    def get_contextual_data(self):
        """Get contextual data like events, school schedules, etc."""
        now = datetime.now()
        
        contextual_features = {
            'hour': now.hour,
            'day_of_week': now.weekday(),
            'is_weekend': 1 if now.weekday() >= 5 else 0,
            'is_rush_hour': 1 if (7 <= now.hour <= 10) or (17 <= now.hour <= 20) else 0,
            'is_night': 1 if (22 <= now.hour or now.hour <= 6) else 0,
            'month': now.month,
            'is_holiday': self._check_holiday(now),
            'is_school_time': self._check_school_hours(now)
        }
        
        return contextual_features
    
    def _check_holiday(self, date):
        """Check if current date is a holiday"""
        # Implement holiday checking logic for your region
        # For now, return 0 (not holiday)
        return 0
    
    def _check_school_hours(self, date):
        """Check if it's school hours"""
        if date.weekday() >= 5:  # Weekend
            return 0
        if 7 <= date.hour <= 17:  # School hours
            return 1
        return 0
    
    def _get_default_weather(self):
        """Return default weather features when API fails"""
        return {
            'temperature': 25.0,
            'humidity': 60,
            'pressure': 1013,
            'visibility': 10,
            'wind_speed': 3.0,
            'wind_direction': 0,
            'weather_condition': 'Clear',
            'weather_description': 'clear sky',
            'is_raining': 0,
            'is_snowing': 0,
            'rain_intensity': 0,
            'timestamp': datetime.now().timestamp(),
            'temp_trend': 0,
            'max_temp_6h': 25.0,
            'rain_forecast_6h': False
        }
    
    def collect_all_data(self, origin, destination):
        """Collect all data needed for traffic prediction"""
        # Get weather data for origin
        weather_data = self.get_weather_data(origin[0], origin[1])
        
        # Get traffic data
        traffic_data = self.get_traffic_data(origin, destination)
        
        # Get contextual data
        contextual_data = self.get_contextual_data()
        
        # Get incidents
        bounds = {
            'north': max(origin[0], destination[0]) + 0.01,
            'south': min(origin[0], destination[0]) - 0.01,
            'east': max(origin[1], destination[1]) + 0.01,
            'west': min(origin[1], destination[1]) - 0.01
        }
        incidents = self.get_realtime_incidents(bounds)
        
        return {
            'weather': weather_data,
            'traffic': traffic_data,
            'contextual': contextual_data,
            'incidents': incidents,
            'timestamp': datetime.now().timestamp()
        }

# Example usage and data generation for training
if __name__ == "__main__":
    collector = DataCollector()
    
    # Example coordinates (Bengaluru)
    origin = (12.9716, 77.5946)  # UB City Mall
    destination = (12.9698, 77.7500)  # Whitefield
    
    data = collector.collect_all_data(origin, destination)
    print("Sample collected data:", json.dumps(data, indent=2, default=str))