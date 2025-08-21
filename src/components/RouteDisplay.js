import React from 'react';

const RouteDisplay = ({ routeResult, emergencyData }) => {
  if (!routeResult) return null;
  return (
    <div style={{
      margin: '1rem 0', padding: '1rem', borderRadius: 8,
      background: 'rgba(255,255,255,0.9)', boxShadow: '0 2px 10px rgba(0,0,0,0.08)'
    }}>
      <h3 style={{ marginTop: 0 }}>📊 Route Summary</h3>
      <p><strong>Estimated Distance:</strong> {routeResult.distance.toFixed(2)} km</p>
      <p><strong>Estimated Time:</strong> {Math.round(routeResult.eta_minutes)} min</p>
      <p><strong>Improvement:</strong> {routeResult.improvement_percent.toFixed(1)}%</p>
      <p><strong>Traffic Factor:</strong> {emergencyData.traffic_factor.toFixed(2)}</p>
    </div>
  );
};

export default RouteDisplay;
