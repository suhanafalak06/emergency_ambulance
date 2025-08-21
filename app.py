from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.emergency_service import EmergencyResponseService, EmergencyAnalytics
from datetime import datetime
import json
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize emergency service
emergency_service = EmergencyResponseService()
analytics = EmergencyAnalytics(emergency_service)

@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')

@app.route('/api/emergency', methods=['POST'])
def handle_emergency():
    """Handle new emergency call"""
    try:
        emergency_data = request.json
        
        # Validate required fields
        required_fields = ['latitude', 'longitude']
        if not all(field in emergency_data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        # Process emergency
        response = emergency_service.handle_emergency_call(emergency_data)
        
        # Log response for analytics
        analytics.log_response(emergency_data, response)
        
        return jsonify({
            'status': 'success',
            'data': response
        })
        
    except Exception as e:
        print(f"Error handling emergency: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/ambulance/location', methods=['POST'])
def update_ambulance_location():
    """Update ambulance location"""
    try:
        location_data = request.json
        
        required_fields = ['ambulance_id', 'latitude', 'longitude']
        if not all(field in location_data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        result = emergency_service.update_ambulance_location(
            location_data['ambulance_id'],
            location_data['latitude'],
            location_data['longitude']
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/predict/traffic', methods=['POST'])
def predict_traffic():
    """Predict traffic conditions for given route"""
    try:
        route_data = request.json
        
        origin = (route_data['origin']['lat'], route_data['origin']['lon'])
        destination = (route_data['destination']['lat'], route_data['destination']['lon'])
        
        # Collect current data
        current_data = emergency_service.data_collector.collect_all_data(origin, destination)
        
        # Preprocess for prediction
        features = emergency_service.preprocessor.preprocess_single_sample(current_data)
        
        # Make predictions for different time horizons
        predictions = emergency_service.traffic_predictor.predict_future_traffic(
            features, forecast_minutes=[15, 30, 45, 60]
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'current_conditions': current_data,
                'predictions': predictions
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/hospitals', methods=['GET'])
def get_hospitals():
    """Get all available hospitals"""
    try:
        hospitals = emergency_service.route_optimizer.hospitals
        
        # Add current status for each hospital
        for hospital in hospitals:
            # In real implementation, this would fetch real-time data
            hospital['current_status'] = {
                'beds_available': hospital['capacity'] - int(hospital['capacity'] * 0.7),
                'emergency_queue': hospital['current_wait_time'],
                'last_updated': datetime.now().isoformat()
            }
        
        return jsonify({
            'status': 'success',
            'data': hospitals
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/routes/optimize', methods=['POST'])
def optimize_route():
    """Get optimized route options"""
    try:
        route_request = request.json
        
        origin = (route_request['origin']['lat'], route_request['origin']['lon'])
        destination = (route_request['destination']['lat'], route_request['destination']['lon'])
        vehicle_type = route_request.get('vehicle_type', 'ambulance')
        
        # Collect current conditions
        current_data = emergency_service.data_collector.collect_all_data(origin, destination)
        
        # Get route options
        route_options = emergency_service.route_optimizer.get_multiple_route_options(
            origin, destination, current_data['contextual'], 
            num_routes=3, vehicle_type=vehicle_type
        )
        
        # Add detailed statistics for each route
        detailed_routes = []
        for route in route_options:
            stats = emergency_service.route_optimizer.calculate_route_stats(
                route['path'], current_data['contextual']
            )
            
            detailed_route = {
                'route_info': route,
                'statistics': stats,
                'current_conditions': current_data['contextual']
            }
            detailed_routes.append(detailed_route)
        
        return jsonify({
            'status': 'success',
            'data': detailed_routes
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/analytics/report', methods=['GET'])
def get_analytics_report():
    """Get system performance analytics"""
    try:
        days = request.args.get('days', 30, type=int)
        report = analytics.generate_performance_report(time_period_days=days)
        
        return jsonify({
            'status': 'success',
            'data': report
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/system/status', methods=['GET'])
def get_system_status():
    """Get current system status"""
    try:
        status = emergency_service.get_system_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/simulate', methods=['POST'])
def run_simulation():
    """Run emergency response simulation"""
    try:
        sim_params = request.json
        num_emergencies = sim_params.get('num_emergencies', 5)
        
        results = emergency_service.simulate_emergency_response(num_emergencies)
        
        return jsonify({
            'status': 'success',
            'data': results
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        'status': 'success',
        'message': 'Emergency Response API is operational',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Emergency Response API Server...")
    print("📍 System initialized for Bengaluru, Karnataka, India")
    print("🌐 Server will be available at: http://localhost:5000")
    print("📚 API Documentation:")
    print("   POST /api/emergency - Handle emergency call")
    print("   POST /api/ambulance/location - Update ambulance location") 
    print("   POST /api/predict/traffic - Predict traffic conditions")
    print("   GET  /api/hospitals - Get hospital information")
    print("   POST /api/routes/optimize - Get optimized routes")
    print("   GET  /api/analytics/report - Get performance analytics")
    print("   GET  /api/system/status - Get system status")
    print("   POST /api/simulate - Run simulation")
    print("   GET  /api/test - Test API connectivity")
    
    app.run(debug=True, host='0.0.0.0', port=5000)