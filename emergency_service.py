import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.traffic_predictor import EmergencyTrafficPredictor
from models.route_optimizer import RouteOptimizer
from data.data_collector import DataCollector
from data.data_preprocessor import DataPreprocessor
from utils.map_utils import MapUtils
from utils.distance_calculator import DistanceCalculator
import json
import time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class EmergencyResponseService:
    """Main service class coordinating all emergency response optimization"""
    
    def __init__(self):
        self.data_collector = DataCollector()
        self.preprocessor = DataPreprocessor()
        self.traffic_predictor = EmergencyTrafficPredictor()
        self.route_optimizer = RouteOptimizer(self.traffic_predictor)
        self.map_utils = MapUtils()
        self.distance_calc = DistanceCalculator()
        
        # Initialize models and data
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize the emergency response system"""
        print("Initializing Emergency Response System...")
        
        try:
            # Load trained models
            self.traffic_predictor.load_models("models/trained_models/traffic_model")
            self.preprocessor.load_preprocessors("models/trained_models/preprocessor")
            print("✓ ML models loaded successfully")
        except:
            print("⚠ Training new models (first run)...")
            self._train_initial_models()
        
        # Initialize road network
        from config import Config
        self.route_optimizer.initialize_road_network(Config.CITY_BOUNDS)
        print("✓ Road network initialized")
        
        # Load hospital data
        self._load_hospital_database()
        print("✓ Hospital database loaded")
        
        print("🚨 Emergency Response System Ready!")
    
    def _train_initial_models(self):
        """Train initial models with synthetic data"""
        print("Generating synthetic training data...")
        df = self.preprocessor.generate_synthetic_training_data(n_samples=10000)
        
        print("Preparing features...")
        X, y = self.preprocessor.prepare_features(df, target_column='traffic_multiplier')
        X_train, X_test, y_train, y_test = self.preprocessor.split_data(X, y)
        
        print("Training models...")
        self.traffic_predictor.train_models(X_train, y_train, X_test, y_test)
        
        # Save models
        self.traffic_predictor.save_models("models/trained_models/traffic_model")
        self.preprocessor.save_preprocessors("models/trained_models/preprocessor")
        
        print("✓ Models trained and saved")
    
    def _load_hospital_database(self):
        """Load hospital database"""
        # Sample hospital data for Bengaluru
        hospitals = [
            {
                'id': 'H001', 'name': 'Manipal Hospital Whitefield',
                'lat': 12.9698, 'lon': 77.7500,
                'capacity': 200, 'specialties': ['cardiology', 'neurology', 'trauma'],
                'emergency_services': True, 'trauma_center': True, 'current_wait_time': 20
            },
            {
                'id': 'H002', 'name': 'Apollo Hospital Bannerghatta',
                'lat': 12.9056, 'lon': 77.5936,
                'capacity': 300, 'specialties': ['cardiac surgery', 'oncology', 'neurosurgery'],
                'emergency_services': True, 'trauma_center': True, 'current_wait_time': 15
            },
            {
                'id': 'H003', 'name': 'Fortis Hospital Cunningham Road',
                'lat': 12.9926, 'lon': 77.5985,
                'capacity': 150, 'specialties': ['emergency medicine', 'pediatrics'],
                'emergency_services': True, 'trauma_center': False, 'current_wait_time': 30
            },
            {
                'id': 'H004', 'name': 'Narayana Health City',
                'lat': 12.8539, 'lon': 77.6648,
                'capacity': 500, 'specialties': ['cardiac surgery', 'neurosurgery', 'trauma', 'pediatrics'],
                'emergency_services': True, 'trauma_center': True, 'current_wait_time': 10
            },
            {
                'id': 'H005', 'name': 'St. Johns Medical College Hospital',
                'lat': 12.9279, 'lon': 77.6271,
                'capacity': 250, 'specialties': ['general medicine', 'surgery', 'pediatrics'],
                'emergency_services': True, 'trauma_center': False, 'current_wait_time': 25
            }
        ]
        
        self.route_optimizer.load_hospital_data(hospitals)
    
    def handle_emergency_call(self, emergency_data):
        """Handle new emergency call and provide optimal response"""
        try:
            print(f"\n🚨 Emergency Call Received: {emergency_data.get('call_id', 'Unknown')}")
            
            # Extract emergency information
            emergency_location = (emergency_data['latitude'], emergency_data['longitude'])
            patient_condition = emergency_data.get('condition', 'general')
            priority = emergency_data.get('priority', 'high')
            
            # Collect real-time data
            print("📊 Collecting real-time data...")
            current_data = self.data_collector.collect_all_data(
                emergency_location, emergency_location  # Same location for context
            )
            
            # Preprocess data for ML model
            features = self.preprocessor.preprocess_single_sample(current_data)
            
            # Find optimal hospitals
            print("🏥 Finding optimal hospitals...")
            hospital_options = self.route_optimizer.find_optimal_hospital(
                emergency_location, patient_condition, current_data['contextual']
            )
            
            # Get route options for top 3 hospitals
            optimized_responses = []
            
            for i, hospital_option in enumerate(hospital_options[:3]):
                hospital = hospital_option['hospital']
                hospital_location = (hospital['lat'], hospital['lon'])
                
                # Get multiple route options
                route_options = self.route_optimizer.get_multiple_route_options(
                    emergency_location, hospital_location, current_data['contextual']
                )
                
                # Predict traffic for each route
                route_predictions = []
                for route in route_options:
                    # Calculate base duration
                    base_duration = self.distance_calc.calculate_travel_time(
                        emergency_location, hospital_location
                    )
                    
                    # Predict with ML model
                    prediction = self.traffic_predictor.predict_emergency_travel_time(
                        features, base_duration, vehicle_type='ambulance', 
                        emergency_priority=priority
                    )
                    
                    route_stats = self.route_optimizer.calculate_route_stats(
                        route['path'], current_data['contextual']
                    )
                    
                    route_prediction = {
                        'route': route,
                        'prediction': prediction,
                        'stats': route_stats,
                        'total_response_time': prediction['travel_time'] + hospital['current_wait_time']
                    }
                    
                    route_predictions.append(route_prediction)
                
                # Select best route for this hospital
                best_route = min(route_predictions, 
                               key=lambda x: x['total_response_time'])
                
                optimized_response = {
                    'hospital': hospital,
                    'best_route': best_route,
                    'rank': i + 1,
                    'suitability_score': hospital_option['suitability_score']
                }
                
                optimized_responses.append(optimized_response)
            
            # Generate final recommendation
            final_recommendation = self._generate_final_recommendation(
                optimized_responses, emergency_data, current_data
            )
            
            print("✅ Optimization complete!")
            return final_recommendation
            
        except Exception as e:
            print(f"❌ Error handling emergency call: {e}")
            return self._generate_fallback_response(emergency_data)
    
    def _generate_final_recommendation(self, optimized_responses, emergency_data, current_data):
        """Generate final recommendation with all details"""
        best_option = optimized_responses[0]
        
        recommendation = {
            'call_id': emergency_data.get('call_id'),
            'timestamp': datetime.now().isoformat(),
            'emergency_location': {
                'latitude': emergency_data['latitude'],
                'longitude': emergency_data['longitude'],
                'address': emergency_data.get('address', 'Unknown')
            },
            'patient_info': {
                'condition': emergency_data.get('condition', 'general'),
                'priority': emergency_data.get('priority', 'high'),
                'age': emergency_data.get('age'),
                'gender': emergency_data.get('gender')
            },
            'recommended_hospital': {
                'id': best_option['hospital']['id'],
                'name': best_option['hospital']['name'],
                'location': {
                    'latitude': best_option['hospital']['lat'],
                    'longitude': best_option['hospital']['lon']
                },
                'specialties': best_option['hospital']['specialties'],
                'current_wait_time': best_option['hospital']['current_wait_time']
            },
            'optimal_route': {
                'algorithm': best_option['best_route']['route']['algorithm'],
                'coordinates': best_option['best_route']['stats']['coordinates'],
                'distance_km': best_option['best_route']['stats']['total_distance_km'],
                'estimated_time': best_option['best_route']['prediction']['travel_time'],
                'time_saved': best_option['best_route']['prediction']['time_saved'],
                'confidence': best_option['best_route']['prediction'].get('confidence', 0.8)
            },
            'alternative_options': [
                {
                    'hospital_name': opt['hospital']['name'],
                    'travel_time': opt['best_route']['prediction']['travel_time'],
                    'total_time': opt['best_route']['total_response_time'],
                    'rank': opt['rank']
                }
                for opt in optimized_responses[1:3]
            ],
            'current_conditions': {
                'weather': current_data['weather']['weather_condition'],
                'traffic_level': 'Heavy' if current_data['contextual']['is_rush_hour'] else 'Moderate',
                'incidents': len(current_data['incidents']),
                'temperature': current_data['weather']['temperature']
            },
            'eta': (datetime.now() + timedelta(
                minutes=best_option['best_route']['prediction']['travel_time']
            )).isoformat(),
            'performance_metrics': {
                'processing_time_seconds': 2.5,  # Estimated
                'confidence_score': best_option['best_route']['prediction'].get('confidence', 0.8),
                'route_efficiency': best_option['best_route']['prediction']['time_saved'] / 
                                  best_option['best_route']['prediction']['normal_travel_time']
            }
        }
        
        return recommendation
    
    def _generate_fallback_response(self, emergency_data):
        """Generate fallback response if optimization fails"""
        return {
            'call_id': emergency_data.get('call_id'),
            'timestamp': datetime.now().isoformat(),
            'status': 'fallback',
            'message': 'Using standard emergency protocols',
            'emergency_location': {
                'latitude': emergency_data['latitude'],
                'longitude': emergency_data['longitude']
            },
            'recommendation': 'Dispatch to nearest available hospital using standard routes'
        }
    
    def update_ambulance_location(self, ambulance_id, latitude, longitude):
        """Update ambulance location for real-time tracking"""
        # This would update the ambulance tracking system
        location_update = {
            'ambulance_id': ambulance_id,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.now().isoformat(),
            'status': 'en_route'
        }
        
        # Check if rerouting is needed based on new location
        # Implementation would check active routes and optimize
        
        return location_update
    
    def get_system_status(self):
        """Get current system status and performance metrics"""
        return {
            'system_status': 'operational',
            'models_loaded': len(self.traffic_predictor.models),
            'best_model': self.traffic_predictor.best_model_name,
            'network_nodes': self.route_optimizer.road_network.number_of_nodes(),
            'network_edges': self.route_optimizer.road_network.number_of_edges(),
            'hospitals_loaded': len(self.route_optimizer.hospitals),
            'last_update': datetime.now().isoformat()
        }
    
    def simulate_emergency_response(self, num_emergencies=5):
        """Simulate multiple emergency responses for testing"""
        print("🧪 Running Emergency Response Simulation...")
        
        # Generate random emergency scenarios
        emergencies = self._generate_test_emergencies(num_emergencies)
        
        results = []
        total_processing_time = 0
        
        for i, emergency in enumerate(emergencies):
            print(f"\nSimulating Emergency {i+1}/{num_emergencies}")
            
            start_time = time.time()
            response = self.handle_emergency_call(emergency)
            processing_time = time.time() - start_time
            
            total_processing_time += processing_time
            
            results.append({
                'emergency': emergency,
                'response': response,
                'processing_time': processing_time
            })
        
        # Calculate simulation statistics
        avg_processing_time = total_processing_time / num_emergencies
        avg_travel_time = np.mean([
            r['response']['optimal_route']['estimated_time'] 
            for r in results if 'optimal_route' in r['response']
        ])
        
        simulation_summary = {
            'total_emergencies': num_emergencies,
            'avg_processing_time': avg_processing_time,
            'avg_travel_time': avg_travel_time,
            'success_rate': len([r for r in results if 'optimal_route' in r['response']]) / num_emergencies,
            'results': results
        }
        
        print(f"\n📊 Simulation Results:")
        print(f"Average processing time: {avg_processing_time:.2f} seconds")
        print(f"Average travel time: {avg_travel_time:.1f} minutes")
        print(f"Success rate: {simulation_summary['success_rate']*100:.1f}%")
        
        return simulation_summary
    
    def _generate_test_emergencies(self, num_emergencies):
        """Generate test emergency scenarios"""
        from config import Config
        bounds = Config.CITY_BOUNDS
        
        conditions = ['cardiac', 'stroke', 'trauma', 'respiratory', 'general']
        priorities = ['critical', 'high', 'medium']
        
        emergencies = []
        for i in range(num_emergencies):
            emergency = {
                'call_id': f'EMG_{datetime.now().strftime("%Y%m%d")}_{i+1:03d}',
                'latitude': np.random.uniform(bounds['south'], bounds['north']),
                'longitude': np.random.uniform(bounds['west'], bounds['east']),
                'condition': np.random.choice(conditions),
                'priority': np.random.choice(priorities),
                'age': np.random.randint(18, 85),
                'gender': np.random.choice(['M', 'F']),
                'address': f'Test Location {i+1}',
                'call_time': datetime.now().isoformat()
            }
            emergencies.append(emergency)
        
        return emergencies

# Utility classes
class EmergencyAnalytics:
    """Analytics and reporting for emergency response performance"""
    
    def __init__(self, emergency_service):
        self.service = emergency_service
        self.response_history = []
    
    def log_response(self, emergency_data, response_data, actual_outcome=None):
        """Log emergency response for analysis"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'emergency': emergency_data,
            'response': response_data,
            'actual_outcome': actual_outcome
        }
        self.response_history.append(log_entry)
    
    def generate_performance_report(self, time_period_days=30):
        """Generate performance report"""
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        
        recent_responses = [
            r for r in self.response_history 
            if datetime.fromisoformat(r['timestamp']) > cutoff_date
        ]
        
        if not recent_responses:
            return "No data available for the specified time period"
        
        # Calculate metrics
        avg_response_time = np.mean([
            r['response']['optimal_route']['estimated_time']
            for r in recent_responses if 'optimal_route' in r['response']
        ])
        
        condition_breakdown = {}
        for response in recent_responses:
            condition = response['emergency']['condition']
            condition_breakdown[condition] = condition_breakdown.get(condition, 0) + 1
        
        priority_breakdown = {}
        for response in recent_responses:
            priority = response['emergency']['priority']
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
        
        report = {
            'period_days': time_period_days,
            'total_emergencies': len(recent_responses),
            'avg_response_time_minutes': avg_response_time,
            'condition_breakdown': condition_breakdown,
            'priority_breakdown': priority_breakdown,
            'system_uptime': '99.5%',  # Would be calculated from actual logs
            'avg_processing_time': 2.3  # seconds
        }
        
        return report

