import React from 'react';
import { Siren, Users, CloudRain, Clock, AlertTriangle } from 'lucide-react';

const ControlPanel = ({
  emergencyData,
  setEmergencyData,
  onOptimizeRoute,
  isOptimizing,
  systemStatus
}) => {
  const handleInputChange = (field, value) => {
    setEmergencyData(prev => ({ ...prev, [field]: value }));
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#e74c3c';
      case 'medium': return '#f39c12';
      case 'low': return '#27ae60';
      default: return '#95a5a6';
    }
  };

  const getWeatherEmoji = (weather) => {
    switch (weather) {
      case 'clear': return '☀️';
      case 'rain': return '🌧️';
      case 'snow': return '❄️';
      case 'fog': return '🌫️';
      case 'storm': return '⛈️';
      default: return '☀️';
    }
  };

  return (
    <div className="control-panel">
      <div className="panel-header">
        <h2><Siren className="inline w-6 h-6 mr-2" />Emergency Dispatch</h2>
        <div className="live-indicator">
          <div className="pulse-dot"></div>
          LIVE SYSTEM
        </div>
      </div>

      {/* Emergency Details */}
      <div className="form-section">
        <h3><AlertTriangle className="inline w-5 h-5 mr-2" />Emergency Details</h3>

        <div className="form-group">
          <label htmlFor="emergency-type">Emergency Type</label>
          <select
            id="emergency-type"
            value={emergencyData.emergency_type}
            onChange={(e) => handleInputChange('emergency_type', e.target.value)}
            className="form-control"
          >
            <option value="cardiac">💓 Cardiac Arrest</option>
            <option value="trauma">🩸 Major Trauma</option>
            <option value="stroke">🧠 Stroke</option>
            <option value="overdose">💊 Overdose</option>
            <option value="accident">🚗 Vehicle Accident</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="priority">Priority Level</label>
          <select
            id="priority"
            value={emergencyData.priority}
            onChange={(e) => handleInputChange('priority', e.target.value)}
            className="form-control"
            style={{ borderColor: getPriorityColor(emergencyData.priority) }}
          >
            <option value="high">🔴 Critical (Life threatening)</option>
            <option value="medium">🟡 Urgent (Serious but stable)</option>
            <option value="low">🟢 Non-urgent (Routine transport)</option>
          </select>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="patient-count">Patients</label>
            <input
              id="patient-count"
              type="number"
              value={emergencyData.patient_count}
              onChange={(e) => handleInputChange('patient_count', parseInt(e.target.value || '1', 10))}
              min="1"
              max="10"
              className="form-control"
            />
          </div>
          <div className="form-group">
            <label htmlFor="crew-size">Crew Size</label>
            <select
              id="crew-size"
              value={emergencyData.crew_size}
              onChange={(e) => handleInputChange('crew_size', parseInt(e.target.value, 10))}
              className="form-control"
            >
              <option value={2}>2 Personnel</option>
              <option value={3}>3 Personnel</option>
              <option value={4}>4 Personnel (Critical)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Vehicle */}
      <div className="form-section">
        <h3><Users className="inline w-5 h-5 mr-2" />Vehicle & Resources</h3>
        <div className="form-group">
          <label htmlFor="vehicle-type">Ambulance Type</label>
          <select
            id="vehicle-type"
            value={emergencyData.vehicle_type}
            onChange={(e) => handleInputChange('vehicle_type', e.target.value)}
            className="form-control"
          >
            <option value="als">🚑 ALS (Advanced Life Support)</option>
            <option value="bls">🚐 BLS (Basic Life Support)</option>
            <option value="critical">🏥 Critical Care Transport</option>
            <option value="helicopter">🚁 Air Ambulance</option>
          </select>
        </div>
      </div>

      {/* Environment */}
      <div className="form-section">
        <h3><CloudRain className="inline w-5 h-5 mr-2" />Environmental Conditions</h3>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="weather">Weather {getWeatherEmoji(emergencyData.weather)}</label>
            <select
              id="weather"
              value={emergencyData.weather}
              onChange={(e) => handleInputChange('weather', e.target.value)}
              className="form-control"
            >
              <option value="clear">☀️ Clear</option>
              <option value="rain">🌧️ Rain</option>
              <option value="snow">❄️ Snow</option>
              <option value="fog">🌫️ Fog</option>
              <option value="storm">⛈️ Storm</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="traffic-factor">Traffic Density</label>
            <select
              id="traffic-factor"
              value={emergencyData.traffic_factor}
              onChange={(e) => handleInputChange('traffic_factor', parseFloat(e.target.value))}
              className="form-control"
            >
              <option value={1.0}>🟢 Light Traffic</option>
              <option value={1.3}>🟡 Moderate Traffic</option>
              <option value={1.8}>🟠 Heavy Traffic</option>
              <option value={2.5}>🔴 Severe Congestion</option>
            </select>
          </div>
        </div>
      </div>

      {/* Button */}
      <div className="form-section">
        <button
          onClick={onOptimizeRoute}
          disabled={isOptimizing}
          className={`optimize-btn ${systemStatus === 'active' ? 'active' : ''}`}
        >
          {isOptimizing ? (
            <>
              <Clock className="inline w-5 h-5 mr-2 animate-spin" />
              OPTIMIZING ROUTE...
            </>
          ) : (
            <>🚨 OPTIMIZE EMERGENCY ROUTE</>
          )}
        </button>
      </div>

      {/* Tips */}
      <div className="instructions">
        <h4>📍 Quick Instructions</h4>
        <ul>
          <li>Click on map to set emergency location</li>
          <li>Configure emergency details above</li>
          <li>Click optimize for AI-powered routing</li>
          <li>Traffic updates every 30 seconds</li>
        </ul>
      </div>
    </div>
  );
};

export default ControlPanel;
