#!/usr/bin/env python3
"""
Emergency Response Route Optimization System
Main application entry point
"""

import sys
import os
import argparse
from datetime import datetime
import json

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from api.emergency_service import EmergencyResponseService, EmergencyAnalytics
from data.data_collector import DataCollector
from data.data_preprocessor import DataPreprocessor
from models.traffic_predictor import EmergencyTrafficPredictor
from config import Config

def setup_environment():
    """Set up required directories and check dependencies"""
    directories = [
        'data/raw',
        'models/trained_models',
        'logs',
        'frontend',
        'tests'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directory created/verified: {directory}")

def train_models():
    """Train ML models with synthetic data"""
    print("🤖 Training Machine Learning Models...")
    
    # Initialize components
    preprocessor = DataPreprocessor()
    predictor = EmergencyTrafficPredictor()
    
    # Generate training data
    print("📊 Generating synthetic training data...")
    df = preprocessor.generate_synthetic_training_data(n_samples=15000)
    print(f"Generated {len(df)} training samples")
    
    # Prepare features
    print("🔧 Preparing features...")
    X, y = preprocessor.prepare_features(df, target_column='traffic_multiplier')
    X_train, X_test, y_train, y_test = preprocessor.split_data(X, y)
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    print(f"Features: {X_train.shape[1]}")
    
    # Train models
    print("🚂 Training models...")
    metrics = predictor.train_models(X_train, y_train, X_test, y_test)
    
    # Evaluate performance
    predictor.evaluate_model_performance()
    
    # Save models
    print("💾 Saving trained models...")
    predictor.save_models("models/trained_models/traffic_model")
    preprocessor.save_preprocessors("models/trained_models/preprocessor")
    
    print("✅ Model training complete!")
    return metrics

def run_system_test():
    """Run comprehensive system test"""
    print("🧪 Running System Tests...")
    
    # Initialize service
    service = EmergencyResponseService()
    
    # Test emergency scenarios
    test_scenarios = [
        {
            'call_id': 'TEST_001',
            'latitude': 12.9716,
            'longitude': 77.5946,
            'condition': 'cardiac',
            'priority': 'critical',
            'age': 65,
            'address': 'UB City Mall, Bengaluru'
        },
        {
            'call_id': 'TEST_002',
            'latitude': 12.9344,
            'longitude': 77.6101,
            'condition': 'trauma',
            'priority': 'high',
            'age': 32,
            'address': 'Electronic City, Bengaluru'
        },
        {
            'call_id': 'TEST_003',
            'latitude': 12.9698,
            'longitude': 77.7500,
            'condition': 'stroke',
            'priority': 'critical',
            'age': 58,
            'address': 'Whitefield, Bengaluru'
        }
    ]
    
    test_results = []
    total_processing_time = 0
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\n🚨 Testing Scenario {i+1}: {scenario['condition']} emergency")
        
        start_time = datetime.now()
        response = service.handle_emergency_call(scenario)
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        total_processing_time += processing_time
        
        # Verify response structure
        test_result = {
            'scenario': scenario,
            'response': response,
            'processing_time': processing_time,
            'success': 'optimal_route' in response
        }
        
        test_results.append(test_result)
        
        if test_result['success']:
            print(f"✅ Success - Hospital: {response['recommended_hospital']['name']}")
            print(f"   Travel time: {response['optimal_route']['estimated_time']:.1f} min")
            print(f"   Processing time: {processing_time:.2f} seconds")
        else:
            print(f"❌ Failed - Using fallback response")
    
    # Summary
    success_rate = sum(1 for r in test_results if r['success']) / len(test_results)
    avg_processing_time = total_processing_time / len(test_results)
    
    print(f"\n📊 Test Summary:")
    print(f"Success rate: {success_rate*100:.1f}%")
    print(f"Average processing time: {avg_processing_time:.2f} seconds")
    
    return test_results

def run_performance_benchmark():
    """Run performance benchmark"""
    print("⏱️ Running Performance Benchmark...")
    
    service = EmergencyResponseService()
    
    # Test with different numbers of simultaneous requests
    benchmark_sizes = [1, 5, 10, 20]
    results = {}
    
    for size in benchmark_sizes:
        print(f"\nTesting with {size} simultaneous emergencies...")
        
        start_time = datetime.now()
        simulation_results = service.simulate_emergency_response(num_emergencies=size)
        end_time = datetime.now()
        
        total_time = (end_time - start_time).total_seconds()
        avg_time_per_request = total_time / size
        
        results[size] = {
            'total_time': total_time,
            'avg_time_per_request': avg_time_per_request,
            'success_rate': simulation_results['success_rate'],
            'avg_travel_time': simulation_results['avg_travel_time']
        }
        
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Avg per request: {avg_time_per_request:.2f}s")
        print(f"   Success rate: {simulation_results['success_rate']*100:.1f}%")
    
    print(f"\n📈 Benchmark Results:")
    for size, result in results.items():
        print(f"Size {size:2d}: {result['avg_time_per_request']:.2f}s/request, "
              f"{result['success_rate']*100:.1f}% success")
    
    return results

def create_sample_data():
    """Create sample data files for development"""
    print("📝 Creating sample data files...")
    
    # Sample traffic data
    import pandas as pd
    import numpy as np
    
    # Generate sample historical traffic data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='H')
    
    traffic_data = []
    for date in dates[:1000]:  # Limit to 1000 samples for demo
        sample = {
            'timestamp': date,
            'hour': date.hour,
            'day_of_week': date.weekday(),
            'month': date.month,
            'route_id': f"R{np.random.randint(1, 100)}",
            'origin_lat': 12.9716 + np.random.uniform(-0.1, 0.1),
            'origin_lon': 77.5946 + np.random.uniform(-0.1, 0.1),
            'dest_lat': 12.9716 + np.random.uniform(-0.1, 0.1),
            'dest_lon': 77.5946 + np.random.uniform(-0.1, 0.1),
            'distance_km': np.random.uniform(2, 25),
            'travel_time_min': np.random.uniform(10, 60),
            'traffic_speed_kmh': np.random.uniform(20, 80),
            'weather_condition': np.random.choice(['Clear', 'Rain', 'Cloudy', 'Storm']),
            'temperature': np.random.uniform(15, 35),
            'is_rush_hour': 1 if (7 <= date.hour <= 10) or (17 <= date.hour <= 20) else 0
        }
        traffic_data.append(sample)
    
    traffic_df = pd.DataFrame(traffic_data)
    traffic_df.to_csv('data/raw/traffic_data.csv', index=False)
    print("✓ Sample traffic data created")
    
    # Sample weather data
    weather_data = []
    for i in range(1000):
        weather_sample = {
            'timestamp': dates[i],
            'temperature': np.random.uniform(15, 35),
            'humidity': np.random.uniform(40, 90),
            'pressure': np.random.uniform(1000, 1020),
            'wind_speed': np.random.uniform(0, 15),
            'visibility': np.random.uniform(5, 10),
            'weather_main': np.random.choice(['Clear', 'Clouds', 'Rain', 'Thunderstorm']),
            'is_raining': np.random.choice([0, 1], p=[0.8, 0.2])
        }
        weather_data.append(weather_sample)
    
    weather_df = pd.DataFrame(weather_data)
    weather_df.to_csv('data/raw/weather_data.csv', index=False)
    print("✓ Sample weather data created")
    
    # Hospital locations
    hospitals = [
        {'id': 'H001', 'name': 'Manipal Hospital Whitefield', 'lat': 12.9698, 'lon': 77.7500, 'capacity': 200},
        {'id': 'H002', 'name': 'Apollo Hospital Bannerghatta', 'lat': 12.9056, 'lon': 77.5936, 'capacity': 300},
        {'id': 'H003', 'name': 'Fortis Hospital Cunningham Road', 'lat': 12.9926, 'lon': 77.5985, 'capacity': 150},
        {'id': 'H004', 'name': 'Narayana Health City', 'lat': 12.8539, 'lon': 77.6648, 'capacity': 500},
        {'id': 'H005', 'name': 'St. Johns Medical College', 'lat': 12.9279, 'lon': 77.6271, 'capacity': 250}
    ]
    
    with open('data/raw/hospital_locations.csv', 'w') as f:
        import csv
        writer = csv.DictWriter(f, fieldnames=['id', 'name', 'lat', 'lon', 'capacity'])
        writer.writeheader()
        writer.writerows(hospitals)
    
    print("✓ Hospital data created")
    print("✅ Sample data files created successfully!")

def interactive_demo():
    """Run interactive demo"""
    print("🎮 Interactive Emergency Response Demo")
    print("="*50)
    
    service = EmergencyResponseService()
    
    while True:
        print("\nOptions:")
        print("1. Handle Emergency Call")
        print("2. Get Hospital Information")
        print("3. Predict Traffic")
        print("4. Run Simulation")
        print("5. System Status")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            print("\n🚨 Emergency Call Handler")
            try:
                lat = float(input("Emergency Latitude: "))
                lon = float(input("Emergency Longitude: "))
                condition = input("Patient Condition (cardiac/stroke/trauma/general): ") or 'general'
                priority = input("Priority (critical/high/medium/low): ") or 'high'
                
                emergency = {
                    'call_id': f'DEMO_{datetime.now().strftime("%H%M%S")}',
                    'latitude': lat,
                    'longitude': lon,
                    'condition': condition,
                    'priority': priority,
                    'address': 'Demo Location'
                }
                
                response = service.handle_emergency_call(emergency)
                
                print("\n📋 Response:")
                print(f"Hospital: {response['recommended_hospital']['name']}")
                print(f"Travel Time: {response['optimal_route']['estimated_time']:.1f} minutes")
                print(f"Distance: {response['optimal_route']['distance_km']:.1f} km")
                print(f"ETA: {response['eta']}")
                
            except ValueError:
                print("❌ Invalid input. Please enter valid coordinates.")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == '2':
            print("\n🏥 Hospital Information")
            hospitals = service.route_optimizer.hospitals
            for i, hospital in enumerate(hospitals, 1):
                print(f"{i}. {hospital['name']}")
                print(f"   Location: {hospital['lat']:.4f}, {hospital['lon']:.4f}")
                print(f"   Capacity: {hospital['capacity']} beds")
                print(f"   Wait Time: {hospital['current_wait_time']} minutes")
                print(f"   Trauma Center: {'Yes' if hospital['trauma_center'] else 'No'}")
                print()
        
        elif choice == '3':
            print("\n🚦 Traffic Prediction")
            try:
                lat1 = float(input("Origin Latitude: "))
                lon1 = float(input("Origin Longitude: "))
                lat2 = float(input("Destination Latitude: "))
                lon2 = float(input("Destination Longitude: "))
                
                origin = (lat1, lon1)
                destination = (lat2, lon2)
                
                # Collect data and predict
                current_data = service.data_collector.collect_all_data(origin, destination)
                features = service.preprocessor.preprocess_single_sample(current_data)
                
                predictions = service.traffic_predictor.predict_future_traffic(features)
                
                print("\n📈 Traffic Predictions:")
                for time_ahead, pred in predictions.items():
                    print(f"{time_ahead}: {pred['prediction'][0]:.2f}x traffic multiplier")
                    print(f"   Uncertainty: ±{pred['uncertainty'][0]:.2f}")
                
            except ValueError:
                print("❌ Invalid coordinates")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == '4':
            print("\n🎲 Running Simulation")
            try:
                num_emergencies = int(input("Number of emergencies to simulate (1-10): ") or "3")
                if 1 <= num_emergencies <= 10:
                    results = service.simulate_emergency_response(num_emergencies)
                    print(f"\n✅ Simulation completed!")
                    print(f"Average response time: {results['avg_travel_time']:.1f} minutes")
                    print(f"Success rate: {results['success_rate']*100:.1f}%")
                else:
                    print("❌ Please enter a number between 1 and 10")
            except ValueError:
                print("❌ Invalid number")
            except Exception as e:
                print(f"❌ Error: {e}")
        
        elif choice == '5':
            print("\n📊 System Status")
            status = service.get_system_status()
            print(f"System Status: {status['system_status']}")
            print(f"Models Loaded: {status['models_loaded']}")
            print(f"Best Model: {status['best_model']}")
            print(f"Network Nodes: {status['network_nodes']}")
            print(f"Network Edges: {status['network_edges']}")
            print(f"Hospitals: {status['hospitals_loaded']}")
            print(f"Last Update: {status['last_update']}")
        
        elif choice == '6':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option. Please select 1-6.")

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description='Emergency Response Route Optimization System')
    parser.add_argument('--mode', choices=['train', 'test', 'demo', 'api', 'setup'], 
                       default='demo', help='Operation mode')
    parser.add_argument('--samples', type=int, default=10000, 
                       help='Number of training samples to generate')
    parser.add_argument('--port', type=int, default=5000, 
                       help='API server port')
    
    args = parser.parse_args()
    
    print("🚨 Emergency Response Route Optimization System")
    print("=" * 60)
    print(f"Mode: {args.mode}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Location: Bengaluru, Karnataka, India")
    print("=" * 60)
    
    try:
        if args.mode == 'setup':
            setup_environment()
            create_sample_data()
            
        elif args.mode == 'train':
            setup_environment()
            train_models()
            
        elif args.mode == 'test':
            setup_environment()
            run_system_test()
            
        elif args.mode == 'demo':
            setup_environment()
            # Train models if they don't exist
            if not os.path.exists('models/trained_models/traffic_model_random_forest.pkl'):
                print("🤖 No trained models found. Training now...")
                train_models()
            interactive_demo()
            
        elif args.mode == 'api':
            setup_environment()
            # Train models if they don't exist
            if not os.path.exists('models/trained_models/traffic_model_random_forest.pkl'):
                print("🤖 No trained models found. Training now...")
                train_models()
            
            print("🚀 Starting API Server...")
            from api.app import app
            app.run(debug=True, host='0.0.0.0', port=args.port)
        
        else:
            print("❌ Invalid mode selected")
            
    except KeyboardInterrupt:
        print("\n\n👋 Application terminated by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)