# Example usage and testing
if __name__ == "__main__":
    # Initialize emergency service
    service = EmergencyResponseService()
    
    # Test emergency call
    test_emergency = {
        'call_id': 'EMG_20250821_001',
        'latitude': 12.9716,
        'longitude': 77.5946,
        'condition': 'cardiac',
        'priority': 'critical',
        'age': 65,
        'gender': 'M',
        'address': 'UB City Mall, Bengaluru',
        'call_time': datetime.now().isoformat()
    }
    
    print("Testing emergency response...")
    response = service.handle_emergency_call(test_emergency)
    
    print("\n📋 Emergency Response Summary:")
    print(f"Recommended Hospital: {response['recommended_hospital']['name']}")
    print(f"Estimated Travel Time: {response['optimal_route']['estimated_time']:.1f} minutes")
    print(f"Distance: {response['optimal_route']['distance_km']:.1f} km")
    print(f"Time Saved: {response['optimal_route']['time_saved']:.1f} minutes")
    print(f"ETA: {response['eta']}")
    
    # Run simulation
    print("\n" + "="*50)
    simulation_results = service.simulate_emergency_response(num_emergencies=3)
    
    # Initialize analytics
    analytics = EmergencyAnalytics(service)
    
    # Log simulated responses
    for result in simulation_results['results']:
        analytics.log_response(result['emergency'], result['response'])
    
    # Generate report
    report = analytics.generate_performance_report()
    print(f"\n📈 Performance Report:")
    print(f"Total emergencies: {report['total_emergencies']}")
    print(f"Average response time: {report['avg_response_time_minutes']:.1f} minutes")
    print(f"Condition breakdown: {report['condition_breakdown']}")
    print(f"Priority breakdown: {report['priority_breakdown']}")