import React, { useState, useEffect } from 'react';
import './App.css';
import Map from './components/Map';
import ControlPanel from './components/ControlPanel';
import RouteDisplay from './components/RouteDisplay';
import { optimizeRoute, getTrafficStatus } from './services/api';
import { AlertCircle, CheckCircle, Clock, Navigation } from 'lucide-react';

// List of Bengaluru hospitals (example coordinates)
const hospitals = [
  { name: 'Manipal Hospital', location: [12.9750, 77.6050] },
  { name: 'Apollo Hospital', location: [12.9720, 77.5930] },
  { name: 'Fortis Hospital', location: [12.9580, 77.6440] },
  { name: 'Sakra World Hospital', location: [12.9500, 77.6330] }
];

// Haversine formula to calculate distance between two points
function getDistance(coord1, coord2) {
  const toRad = (x) => (x * Math.PI) / 180;
  const R = 6371; // Earth radius km
  const dLat = toRad(coord2[0] - coord1[0]);
  const dLon = toRad(coord2[1] - coord1[1]);
  const a =
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(toRad(coord1[0])) * Math.cos(toRad(coord2[0])) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

function App() {
  const [emergencyData, setEmergencyData] = useState({
    emergency_type: 'cardiac',
    priority: 'high',
    patient_count: 1,
    ambulance_location: [12.9716, 77.5946], // Bengaluru city center
    emergency_location: [12.9750, 77.6100],
    hospital_location: hospitals[0].location,
    vehicle_type: 'als',
    crew_size: 2,
    weather: 'clear',
    traffic_factor: 1.0
  });

  const [routeResult, setRouteResult] = useState(null);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [systemStatus, setSystemStatus] = useState('ready');
  const [notifications, setNotifications] = useState([]);

  // Choose nearest hospital dynamically
  useEffect(() => {
    const nearest = hospitals.reduce((prev, curr) => {
      return getDistance(emergencyData.emergency_location, curr.location) <
             getDistance(emergencyData.emergency_location, prev.location)
             ? curr : prev;
    }, hospitals[0]);
    setEmergencyData(prev => ({ ...prev, hospital_location: nearest.location }));
  }, [emergencyData.emergency_location]);

  useEffect(() => {
    addNotification('System initialized and ready for emergency dispatch', 'success');
    
    const trafficInterval = setInterval(async () => {
      try {
        const status = await getTrafficStatus(
          emergencyData.emergency_location[0],
          emergencyData.emergency_location[1]
        );
        setEmergencyData(prev => ({ ...prev, traffic_factor: status.traffic_factor }));
      } catch (error) {
        console.error('Failed to update traffic:', error);
      }
    }, 30000);

    return () => clearInterval(trafficInterval);
  }, [emergencyData.emergency_location]);

  const addNotification = (message, type = 'info') => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type, timestamp: new Date() }]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== id)), 5000);
  };

  const handleOptimizeRoute = async () => {
    setIsOptimizing(true);
    setSystemStatus('optimizing');
    addNotification('🚨 Emergency route optimization initiated', 'warning');
    
    try {
      const result = await optimizeRoute(emergencyData);
      setRouteResult(result);
      setSystemStatus('active');
      addNotification(`Route optimized! ${result.improvement_percent.toFixed(1)}% improvement`, 'success');
    } catch {
      addNotification('Route optimization failed. Using fallback routing.', 'error');
      setSystemStatus('error');
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleLocationUpdate = (locationType, coordinates) => {
    setEmergencyData(prev => ({ ...prev, [locationType]: coordinates }));
    if (routeResult) setRouteResult(null);
  };

  const getStatusIcon = () => {
    switch (systemStatus) {
      case 'ready': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'optimizing': return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />;
      case 'active': return <Navigation className="w-5 h-5 text-red-500" />;
      case 'error': return <AlertCircle className="w-5 h-5 text-red-600" />;
      default: return <CheckCircle className="w-5 h-5 text-green-500" />;
    }
  };

  const getStatusMessage = () => {
    switch (systemStatus) {
      case 'ready': return 'System ready for emergency dispatch';
      case 'optimizing': return 'Optimizing emergency route using AI...';
      case 'active': return 'ACTIVE EMERGENCY DISPATCH - Route optimized';
      case 'error': return 'System error - Using fallback mode';
      default: return 'System status unknown';
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">🚨 Emergency Route Optimizer - Bengaluru</h1>
          <div className="status-indicator">
            {getStatusIcon()} <span className={`status-text ${systemStatus}`}>{getStatusMessage()}</span>
          </div>
        </div>
      </header>

      <div className="app-body">
        <div className="control-section">
          <ControlPanel
            emergencyData={emergencyData}
            setEmergencyData={setEmergencyData}
            onOptimizeRoute={handleOptimizeRoute}
            isOptimizing={isOptimizing}
            systemStatus={systemStatus}
          />
          {routeResult && <RouteDisplay routeResult={routeResult} emergencyData={emergencyData} />}
        </div>

        <div className="map-section">
          <Map
            emergencyData={emergencyData}
            routeResult={routeResult}
            onLocationUpdate={handleLocationUpdate}
            isOptimizing={isOptimizing}
          />
        </div>
      </div>

      <div className="notifications">
        {notifications.map(n => (
          <div key={n.id} className={`notification ${n.type}`}>
            <div className="notification-content">
              <span>{n.message}</span>
              <small>{n.timestamp.toLocaleTimeString()}</small>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
